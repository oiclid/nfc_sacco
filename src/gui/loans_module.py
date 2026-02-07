"""
Loans Module - Complete loan management
=======================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QGroupBox, QTextEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class LoansModule(QWidget):
    """Complete loans management module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.current_user = app.current_user
        self.current_member = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Loans Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        self.disburse_btn = QPushButton("💰 New Loan")
        self.disburse_btn.setFixedHeight(35)
        self.disburse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disburse_btn.setEnabled(False)
        self.disburse_btn.clicked.connect(self.show_disburse_dialog)
        header_layout.addWidget(self.disburse_btn)
        
        self.repay_btn = QPushButton("💵 Record Payment")
        self.repay_btn.setFixedHeight(35)
        self.repay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repay_btn.setEnabled(False)
        self.repay_btn.clicked.connect(self.show_repayment_dialog)
        header_layout.addWidget(self.repay_btn)
        
        layout.addLayout(header_layout)
        
        # Search section
        search_group = QGroupBox("Search Member")
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Member ID:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Member ID (e.g., NFC0001)")
        self.search_input.returnPressed.connect(self.search_member)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self.search_member)
        search_layout.addWidget(search_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Member info
        self.member_info_label = QLabel("No member selected")
        self.member_info_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.member_info_label)
        
        # Loans table
        loans_label = QLabel("Active Loans")
        loans_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        layout.addWidget(loans_label)
        
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(9)
        self.loans_table.setHorizontalHeaderLabels([
            "Loan Number", "Type", "Principal", "Interest", "Total Amount",
            "Monthly Payment", "Amount Paid", "Balance", "Status"
        ])
        
        self.loans_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.loans_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.loans_table.setAlternatingRowColors(True)
        self.loans_table.horizontalHeader().setStretchLastSection(True)
        self.loans_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.loans_table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #7F8C8D; font-size: 10pt;")
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        """Refresh module"""
        if self.current_member:
            self.load_member_loans(self.current_member)
    
    def search_member(self):
        """Search for member"""
        member_id = self.search_input.text().strip().upper()
        
        if not member_id:
            QMessageBox.warning(self, "Search", "Please enter a Member ID")
            return
        
        member = self.db.get_member(member_id)
        
        if not member:
            QMessageBox.warning(
                self,
                "Not Found",
                f"Member '{member_id}' not found."
            )
            return
        
        self.current_member = member
        self.load_member_loans(member)
        
        self.disburse_btn.setEnabled(True)
        self.repay_btn.setEnabled(True)
    
    def load_member_loans(self, member):
        """Load member's loans"""
        full_name = f"{member['first_name']}"
        if member['middle_name']:
            full_name += f" {member['middle_name']}"
        full_name += f" {member['last_name']}"
        
        # Get loans
        loans = self.db.get_member_loans(member['member_id'], active_only=False)
        
        # Calculate totals
        total_outstanding = sum(l['balance_outstanding'] for l in loans if l['status'] == 'Active')
        
        self.member_info_label.setText(
            f"<b>Member:</b> {full_name} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>ID:</b> {member['member_id']} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Total Outstanding:</b> <span style='color: #E74C3C;'>₦{total_outstanding:,.2f}</span>"
        )
        
        # Populate table
        self.loans_table.setRowCount(len(loans))
        
        for row, loan in enumerate(loans):
            self.loans_table.setItem(row, 0, QTableWidgetItem(loan['loan_number']))
            self.loans_table.setItem(row, 1, QTableWidgetItem(loan['type_name']))
            
            # Format currency
            principal_item = QTableWidgetItem(f"₦{loan['principal_amount']:,.2f}")
            principal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 2, principal_item)
            
            interest_item = QTableWidgetItem(f"₦{loan['interest_amount']:,.2f}")
            interest_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 3, interest_item)
            
            total_item = QTableWidgetItem(f"₦{loan['total_amount']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 4, total_item)
            
            monthly_item = QTableWidgetItem(f"₦{loan['monthly_installment']:,.2f}")
            monthly_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 5, monthly_item)
            
            paid_item = QTableWidgetItem(f"₦{loan['amount_paid']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 6, paid_item)
            
            balance_item = QTableWidgetItem(f"₦{loan['balance_outstanding']:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.loans_table.setItem(row, 7, balance_item)
            
            # Status with color
            status_item = QTableWidgetItem(loan['status'])
            if loan['status'] == 'Active':
                status_item.setForeground(Qt.GlobalColor.yellow)
            elif loan['status'] == 'Completed':
                status_item.setForeground(Qt.GlobalColor.green)
            self.loans_table.setItem(row, 8, status_item)
        
        # Update summary
        active_loans = sum(1 for l in loans if l['status'] == 'Active')
        self.summary_label.setText(
            f"Total Loans: {len(loans)} | Active: {active_loans} | "
            f"Total Outstanding: ₦{total_outstanding:,.2f}"
        )
    
    def clear_search(self):
        """Clear search"""
        self.search_input.clear()
        self.current_member = None
        self.loans_table.setRowCount(0)
        self.member_info_label.setText("No member selected")
        self.summary_label.clear()
        
        self.disburse_btn.setEnabled(False)
        self.repay_btn.setEnabled(False)
    
    def show_disburse_dialog(self):
        """Show loan disbursement dialog"""
        if not self.current_member:
            return
        
        dialog = DisburseLoanDialog(self.db, self.current_member, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                loan_data = dialog.get_loan_data()
                
                # Disburse loan
                loan_id = self.db.disburse_loan(loan_data, self.current_user['username'])
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Loan disbursed successfully!\n"
                    f"Loan ID: {loan_id}\n"
                    f"Amount: ₦{loan_data['principal_amount']:,.2f}\n"
                    f"Monthly Payment: ₦{loan_data['principal_amount'] * (1 + loan_data['interest_rate']/100) / loan_data['duration_months']:,.2f}"
                )
                
                self.load_member_loans(self.current_member)
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to disburse loan:\n{str(e)}"
                )
    
    def show_repayment_dialog(self):
        """Show repayment dialog"""
        if not self.current_member:
            return
        
        # Get active loans
        active_loans = self.db.get_member_loans(self.current_member['member_id'], active_only=True)
        
        if not active_loans:
            QMessageBox.information(
                self,
                "No Active Loans",
                "This member has no active loans."
            )
            return
        
        dialog = RepaymentDialog(self.db, self.current_member, active_loans, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                payment_data = dialog.get_payment_data()
                
                # Record repayment
                self.db.record_loan_repayment(
                    payment_data['loan_id'],
                    payment_data['amount'],
                    payment_data,
                    self.current_user['username']
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Payment of ₦{payment_data['amount']:,.2f} recorded successfully!\n"
                    f"Receipt: {payment_data['receipt_number']}"
                )
                
                self.load_member_loans(self.current_member)
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to record payment:\n{str(e)}"
                )


class DisburseLoanDialog(QDialog):
    """Loan disbursement dialog"""
    
    def __init__(self, db, member, parent=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        
        self.setWindowTitle(f"New Loan - {member['member_id']}")
        self.setMinimumWidth(600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Member info
        info_label = QLabel(
            f"<b>Member:</b> {self.member['first_name']} {self.member['last_name']}<br>"
            f"<b>ID:</b> {self.member['member_id']}"
        )
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        # Form
        form_layout = QFormLayout()
        
        # Loan type
        self.type_combo = QComboBox()
        types = self.db.get_loan_types()
        
        for ltype in types:
            self.type_combo.addItem(
                f"{ltype['type_name']} ({ltype['interest_rate']:.0f}% - {ltype['max_duration_months']} months)",
                ltype
            )
        self.type_combo.currentIndexChanged.connect(self.update_loan_calculation)
        form_layout.addRow("Loan Type:*", self.type_combo)
        
        # Principal amount
        self.principal_input = QDoubleSpinBox()
        self.principal_input.setRange(1000, 50000000)
        self.principal_input.setDecimals(2)
        self.principal_input.setPrefix("₦ ")
        self.principal_input.setSingleStep(10000)
        self.principal_input.valueChanged.connect(self.update_loan_calculation)
        form_layout.addRow("Principal Amount:*", self.principal_input)
        
        # Duration
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 36)
        self.duration_input.setSuffix(" months")
        self.duration_input.valueChanged.connect(self.update_loan_calculation)
        form_layout.addRow("Duration:*", self.duration_input)
        
        # Calculation summary
        self.calc_label = QLabel()
        self.calc_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D32;
                border: 1px solid #2980B9;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        form_layout.addRow("", self.calc_label)
        
        # Disbursement date
        self.disbursement_date_input = QDateEdit()
        self.disbursement_date_input.setCalendarPopup(True)
        self.disbursement_date_input.setDate(QDate.currentDate())
        self.disbursement_date_input.dateChanged.connect(self.update_end_date)
        form_layout.addRow("Disbursement Date:*", self.disbursement_date_input)
        
        # Start date
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.dateChanged.connect(self.update_end_date)
        form_layout.addRow("First Payment Date:*", self.start_date_input)
        
        # End date (calculated)
        self.end_date_label = QLabel()
        form_layout.addRow("End Date:", self.end_date_label)
        
        # Payment method
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cheque", "Cash", "Transfer"])
        form_layout.addRow("Payment Method:*", self.payment_combo)
        
        # Cheque/Reference number
        self.cheque_input = QLineEdit()
        form_layout.addRow("Cheque/Ref No:", self.cheque_input)
        
        # Bank name
        self.bank_input = QLineEdit()
        form_layout.addRow("Bank Name:", self.bank_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial calculation
        self.update_loan_calculation()
        self.update_end_date()
    
    def update_loan_calculation(self):
        """Update loan calculation"""
        ltype = self.type_combo.currentData()
        if not ltype:
            return
        
        principal = self.principal_input.value()
        duration = self.duration_input.value()
        interest_rate = ltype['interest_rate']
        
        # Update duration max
        self.duration_input.setMaximum(ltype['max_duration_months'])
        
        # Calculate
        interest_amount = principal * (interest_rate / 100)
        total_amount = principal + interest_amount
        monthly_payment = total_amount / duration if duration > 0 else 0
        
        # Display
        self.calc_label.setText(
            f"<b>Interest ({interest_rate:.0f}%):</b> ₦{interest_amount:,.2f}<br>"
            f"<b>Total Amount:</b> ₦{total_amount:,.2f}<br>"
            f"<b>Monthly Payment:</b> ₦{monthly_payment:,.2f}"
        )
        
        self.update_end_date()
    
    def update_end_date(self):
        """Update end date"""
        start_date = self.start_date_input.date().toPyDate()
        duration = self.duration_input.value()
        
        end_date = start_date + relativedelta(months=duration)
        self.end_date_label.setText(end_date.strftime('%Y-%m-%d'))
    
    def get_loan_data(self):
        """Get loan data"""
        ltype = self.type_combo.currentData()
        
        if self.principal_input.value() <= 0:
            raise ValueError("Principal amount must be greater than zero")
        
        if self.duration_input.value() <= 0:
            raise ValueError("Duration must be greater than zero")
        
        # Get station from member
        member = self.db.get_member(self.member['member_id'])
        
        return {
            'member_id': self.member['member_id'],
            'station_id': member['station_id'],
            'loan_type_id': ltype['loan_type_id'],
            'principal_amount': self.principal_input.value(),
            'interest_rate': ltype['interest_rate'],
            'duration_months': self.duration_input.value(),
            'disbursement_date': self.disbursement_date_input.date().toString('yyyy-MM-dd'),
            'start_date': self.start_date_input.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date_label.text(),
            'payment_method': self.payment_combo.currentText(),
            'cheque_number': self.cheque_input.text().strip() or None,
            'bank_name': self.bank_input.text().strip() or None
        }


class RepaymentDialog(QDialog):
    """Loan repayment dialog"""
    
    def __init__(self, db, member, loans, parent=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        self.loans = loans
        
        self.setWindowTitle(f"Loan Repayment - {member['member_id']}")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        # Loan selection
        self.loan_combo = QComboBox()
        for loan in self.loans:
            self.loan_combo.addItem(
                f"{loan['type_name']} - ₦{loan['balance_outstanding']:,.2f} (Monthly: ₦{loan['monthly_installment']:,.2f})",
                loan
            )
        self.loan_combo.currentIndexChanged.connect(self.update_loan_info)
        form_layout.addRow("Select Loan:*", self.loan_combo)
        
        # Loan info
        self.loan_info_label = QLabel()
        self.loan_info_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        form_layout.addRow("", self.loan_info_label)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₦ ")
        self.amount_input.setSingleStep(1000)
        form_layout.addRow("Payment Amount:*", self.amount_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Payment Date:*", self.date_input)
        
        # Payment method
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Cheque", "Transfer", "Deduction"])
        form_layout.addRow("Payment Method:*", self.payment_combo)
        
        # Receipt number
        self.receipt_input = QLineEdit()
        self.receipt_input.setText(f"RPY-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        form_layout.addRow("Receipt Number:*", self.receipt_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(60)
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial update
        self.update_loan_info()
    
    def update_loan_info(self):
        """Update loan information"""
        loan = self.loan_combo.currentData()
        if not loan:
            return
        
        # Set suggested amount
        self.amount_input.setValue(loan['monthly_installment'])
        
        # Display loan info
        self.loan_info_label.setText(
            f"<b>Total Amount:</b> ₦{loan['total_amount']:,.2f}<br>"
            f"<b>Amount Paid:</b> ₦{loan['amount_paid']:,.2f}<br>"
            f"<b>Balance Outstanding:</b> ₦{loan['balance_outstanding']:,.2f}<br>"
            f"<b>Expected Monthly:</b> ₦{loan['monthly_installment']:,.2f}"
        )
    
    def get_payment_data(self):
        """Get payment data"""
        loan = self.loan_combo.currentData()
        
        if self.amount_input.value() <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        if not self.receipt_input.text().strip():
            raise ValueError("Receipt number is required")
        
        return {
            'loan_id': loan['loan_id'],
            'amount': self.amount_input.value(),
            'payment_date': self.date_input.date().toString('yyyy-MM-dd'),
            'payment_method': self.payment_combo.currentText(),
            'receipt_number': self.receipt_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip() or None
        }
