"""
Reports Module - Generate various reports
=========================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QDateEdit, QMessageBox, QLineEdit,
    QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from datetime import datetime
import os
import sys

# Import report generator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reports.report_generator import ReportGenerator


class ReportsModule(QWidget):
    """Reports generation module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.report_gen = ReportGenerator(self.db)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Date range selection
        date_group = QGroupBox("Report Period")
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.from_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.to_date)
        
        date_layout.addStretch()
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Financial Reports
        financial_group = QGroupBox("Financial Reports")
        financial_layout = QGridLayout()
        
        reports = [
            ("💰 Cashbook", self.generate_cashbook),
            ("📊 Income & Expenditure", self.generate_income_expenditure),
            ("💵 Statement of Financial Position", self.generate_financial_position),
            ("📈 Monthly Revenue", self.generate_monthly_revenue),
            ("🏦 Bank Reconciliation", self.generate_bank_reconciliation),
            ("💳 Bank Statement", self.generate_bank_statement)
        ]
        
        for i, (label, handler) in enumerate(reports):
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            financial_layout.addWidget(btn, i // 2, i % 2)
        
        financial_group.setLayout(financial_layout)
        layout.addWidget(financial_group)
        
        # Member Reports
        member_group = QGroupBox("Member Reports")
        member_layout = QGridLayout()
        
        member_reports = [
            ("👥 Member Statements", self.generate_member_statements),
            ("💾 Accounts Ledger", self.generate_accounts_ledger),
            ("📋 Member Summary", self.generate_member_summary)
        ]
        
        for i, (label, handler) in enumerate(member_reports):
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            member_layout.addWidget(btn, i // 2, i % 2)
        
        member_group.setLayout(member_layout)
        layout.addWidget(member_group)
        
        # Loan Reports
        loan_group = QGroupBox("Loan Reports")
        loan_layout = QGridLayout()
        
        loan_reports = [
            ("💳 Monthly Repayments", self.generate_monthly_repayments),
            ("💰 Monthly Disbursements", self.generate_monthly_disbursements),
            ("📉 Loan Portfolio", self.generate_loan_portfolio)
        ]
        
        for i, (label, handler) in enumerate(loan_reports):
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(handler)
            loan_layout.addWidget(btn, i // 2, i % 2)
        
        loan_group.setLayout(loan_layout)
        layout.addWidget(loan_group)
        
        # Audit Report
        audit_group = QGroupBox("Audit & Compliance")
        audit_layout = QHBoxLayout()
        
        audit_btn = QPushButton("📋 Generate Audit Report")
        audit_btn.setFixedHeight(50)
        audit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        audit_btn.clicked.connect(self.generate_audit_report)
        audit_layout.addWidget(audit_btn)
        
        audit_group.setLayout(audit_layout)
        layout.addWidget(audit_group)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh module"""
        pass
    
    def generate_cashbook(self):
        """Generate cashbook report"""
        start_date = self.from_date.date().toString('yyyy-MM-dd')
        end_date = self.to_date.date().toString('yyyy-MM-dd')
        
        try:
            filepath = self.report_gen.generate_cashbook_pdf(start_date, end_date)
            
            QMessageBox.information(
                self,
                "Success",
                f"Cashbook report generated successfully!\n\n"
                f"Saved to: {filepath}"
            )
            
            # Open the PDF
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate cashbook:\n{str(e)}"
            )
    
    def generate_income_expenditure(self):
        """Generate income & expenditure statement"""
        QMessageBox.information(
            self,
            "Income & Expenditure",
            "Income & Expenditure statement will be implemented.\n\n"
            "This will show comprehensive financial performance."
        )
    
    def generate_financial_position(self):
        """Generate statement of financial position"""
        QMessageBox.information(
            self,
            "Financial Position",
            "Statement of Financial Position (Balance Sheet) will be implemented.\n\n"
            "This will show assets, liabilities, and equity."
        )
    
    def generate_monthly_revenue(self):
        """Generate monthly revenue report"""
        QMessageBox.information(
            self,
            "Monthly Revenue",
            "Monthly Revenue report will be implemented.\n\n"
            "This will show all income sources for the month."
        )
    
    def generate_bank_reconciliation(self):
        """Generate bank reconciliation"""
        QMessageBox.information(
            self,
            "Bank Reconciliation",
            "Bank Reconciliation report will be implemented.\n\n"
            "This will match book records with bank statements."
        )
    
    def generate_bank_statement(self):
        """Generate bank statement"""
        QMessageBox.information(
            self,
            "Bank Statement",
            "Bank Statement report will be implemented.\n\n"
            "This will show all bank transactions."
        )
    
    def generate_member_statements(self):
        """Generate member statements"""
        # Ask for member ID
        member_id, ok = QInputDialog.getText(
            self,
            "Member Statement",
            "Enter Member ID (or leave blank for all):"
        )
        
        if not ok:
            return
        
        member_id = member_id.strip().upper()
        start_date = self.from_date.date().toString('yyyy-MM-dd')
        end_date = self.to_date.date().toString('yyyy-MM-dd')
        
        try:
            if member_id:
                # Single member statement
                filepath = self.report_gen.generate_member_statement_pdf(
                    member_id, start_date, end_date
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Member statement generated successfully!\n\n"
                    f"Saved to: {filepath}"
                )
                
                # Open the PDF
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
            else:
                QMessageBox.information(
                    self,
                    "All Members",
                    "Generating statements for all members...\nThis may take a few minutes."
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate report:\n{str(e)}"
            )
    
    def generate_accounts_ledger(self):
        """Generate accounts ledger"""
        QMessageBox.information(
            self,
            "Accounts Ledger",
            "Accounts Ledger report will be implemented.\n\n"
            "This will show complete transaction history by account."
        )
    
    def generate_member_summary(self):
        """Generate member summary"""
        start_date = self.from_date.date().toString('yyyy-MM-dd')
        end_date = self.to_date.date().toString('yyyy-MM-dd')
        
        try:
            filepath = self.report_gen.generate_member_summary_excel(start_date, end_date)
            
            QMessageBox.information(
                self,
                "Success",
                f"Member Summary generated successfully!\n\n"
                f"Excel file saved to: {filepath}\n\n"
                f"Opening file..."
            )
            
            # Open the Excel file
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate summary:\n{str(e)}"
            )
    
    def generate_monthly_repayments(self):
        """Generate monthly repayments report"""
        QMessageBox.information(
            self,
            "Monthly Repayments",
            "Monthly Loan Repayments report will be implemented.\n\n"
            "This will show all loan payments received."
        )
    
    def generate_monthly_disbursements(self):
        """Generate monthly disbursements report"""
        QMessageBox.information(
            self,
            "Monthly Disbursements",
            "Monthly Loan Disbursements report will be implemented.\n\n"
            "This will show all loans disbursed."
        )
    
    def generate_loan_portfolio(self):
        """Generate loan portfolio report"""
        try:
            filepath = self.report_gen.generate_loan_portfolio_excel()
            
            QMessageBox.information(
                self,
                "Success",
                f"Loan Portfolio Analysis generated successfully!\n\n"
                f"Excel file saved to: {filepath}\n\n"
                "This report includes:\n"
                "- Portfolio summary\n"
                "- Detailed loan list\n"
                "- Performance metrics\n\n"
                "Opening file..."
            )
            
            # Open the Excel file
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate loan portfolio:\n{str(e)}"
            )
    
    def generate_audit_report(self):
        """Generate audit report"""
        QMessageBox.information(
            self,
            "Audit Report",
            "Comprehensive Audit Report will be implemented.\n\n"
            "This will include:\n"
            "- All financial statements\n"
            "- Compliance checks\n"
            "- Transaction verification\n"
            "- Recommendations"
        )
