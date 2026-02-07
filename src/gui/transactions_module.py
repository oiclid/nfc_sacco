"""
Transactions Module - View all transactions
===========================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class TransactionsModule(QWidget):
    """Transactions viewing module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Transaction History")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)
        
        filter_layout.addWidget(QLabel("Member ID:"))
        self.member_input = QLineEdit()
        self.member_input.setPlaceholderText("Optional")
        filter_layout.addWidget(self.member_input)
        
        filter_btn = QPushButton("Apply Filters")
        filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Date", "Member ID", "Type", "Account Type",
            "Description", "Amount", "Credit/Debit", "Payment Method"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #7F8C8D;")
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        """Refresh transactions"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply filters and load transactions"""
        start_date = self.from_date.date().toString('yyyy-MM-dd')
        end_date = self.to_date.date().toString('yyyy-MM-dd')
        member_id = self.member_input.text().strip().upper() or None
        
        transactions = self.db.get_transactions(member_id, start_date, end_date)
        
        # Populate table
        self.table.setRowCount(len(transactions))
        
        total_credit = 0
        total_debit = 0
        
        for row, txn in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(txn['transaction_date']))
            self.table.setItem(row, 1, QTableWidgetItem(txn['member_id']))
            self.table.setItem(row, 2, QTableWidgetItem(txn['transaction_type']))
            self.table.setItem(row, 3, QTableWidgetItem(txn['account_type']))
            self.table.setItem(row, 4, QTableWidgetItem(txn['description'] or ''))
            
            amount_item = QTableWidgetItem(f"₦{txn['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, amount_item)
            
            cd = "Credit" if txn['is_credit'] else "Debit"
            cd_item = QTableWidgetItem(cd)
            cd_item.setForeground(Qt.GlobalColor.green if txn['is_credit'] else Qt.GlobalColor.red)
            self.table.setItem(row, 6, cd_item)
            
            self.table.setItem(row, 7, QTableWidgetItem(txn['payment_method'] or ''))
            
            if txn['is_credit']:
                total_credit += txn['amount']
            else:
                total_debit += txn['amount']
        
        self.summary_label.setText(
            f"Total Transactions: {len(transactions)} | "
            f"Total Credits: ₦{total_credit:,.2f} | "
            f"Total Debits: ₦{total_debit:,.2f}"
        )
