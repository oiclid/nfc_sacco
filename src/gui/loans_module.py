"""
Loans Module - Enhanced with Advanced Search
=============================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QDialog, QFormLayout, QComboBox, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QGroupBox, QTextEdit, QSpinBox, QCheckBox,
    QScrollArea, QFrame, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class LoansModule(QWidget):
    """Enhanced loans management module with advanced search"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.current_user = app.current_user
        self.selected_members = []  # Store multiple selected members
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
        self.disburse_btn.setMinimumHeight(40)
        self.disburse_btn.setMinimumWidth(130)
        self.disburse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disburse_btn.setEnabled(False)
        self.disburse_btn.clicked.connect(self.show_disburse_dialog)
        header_layout.addWidget(self.disburse_btn)
        
        self.repay_btn = QPushButton("💵 Record Payment")
        self.repay_btn.setMinimumHeight(40)
        self.repay_btn.setMinimumWidth(150)
        self.repay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repay_btn.setEnabled(False)
        self.repay_btn.clicked.connect(self.show_repayment_dialog)
        header_layout.addWidget(self.repay_btn)
        
        layout.addLayout(header_layout)
        
        # Advanced Search Section
        search_group = QGroupBox("🔍 Advanced Search")
        search_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        search_layout = QVBoxLayout()
        
        # Search criteria row 1
        search_row1 = QHBoxLayout()
        
        # Member ID/Name search
        search_row1.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Member ID (full or partial) or Name (full or partial)")
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_row1.addWidget(self.search_input, 3)
        
        # Loan type filter
        search_row1.addWidget(QLabel("Loan Type:"))
        self.loan_type_filter = QComboBox()
        self.loan_type_filter.setMinimumHeight(35)
        self.loan_type_filter.setMinimumWidth(180)
        self.loan_type_filter.addItem("All Types", None)
        self._load_loan_types()
        self.loan_type_filter.currentIndexChanged.connect(self.apply_filters)
        search_row1.addWidget(self.loan_type_filter)
        
        search_layout.addLayout(search_row1)
        
        # Search criteria row 2
        search_row2 = QHBoxLayout()
        
        # Status filter
        search_row2.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(35)
        self.status_filter.setMinimumWidth(130)
        self.status_filter.addItems(["All", "Active", "Completed", "Defaulted"])
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        search_row2.addWidget(self.status_filter)
        
        search_row2.addStretch()
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.setMinimumHeight(35)
        search_btn.setMinimumWidth(120)
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self.perform_search)
        search_row2.addWidget(search_btn)
        
        # Clear button
        clear_btn = QPushButton("✖ Clear")
        clear_btn.setMinimumHeight(35)
        clear_btn.setMinimumWidth(100)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_search)
        search_row2.addWidget(clear_btn)
        
        search_layout.addLayout(search_row2)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Search Results / Selected Members
        self.results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()
        
        # Results table with horizontal and vertical scroll
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Select", "Member ID", "Name", "Station", "Active Loans", "Total Outstanding"
        ])
        
        # Enable scrollbars
        self.results_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.results_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Table settings
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setMinimumHeight(200)
        
        # Set column widths
        self.results_table.setColumnWidth(0, 60)   # Select
        self.results_table.setColumnWidth(1, 120)  # Member ID
        self.results_table.setColumnWidth(2, 250)  # Name
        self.results_table.setColumnWidth(3, 150)  # Station
        self.results_table.setColumnWidth(4, 120)  # Active Loans
        self.results_table.setColumnWidth(5, 150)  # Total Outstanding
        
        self.results_table.cellClicked.connect(self.on_result_selected)
        results_layout.addWidget(self.results_table)
        
        # Selected members info
        self.selected_info_label = QLabel("No members selected")
        self.selected_info_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
                color: #BDC3C7;
            }
        """)
        results_layout.addWidget(self.selected_info_label)
        
        self.results_group.setLayout(results_layout)
        layout.addWidget(self.results_group)
        
        # Loans table for selected member(s)
        loans_label = QLabel("Loans for Selected Member(s)")
        loans_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(loans_label)
        
        # Loans table with full scrolling support
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(12)
        self.loans_table.setHorizontalHeaderLabels([
            "Loan #", "Member", "Type", "Principal", "Interest %", 
            "Total Amount", "Monthly Payment", "Outstanding", 
            "Start Date", "End Date", "Status", "Actions"
        ])
        
        # Enable all scrollbars
        self.loans_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.loans_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.loans_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.loans_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Table settings
        self.loans_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.loans_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.loans_table.setAlternatingRowColors(True)
        self.loans_table.verticalHeader().setVisible(False)
        self.loans_table.setSortingEnabled(True)
        
        # Set minimum column widths
        header = self.loans_table.horizontalHeader()
        for i in range(12):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.loans_table)
        
        # Summary label
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #7F8C8D; font-size: 11pt; padding: 5px;")
        self.summary_label.setMinimumHeight(30)
        layout.addWidget(self.summary_label)
        
        # Initialize
        self.clear_search()
    
    def _load_loan_types(self):
        """Load loan types into filter"""
        try:
            loan_types = self.db.get_loan_types()
            for lt in loan_types:
                self.loan_type_filter.addItem(lt['type_name'], lt['loan_type_id'])
        except:
            pass
    
    def on_search_text_changed(self, text):
        """Auto-search as user types"""
        if len(text) >= 2:  # Start searching after 2 characters
            self.perform_search()
        elif len(text) == 0:
            self.clear_results()
    
    def perform_search(self):
        """Perform advanced member search"""
        search_term = self.search_input.text().strip().upper()
        
        if not search_term:
            self.clear_results()
            return
        
        # Search in members table
        query = """
            SELECT DISTINCT m.*, s.station_name,
                   COUNT(DISTINCT l.loan_id) as active_loans,
                   COALESCE(SUM(CASE WHEN l.status = 'Active' THEN l.balance_outstanding ELSE 0 END), 0) as total_outstanding
            FROM members m
            LEFT JOIN stations s ON m.station_id = s.station_id
            LEFT JOIN loans l ON m.member_id = l.member_id
            WHERE (
                UPPER(m.member_id) LIKE ? OR
                UPPER(m.first_name) LIKE ? OR
                UPPER(m.middle_name) LIKE ? OR
                UPPER(m.last_name) LIKE ? OR
                UPPER(m.first_name || ' ' || COALESCE(m.middle_name, '') || ' ' || m.last_name) LIKE ?
            )
            GROUP BY m.member_id
            ORDER BY m.member_id
        """
        
        search_pattern = f"%{search_term}%"
        results = self.db.fetchall(query, (search_pattern, search_pattern, search_pattern, 
                                            search_pattern, search_pattern))
        
        self.populate_results(results)
    
    def populate_results(self, results):
        """Populate search results table"""
        self.results_table.setSortingEnabled(False)
        self.results_table.setRowCount(0)
        
        for result in results:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox { margin-left: 20px; }")
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.results_table.setCellWidget(row, 0, checkbox_widget)
            checkbox.stateChanged.connect(lambda state, r=result: self.toggle_member_selection(r, state))
            
            # Member ID
            self.results_table.setItem(row, 1, QTableWidgetItem(result['member_id']))
            
            # Full Name
            full_name = f"{result['first_name']} {result.get('middle_name', '')} {result['last_name']}".strip()
            self.results_table.setItem(row, 2, QTableWidgetItem(full_name))
            
            # Station
            self.results_table.setItem(row, 3, QTableWidgetItem(result.get('station_name', 'N/A')))
            
            # Active Loans
            active_loans_item = QTableWidgetItem(str(result.get('active_loans', 0)))
            active_loans_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 4, active_loans_item)
            
            # Total Outstanding
            outstanding_item = QTableWidgetItem(f"₦{result.get('total_outstanding', 0):,.2f}")
            outstanding_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(row, 5, outstanding_item)
        
        self.results_table.setSortingEnabled(True)
        
        # Update summary
        if results:
            self.summary_label.setText(f"Found {len(results)} member(s) matching your search")
        else:
            self.summary_label.setText("No members found matching your search criteria")
    
    def toggle_member_selection(self, member, state):
        """Toggle member selection"""
        member_id = member['member_id']
        
        if state == Qt.CheckState.Checked.value:
            if member_id not in [m['member_id'] for m in self.selected_members]:
                self.selected_members.append(member)
        else:
            self.selected_members = [m for m in self.selected_members if m['member_id'] != member_id]
        
        self.update_selected_info()
        self.load_selected_members_loans()
    
    def on_result_selected(self, row, column):
        """Handle result table cell click"""
        # Get member from this row
        if column != 0:  # Not the checkbox column
            # Toggle the checkbox
            checkbox_widget = self.results_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
    
    def update_selected_info(self):
        """Update selected members info label"""
        count = len(self.selected_members)
        if count == 0:
            self.selected_info_label.setText("No members selected")
            self.disburse_btn.setEnabled(False)
            self.repay_btn.setEnabled(False)
        elif count == 1:
            member = self.selected_members[0]
            full_name = f"{member['first_name']} {member.get('middle_name', '')} {member['last_name']}".strip()
            self.selected_info_label.setText(
                f"Selected: {member['member_id']} - {full_name}"
            )
            self.disburse_btn.setEnabled(True)
            self.repay_btn.setEnabled(True)
        else:
            member_ids = ", ".join([m['member_id'] for m in self.selected_members])
            self.selected_info_label.setText(
                f"Selected {count} members: {member_ids}"
            )
            self.disburse_btn.setEnabled(False)  # Can't disburse to multiple
            self.repay_btn.setEnabled(False)     # Can't repay for multiple
    
    def load_selected_members_loans(self):
        """Load loans for all selected members"""
        self.loans_table.setSortingEnabled(False)
        self.loans_table.setRowCount(0)
        
        if not self.selected_members:
            return
        
        all_loans = []
        for member in self.selected_members:
            loans = self.db.get_member_loans(member['member_id'], active_only=False)
            all_loans.extend(loans)
        
        # Apply filters
        filtered_loans = self.apply_loan_filters(all_loans)
        
        for loan in filtered_loans:
            self.add_loan_to_table(loan)
        
        self.loans_table.setSortingEnabled(True)
    
    def apply_loan_filters(self, loans):
        """Apply loan type and status filters"""
        filtered = loans
        
        # Filter by loan type
        loan_type_id = self.loan_type_filter.currentData()
        if loan_type_id:
            filtered = [l for l in filtered if l['loan_type_id'] == loan_type_id]
        
        # Filter by status
        status = self.status_filter.currentText()
        if status != "All":
            filtered = [l for l in filtered if l['status'] == status]
        
        return filtered
    
    def apply_filters(self):
        """Reapply filters to current loans"""
        self.load_selected_members_loans()
    
    def add_loan_to_table(self, loan):
        """Add a loan row to the table"""
        row = self.loans_table.rowCount()
        self.loans_table.insertRow(row)
        
        # Loan Number
        self.loans_table.setItem(row, 0, QTableWidgetItem(loan.get('loan_number', 'N/A')))
        
        # Member ID
        self.loans_table.setItem(row, 1, QTableWidgetItem(loan['member_id']))
        
        # Loan Type
        self.loans_table.setItem(row, 2, QTableWidgetItem(loan.get('type_name', 'N/A')))
        
        # Principal
        principal_item = QTableWidgetItem(f"₦{loan['principal_amount']:,.2f}")
        principal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.loans_table.setItem(row, 3, principal_item)
        
        # Interest %
        interest_item = QTableWidgetItem(f"{loan['interest_rate']:.1f}%")
        interest_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loans_table.setItem(row, 4, interest_item)
        
        # Total Amount
        total_item = QTableWidgetItem(f"₦{loan['total_amount']:,.2f}")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.loans_table.setItem(row, 5, total_item)
        
        # Monthly Payment
        monthly_item = QTableWidgetItem(f"₦{loan['monthly_installment']:,.2f}")
        monthly_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.loans_table.setItem(row, 6, monthly_item)
        
        # Outstanding
        outstanding_item = QTableWidgetItem(f"₦{loan['balance_outstanding']:,.2f}")
        outstanding_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if loan['balance_outstanding'] > 0:
            outstanding_item.setForeground(Qt.GlobalColor.red if loan['status'] == 'Defaulted' else Qt.GlobalColor.yellow)
        else:
            outstanding_item.setForeground(Qt.GlobalColor.green)
        self.loans_table.setItem(row, 7, outstanding_item)
        
        # Start Date
        self.loans_table.setItem(row, 8, QTableWidgetItem(loan.get('start_date', 'N/A')))
        
        # End Date
        self.loans_table.setItem(row, 9, QTableWidgetItem(loan.get('end_date', 'N/A')))
        
        # Status
        status_item = QTableWidgetItem(loan['status'])
        status_item.setForeground(
            Qt.GlobalColor.green if loan['status'] == 'Completed' else
            Qt.GlobalColor.red if loan['status'] == 'Defaulted' else
            Qt.GlobalColor.yellow
        )
        self.loans_table.setItem(row, 10, status_item)
        
        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        actions_layout.setSpacing(4)
        
        view_btn = QPushButton("👁️")
        view_btn.setToolTip("View Details")
        view_btn.setMinimumHeight(30)
        view_btn.setMinimumWidth(35)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.clicked.connect(lambda checked, l=loan: self.view_loan_details(l))
        actions_layout.addWidget(view_btn)
        
        if loan['status'] == 'Active':
            pay_btn = QPushButton("💵")
            pay_btn.setToolTip("Record Payment")
            pay_btn.setMinimumHeight(30)
            pay_btn.setMinimumWidth(35)
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.clicked.connect(lambda checked, l=loan: self.quick_payment(l))
            actions_layout.addWidget(pay_btn)
        
        self.loans_table.setCellWidget(row, 11, actions_widget)
    
    def clear_results(self):
        """Clear search results"""
        self.results_table.setRowCount(0)
        self.summary_label.setText("")
    
    def clear_search(self):
        """Clear all search fields and results"""
        self.search_input.clear()
        self.loan_type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.selected_members.clear()
        self.clear_results()
        self.loans_table.setRowCount(0)
        self.update_selected_info()
        self.summary_label.setText("Enter search criteria to find members")
    
    def show_disburse_dialog(self):
        """Show loan disbursement dialog"""
        if not self.selected_members or len(self.selected_members) != 1:
            QMessageBox.warning(self, "Warning", "Please select exactly one member")
            return
        
        # TODO: Implement disburse dialog
        QMessageBox.information(self, "Info", "Disbursement dialog - to be implemented")
    
    def show_repayment_dialog(self):
        """Show repayment dialog"""
        if not self.selected_members or len(self.selected_members) != 1:
            QMessageBox.warning(self, "Warning", "Please select exactly one member")
            return
        
        # TODO: Implement repayment dialog
        QMessageBox.information(self, "Info", "Repayment dialog - to be implemented")
    
    def view_loan_details(self, loan):
        """View loan details"""
        # TODO: Implement loan details dialog
        QMessageBox.information(self, "Info", f"Loan details for {loan.get('loan_number', 'N/A')}")
    
    def quick_payment(self, loan):
        """Quick payment for a loan"""
        # TODO: Implement quick payment dialog
        QMessageBox.information(self, "Info", f"Quick payment for loan {loan.get('loan_number', 'N/A')}")
    
    def refresh(self):
        """Refresh the current view"""
        if self.selected_members:
            self.load_selected_members_loans()
        elif self.search_input.text():
            self.perform_search()
