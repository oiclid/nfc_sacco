"""
Savings Module - Complete savings account management
====================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QGroupBox, QTextEdit, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime


class SavingsModule(QWidget):
    """Complete savings management module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.current_user = app.current_user
        self.current_member = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Savings Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.deposit_btn = QPushButton("➕ Deposit")
        self.deposit_btn.setEnabled(False)
        self.deposit_btn.clicked.connect(self.deposit)
        header_layout.addWidget(self.deposit_btn)
        
        self.withdraw_btn = QPushButton("➖ Withdraw")
        self.withdraw_btn.setEnabled(False)
        self.withdraw_btn.clicked.connect(self.withdraw)
        header_layout.addWidget(self.withdraw_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Member ID, Name, or Partial Name (use + or & for multiple)")
        self.search_input.setMinimumHeight(35)  # Taller for better usability
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setMinimumHeight(35)
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Member info
        self.member_info_label = QLabel("No member selected")
        self.member_info_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.member_info_label)
        
        # Accounts table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Account Number", "Type", "Balance", "Total Deposits",
            "Total Withdrawals", "Interest Earned"
        ])
        
        # Set row height for better readability
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setVisible(False)
        
        # Table settings
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        if self.current_member:
            self.search()
    
    def search(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Search", "Please enter a Member ID or Name")
            return
        
        # Check if searching by multiple terms (using + or &)
        search_terms = []
        if '+' in search_text or '&' in search_text:
            # Split by both + and &
            import re
            search_terms = [term.strip() for term in re.split('[+&]', search_text) if term.strip()]
        else:
            search_terms = [search_text]
        
        # Try to find member(s) matching the search
        member = None
        
        # First, try direct member ID match
        if len(search_terms) == 1:
            potential_id = search_terms[0].upper()
            member = self.db.get_member(potential_id)
        
        # If not found by ID, search by name
        if not member:
            # Build SQL query for name search
            query_parts = []
            params = []
            
            for term in search_terms:
                term_lower = term.lower()
                # Search in first name, middle name, or last name
                query_parts.append("""
                    (LOWER(first_name) LIKE ? OR 
                     LOWER(middle_name) LIKE ? OR 
                     LOWER(last_name) LIKE ?)
                """)
                params.extend([f'%{term_lower}%', f'%{term_lower}%', f'%{term_lower}%'])
            
            # Join with AND if multiple terms (all must match)
            where_clause = ' AND '.join(query_parts)
            
            sql = f"""
                SELECT member_id, first_name, middle_name, last_name
                FROM members
                WHERE {where_clause}
                LIMIT 10
            """
            
            results = self.db.fetchall(sql, tuple(params))
            
            if not results:
                QMessageBox.warning(
                    self, 
                    "Not Found", 
                    f"No member found matching: {search_text}"
                )
                return
            elif len(results) == 1:
                # Found exactly one match
                member = self.db.get_member(results[0]['member_id'])
            else:
                # Multiple matches - let user choose
                from PyQt6.QtWidgets import QInputDialog
                names = [
                    f"{r['member_id']}: {r['first_name']} {r.get('middle_name', '')} {r['last_name']}".replace('  ', ' ')
                    for r in results
                ]
                choice, ok = QInputDialog.getItem(
                    self,
                    "Multiple Matches",
                    "Select member:",
                    names,
                    0,
                    False
                )
                if ok and choice:
                    selected_id = choice.split(':')[0]
                    member = self.db.get_member(selected_id)
                else:
                    return
        
        if not member:
            QMessageBox.warning(self, "Not Found", f"Member not found: {search_text}")
            return
        
        member_id = member['member_id']
        self.current_member = member
        accounts = self.db.get_member_savings_accounts(member_id)
        
        # Update member info
        full_name = f"{member['first_name']} {member.get('middle_name', '')} {member['last_name']}".strip()
        self.member_info_label.setText(
            f"<b>Member:</b> {full_name} &nbsp;|&nbsp; <b>ID:</b> {member_id}"
        )
        
        # Populate table
        self.table.setRowCount(len(accounts))
        total_balance = 0
        
        for row, account in enumerate(accounts):
            self.table.setItem(row, 0, QTableWidgetItem(account['account_number']))
            self.table.setItem(row, 1, QTableWidgetItem(account['type_name']))
            
            balance_item = QTableWidgetItem(f"₦{account['current_balance']:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, balance_item)
            
            deposits_item = QTableWidgetItem(f"₦{account['total_deposits']:,.2f}")
            deposits_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, deposits_item)
            
            withdrawals_item = QTableWidgetItem(f"₦{account['total_withdrawals']:,.2f}")
            withdrawals_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, withdrawals_item)
            
            interest_item = QTableWidgetItem(f"₦{account['total_interest_earned']:,.2f}")
            interest_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, interest_item)
            
            total_balance += account['current_balance']
        
        self.summary_label.setText(f"Total Accounts: {len(accounts)} | Total Balance: ₦{total_balance:,.2f}")
        
        self.deposit_btn.setEnabled(True)
        self.withdraw_btn.setEnabled(True)
    
    def deposit(self):
        QMessageBox.information(self, "Deposit", "Deposit functionality - Coming soon!")
    
    def withdraw(self):
        QMessageBox.information(self, "Withdraw", "Withdrawal functionality - Coming soon!")