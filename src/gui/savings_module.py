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
        
        # Search with updated placeholder
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Member ID, First Name, Middle Name, or Last Name (use & or + for multiple members)...")
        self.search_input.returnPressed.connect(self.search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
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
        
        # Accounts table with improved column headers and scrolling
        self.table = QTableWidget()
        self.table.setColumnCount(8)  # Added 2 columns: Member Name and Station Name
        self.table.setHorizontalHeaderLabels([
            "Member Name",
            "Station Name", 
            "Account Number", 
            "Type", 
            "Balance", 
            "Total Deposits",
            "Total Withdrawals", 
            "Interest Earned"
        ])
        
        # Enable both horizontal and vertical scrolling
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Expand column headers for better readability
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Member Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Station Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Account Number
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Balance
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Total Deposits
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Total Withdrawals
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Interest Earned
        
        # Set minimum column widths for better readability
        self.table.setColumnWidth(0, 180)  # Member Name
        self.table.setColumnWidth(1, 150)  # Station Name
        self.table.setColumnWidth(2, 120)  # Account Number
        self.table.setColumnWidth(3, 180)  # Type
        self.table.setColumnWidth(4, 120)  # Balance
        self.table.setColumnWidth(5, 130)  # Total Deposits
        self.table.setColumnWidth(6, 150)  # Total Withdrawals
        self.table.setColumnWidth(7, 130)  # Interest Earned
        
        layout.addWidget(self.table)
        
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        if self.current_member:
            self.search()
    
    def search(self):
        """
        Enhanced search supporting:
        1. Search by first name, middle name, last name, or member ID
        2. Multiple member search using & or + separator
        """
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Search", "Please enter a Member ID or name to search")
            return
        
        # Check if searching for multiple members (using & or +)
        if '&' in search_text or '+' in search_text:
            # Split by both separators
            search_terms = []
            for term in search_text.replace('+', '&').split('&'):
                term = term.strip()
                if term:
                    search_terms.append(term)
            
            if not search_terms:
                QMessageBox.warning(self, "Search", "Please enter valid search terms")
                return
            
            # Search for multiple members
            self._search_multiple_members(search_terms)
        else:
            # Single member search
            self._search_single_member(search_text)
    
    def _search_single_member(self, search_term):
        """Search for a single member by ID or name - shows all matches if multiple found"""
        # First try exact member ID match
        member = self.db.get_member(search_term.upper())
        
        # If found by exact ID, show just that member
        if member:
            members = [member]
        else:
            # Search by name (partial match)
            members = self.db.search_members(search_term)
            
            if not members:
                QMessageBox.warning(self, "Not Found", f"No member found matching '{search_term}'")
                return
        
        # Show all matching members (whether 1 or many)
        all_members = []
        all_accounts = []
        all_stations = []
        
        for m in members:
            member_id = m['member_id']
            accounts = self.db.get_member_savings_accounts(member_id)
            
            # Get station name
            station = self.db.fetchone("SELECT station_name FROM stations WHERE station_id = ?", 
                                       (m['station_id'],))
            station_name = station['station_name'] if station else "Unknown"
            
            all_members.append(m)
            all_accounts.append(accounts)
            all_stations.append(station_name)
        
        # Update member info
        if len(all_members) == 1:
            # Single member
            member = all_members[0]
            full_name = f"{member['first_name']} {member.get('middle_name', '')} {member['last_name']}".strip()
            self.member_info_label.setText(
                f"<b>Member:</b> {full_name} &nbsp;|&nbsp; <b>ID:</b> {member['member_id']} &nbsp;|&nbsp; <b>Station:</b> {all_stations[0]}"
            )
            self.current_member = member
            self.deposit_btn.setEnabled(True)
            self.withdraw_btn.setEnabled(True)
        else:
            # Multiple members
            member_names = [f"{m['first_name']} {m['last_name']}" for m in all_members]
            self.member_info_label.setText(
                f"<b>Viewing {len(all_members)} members matching '{search_term}':</b> {', '.join(member_names)}"
            )
            self.current_member = None
            self.deposit_btn.setEnabled(False)
            self.withdraw_btn.setEnabled(False)
        
        # Populate table with all matches
        self._populate_table(all_members, all_accounts, all_stations)
    
    def _search_multiple_members(self, search_terms):
        """
        Search for multiple members using & or + separator
        Returns all matches for each search term
        
        Why support both & and +?
        - '&' (ampersand): Common in data/spreadsheet contexts, easy to type with Shift+7
        - '+' (plus): More intuitive for users thinking "add another member", easy to type
        
        Both separators work identically to maximize user flexibility and convenience.
        """
        all_members = []
        all_accounts = []
        all_stations = []
        not_found = []
        
        for search_term in search_terms:
            # Try exact member ID match first
            member = self.db.get_member(search_term.upper())
            
            if member:
                # Exact ID match found
                members_to_add = [member]
            else:
                # Search by name (partial match)
                members_to_add = self.db.search_members(search_term)
                
                if not members_to_add:
                    not_found.append(search_term)
                    continue
            
            # Add all matching members for this search term
            for m in members_to_add:
                # Get member's accounts
                member_id = m['member_id']
                accounts = self.db.get_member_savings_accounts(member_id)
                
                # Get station name
                station = self.db.fetchone("SELECT station_name FROM stations WHERE station_id = ?", 
                                           (m['station_id'],))
                station_name = station['station_name'] if station else "Unknown"
                
                all_members.append(m)
                all_accounts.append(accounts)
                all_stations.append(station_name)
        
        if not all_members:
            QMessageBox.warning(self, "Not Found", f"No members found for the search terms provided")
            return
        
        # Show warning for any not found
        if not_found:
            msg = f"Could not find members matching:\n" + "\n".join(not_found)
            QMessageBox.warning(self, "Partial Results", msg)
        
        # Update member info for multiple members
        member_names = [f"{m['first_name']} {m['last_name']}" for m in all_members]
        self.member_info_label.setText(
            f"<b>Viewing {len(all_members)} members:</b> {', '.join(member_names[:5])}" + 
            (f" and {len(member_names) - 5} more" if len(member_names) > 5 else "")
        )
        
        # Populate table with all members
        self._populate_table(all_members, all_accounts, all_stations)
        
        # Disable deposit/withdraw for multiple member view
        self.deposit_btn.setEnabled(False)
        self.withdraw_btn.setEnabled(False)
    
    def _populate_table(self, members, accounts_list, station_names):
        """
        Populate the table with account information for one or more members
        
        Args:
            members: List of member dictionaries
            accounts_list: List of account lists (one per member)
            station_names: List of station names (one per member)
        """
        # Temporarily disable sorting while populating
        self.table.setSortingEnabled(False)
        
        # Calculate total rows
        total_rows = sum(len(accounts) for accounts in accounts_list)
        self.table.setRowCount(total_rows)
        
        total_balance = 0
        row = 0
        
        for member, accounts, station_name in zip(members, accounts_list, station_names):
            full_name = f"{member['first_name']} {member.get('middle_name', '')} {member['last_name']}".strip()
            
            for account in accounts:
                # Member Name
                member_name_item = QTableWidgetItem(full_name)
                self.table.setItem(row, 0, member_name_item)
                
                # Station Name
                station_item = QTableWidgetItem(station_name)
                self.table.setItem(row, 1, station_item)
                
                # Account Number
                self.table.setItem(row, 2, QTableWidgetItem(account['account_number']))
                
                # Type
                self.table.setItem(row, 3, QTableWidgetItem(account['type_name']))
                
                # Balance
                balance_item = QTableWidgetItem(f"₦{account['current_balance']:,.2f}")
                balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 4, balance_item)
                
                # Total Deposits
                deposits_item = QTableWidgetItem(f"₦{account['total_deposits']:,.2f}")
                deposits_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 5, deposits_item)
                
                # Total Withdrawals
                withdrawals_item = QTableWidgetItem(f"₦{account['total_withdrawals']:,.2f}")
                withdrawals_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 6, withdrawals_item)
                
                # Interest Earned
                interest_item = QTableWidgetItem(f"₦{account['total_interest_earned']:,.2f}")
                interest_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 7, interest_item)
                
                total_balance += account['current_balance']
                row += 1
        
        # Update summary
        total_accounts = sum(len(accounts) for accounts in accounts_list)
        self.summary_label.setText(
            f"Total Members: {len(members)} | Total Accounts: {total_accounts} | Total Balance: ₦{total_balance:,.2f}"
        )
        
        # Re-enable sorting after populating
        self.table.setSortingEnabled(True)
    
    def deposit(self):
        QMessageBox.information(self, "Deposit", "Deposit functionality - Coming soon!")
    
    def withdraw(self):
        QMessageBox.information(self, "Withdraw", "Withdrawal functionality - Coming soon!")
