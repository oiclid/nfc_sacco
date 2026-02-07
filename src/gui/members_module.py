"""
Members Module - Member management interface
============================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QDateEdit, QMessageBox,
    QGroupBox, QTextEdit, QDialogButtonBox, QScrollArea
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime


class MembersModule(QWidget):
    """Members management module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.current_user = app.current_user
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Member Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID or name...")
        self.search_input.setFixedWidth(300)
        self.search_input.setMinimumHeight(40)  # Taller input
        self.search_input.textChanged.connect(self.search_members)
        header_layout.addWidget(self.search_input)
        
        # Add member button
        add_btn = QPushButton("➕ Add Member")
        add_btn.setMinimumHeight(40)  # Taller button
        add_btn.setMinimumWidth(150)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_member)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Members table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Member ID", "Name", "Gender", "Phone", 
            "Station", "Date Joined", "Status", "Actions"
        ])
        
        # Table settings
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Enable scrollbars - FIXED: Allow horizontal scrolling
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set row height to be taller (readable) - increased for better button visibility
        self.table.verticalHeader().setDefaultSectionSize(60)
        
        # Column widths - FIXED: Give Actions column enough space
        self.table.setColumnWidth(0, 120)  # Member ID
        self.table.setColumnWidth(1, 250)  # Name
        self.table.setColumnWidth(2, 80)   # Gender
        self.table.setColumnWidth(3, 130)  # Phone
        self.table.setColumnWidth(4, 180)  # Station
        self.table.setColumnWidth(5, 120)  # Date Joined
        self.table.setColumnWidth(6, 100)  # Status
        self.table.setColumnWidth(7, 260)  # Actions - FIXED: Enough space for 3 buttons
        
        # Don't stretch last column - use fixed width instead
        self.table.horizontalHeader().setStretchLastSection(False)
        # Allow horizontal scrolling when needed
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #7F8C8D; font-size: 11pt; padding: 5px;")
        self.summary_label.setMinimumHeight(30)
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        """Refresh members list"""
        members = self.db.get_all_members(active_only=False)  # Show ALL members
        self.populate_table(members)
    
    def populate_table(self, members):
        """Populate table with members"""
        self.table.setRowCount(0)
        
        for member in members:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Member ID
            id_item = QTableWidgetItem(member['member_id'])
            id_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 0, id_item)
            
            # Full name
            full_name = f"{member['first_name']}"
            if member['middle_name']:
                full_name += f" {member['middle_name']}"
            full_name += f" {member['last_name']}"
            name_item = QTableWidgetItem(full_name)
            name_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 1, name_item)
            
            # Gender
            gender_item = QTableWidgetItem(member['gender'] or '')
            gender_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 2, gender_item)
            
            # Phone
            phone_item = QTableWidgetItem(member['phone_number'] or '')
            phone_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 3, phone_item)
            
            # Station
            station = self.db.fetchone(
                "SELECT station_name FROM stations WHERE station_id = ?",
                (member['station_id'],)
            )
            station_item = QTableWidgetItem(station['station_name'] if station else '')
            station_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 4, station_item)
            
            # Date joined
            date_item = QTableWidgetItem(member['date_joined'])
            date_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 5, date_item)
            
            # Status - FIXED to show actual status
            if member['is_deceased']:
                status = "Deceased"
                color = "#E74C3C"  # Red
            elif member['is_active']:
                status = "Active"
                color = "#27AE60"  # Green
            else:
                status = "Inactive"
                color = "#F39C12"  # Orange
            
            status_item = QTableWidgetItem(status)
            status_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            status_item.setForeground(Qt.GlobalColor.white)
            status_item.setBackground(Qt.GlobalColor.darkGray if status == "Inactive" else (Qt.GlobalColor.red if status == "Deceased" else Qt.GlobalColor.darkGreen))
            self.table.setItem(row, 6, status_item)
            
            # Actions - Properly sized buttons with vertical centering
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            view_btn = QPushButton("View")
            view_btn.setMinimumHeight(40)
            view_btn.setMinimumWidth(65)
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.clicked.connect(lambda checked, m=member: self.view_member(m))
            actions_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setMinimumHeight(40)
            edit_btn.setMinimumWidth(65)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, m=member: self.edit_member(m))
            actions_layout.addWidget(edit_btn)
            
            status_btn = QPushButton("Status")
            status_btn.setMinimumHeight(40)
            status_btn.setMinimumWidth(65)
            status_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            status_btn.clicked.connect(lambda checked, m=member: self.change_status(m))
            actions_layout.addWidget(status_btn)
            
            actions_layout.addStretch()
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Update summary
        total = len(members)
        active = sum(1 for m in members if m['is_active'])
        inactive = sum(1 for m in members if not m['is_active'] and not m['is_deceased'])
        deceased = sum(1 for m in members if m['is_deceased'])
        
        self.summary_label.setText(
            f"Total Members: {total} | Active: {active} | Inactive: {inactive} | Deceased: {deceased}"
        )
    
    def search_members(self):
        """Search members"""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.refresh()
            return
        
        members = self.db.search_members(search_term)
        self.populate_table(members)
    
    def add_member(self):
        """Show add member dialog"""
        dialog = MemberDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                member_data = dialog.get_member_data()
                member_id = self.db.add_member(member_data, self.current_user['username'])
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Member added successfully!\nMember ID: {member_id}"
                )
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add member:\n{str(e)}"
                )
    
    def edit_member(self, member):
        """Show edit member dialog"""
        dialog = MemberDialog(self.db, member, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                member_data = dialog.get_member_data()
                self.db.update_member(
                    member['member_id'],
                    member_data,
                    self.current_user['username']
                )
                
                QMessageBox.information(self, "Success", "Member updated successfully!")
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update member:\n{str(e)}"
                )
    
    def view_member(self, member):
        """Show member details"""
        dialog = MemberDetailsDialog(self.db, member, self)
        dialog.exec()
    
    def change_status(self, member):
        """Change member status (Active/Inactive/Deceased)"""
        dialog = ChangeStatusDialog(self.db, member, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                status_data = dialog.get_status_data()
                
                # Update member status in database
                self.db.execute(
                    """
                    UPDATE members 
                    SET is_active = ?, 
                        is_deceased = ?, 
                        deceased_date = ?,
                        modified_date = datetime('now'),
                        modified_by = ?
                    WHERE member_id = ?
                    """,
                    (
                        status_data['is_active'],
                        status_data['is_deceased'],
                        status_data['deceased_date'],
                        self.current_user['username'],
                        member['member_id']
                    )
                )
                
                status_name = "Deceased" if status_data['is_deceased'] else ("Active" if status_data['is_active'] else "Inactive")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Member status changed to: {status_name}"
                )
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update member status:\n{str(e)}"
                )


class MemberDialog(QDialog):
    """Dialog for adding/editing members"""
    
    def __init__(self, db, member=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        self.is_edit = member is not None
        
        self.setWindowTitle("Edit Member" if self.is_edit else "Add Member")
        
        # Make dialog responsive to screen size
        if parent:
            screen = parent.screen().availableGeometry()
            # Use 60% of screen height, max 800px
            dialog_height = min(int(screen.height() * 0.60), 800)
            dialog_width = min(int(screen.width() * 0.50), 700)
            self.resize(dialog_width, dialog_height)
        else:
            self.setMinimumSize(600, 500)
            self.resize(700, 700)
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_member_data()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Basic Info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        # Station
        self.station_combo = QComboBox()
        self.station_combo.setMinimumHeight(35)
        stations = self.db.get_all_stations()
        for station in stations:
            self.station_combo.addItem(station['station_name'], station['station_id'])
        basic_layout.addRow("Station:", self.station_combo)
        
        # First name
        self.first_name_input = QLineEdit()
        self.first_name_input.setMinimumHeight(35)
        basic_layout.addRow("First Name:*", self.first_name_input)
        
        # Middle name
        self.middle_name_input = QLineEdit()
        self.middle_name_input.setMinimumHeight(35)
        basic_layout.addRow("Middle Name:", self.middle_name_input)
        
        # Last name
        self.last_name_input = QLineEdit()
        self.last_name_input.setMinimumHeight(35)
        basic_layout.addRow("Last Name:*", self.last_name_input)
        
        # Gender
        self.gender_combo = QComboBox()
        self.gender_combo.setMinimumHeight(35)
        self.gender_combo.addItems(["", "Male", "Female"])
        basic_layout.addRow("Gender:", self.gender_combo)
        
        # Date of birth
        self.dob_input = QDateEdit()
        self.dob_input.setMinimumHeight(35)
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate().addYears(-30))
        basic_layout.addRow("Date of Birth:", self.dob_input)
        
        # Date joined
        self.date_joined_input = QDateEdit()
        self.date_joined_input.setMinimumHeight(35)
        self.date_joined_input.setCalendarPopup(True)
        self.date_joined_input.setDate(QDate.currentDate())
        basic_layout.addRow("Date Joined:*", self.date_joined_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Contact Info
        contact_group = QGroupBox("Contact Information")
        contact_layout = QFormLayout()
        
        self.address_input = QTextEdit()
        self.address_input.setFixedHeight(80)
        contact_layout.addRow("Address:", self.address_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(35)
        contact_layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(35)
        contact_layout.addRow("Email:", self.email_input)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        # Employment Info
        emp_group = QGroupBox("Employment Information")
        emp_layout = QFormLayout()
        
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setMinimumHeight(35)
        emp_layout.addRow("Employee ID:", self.employee_id_input)
        
        self.grade_level_input = QLineEdit()
        self.grade_level_input.setMinimumHeight(35)
        emp_layout.addRow("Grade Level:", self.grade_level_input)
        
        emp_group.setLayout(emp_layout)
        layout.addWidget(emp_group)
        
        # Next of Kin 1
        nok1_group = QGroupBox("Next of Kin 1")
        nok1_layout = QFormLayout()
        
        self.nok1_name_input = QLineEdit()
        self.nok1_name_input.setMinimumHeight(35)
        nok1_layout.addRow("Name:", self.nok1_name_input)
        
        self.nok1_relationship_input = QLineEdit()
        self.nok1_relationship_input.setMinimumHeight(35)
        nok1_layout.addRow("Relationship:", self.nok1_relationship_input)
        
        self.nok1_address_input = QLineEdit()
        self.nok1_address_input.setMinimumHeight(35)
        nok1_layout.addRow("Address:", self.nok1_address_input)
        
        self.nok1_phone_input = QLineEdit()
        self.nok1_phone_input.setMinimumHeight(35)
        nok1_layout.addRow("Phone:", self.nok1_phone_input)
        
        nok1_group.setLayout(nok1_layout)
        layout.addWidget(nok1_group)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def load_member_data(self):
        """Load member data into form"""
        # Find station index
        for i in range(self.station_combo.count()):
            if self.station_combo.itemData(i) == self.member['station_id']:
                self.station_combo.setCurrentIndex(i)
                break
        
        self.first_name_input.setText(self.member['first_name'])
        self.middle_name_input.setText(self.member['middle_name'] or '')
        self.last_name_input.setText(self.member['last_name'])
        
        if self.member['gender']:
            self.gender_combo.setCurrentText(self.member['gender'])
        
        if self.member['date_of_birth']:
            self.dob_input.setDate(QDate.fromString(self.member['date_of_birth'], 'yyyy-MM-dd'))
        
        self.date_joined_input.setDate(QDate.fromString(self.member['date_joined'], 'yyyy-MM-dd'))
        self.address_input.setPlainText(self.member['address'] or '')
        self.phone_input.setText(self.member['phone_number'] or '')
        self.email_input.setText(self.member['email'] or '')
        self.employee_id_input.setText(self.member['employee_id'] or '')
        self.grade_level_input.setText(self.member['grade_level'] or '')
        
        self.nok1_name_input.setText(self.member['nok1_name'] or '')
        self.nok1_relationship_input.setText(self.member['nok1_relationship'] or '')
        self.nok1_address_input.setText(self.member['nok1_address'] or '')
        self.nok1_phone_input.setText(self.member['nok1_phone'] or '')
    
    def get_member_data(self):
        """Get member data from form"""
        # Validate
        if not self.first_name_input.text().strip():
            raise ValueError("First name is required")
        if not self.last_name_input.text().strip():
            raise ValueError("Last name is required")
        
        return {
            'station_id': self.station_combo.currentData(),
            'first_name': self.first_name_input.text().strip(),
            'middle_name': self.middle_name_input.text().strip() or None,
            'last_name': self.last_name_input.text().strip(),
            'gender': self.gender_combo.currentText() or None,
            'date_of_birth': self.dob_input.date().toString('yyyy-MM-dd'),
            'date_joined': self.date_joined_input.date().toString('yyyy-MM-dd'),
            'address': self.address_input.toPlainText().strip() or None,
            'phone_number': self.phone_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'employee_id': self.employee_id_input.text().strip() or None,
            'grade_level': self.grade_level_input.text().strip() or None,
            'nok1_name': self.nok1_name_input.text().strip() or None,
            'nok1_relationship': self.nok1_relationship_input.text().strip() or None,
            'nok1_address': self.nok1_address_input.text().strip() or None,
            'nok1_phone': self.nok1_phone_input.text().strip() or None,
        }


class MemberDetailsDialog(QDialog):
    """Dialog showing member details"""
    
    def __init__(self, db, member, parent=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        
        self.setWindowTitle(f"Member Details - {member['member_id']}")
        self.setMinimumSize(700, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Get member summary
        summary = self.db.get_member_summary(self.member['member_id'])
        if summary:
            summary = summary[0]
        
        # Format amounts safely outside f-string
        total_savings = f"{summary['total_savings']:,.2f}" if summary else '0.00'
        total_loans = f"{summary['total_loans_outstanding']:,.2f}" if summary else '0.00'
        net_balance = f"{summary['net_balance']:,.2f}" if summary else '0.00'
        
        info_text = f"""
        <h2>{summary['full_name'] if summary else ''}</h2>
        <p><b>Member ID:</b> {self.member['member_id']}</p>
        <p><b>Station:</b> {summary['station_name'] if summary else ''}</p>
        <p><b>Gender:</b> {self.member['gender'] or 'N/A'}</p>
        <p><b>Phone:</b> {self.member['phone_number'] or 'N/A'}</p>
        <p><b>Email:</b> {self.member['email'] or 'N/A'}</p>
        <p><b>Date Joined:</b> {self.member['date_joined']}</p>
        
        <h3>Account Summary</h3>
        <p><b>Total Savings:</b> ₦{total_savings}</p>
        <p><b>Total Loans Outstanding:</b> ₦{total_loans}</p>
        <p><b>Net Balance:</b> ₦{net_balance}</p>
        """
        
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class ChangeStatusDialog(QDialog):
    """Dialog for changing member status"""
    
    def __init__(self, db, member, parent=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        
        self.setWindowTitle(f"Change Status - {member['member_id']}")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Member info header
        member_name = f"{self.member['first_name']}"
        if self.member['middle_name']:
            member_name += f" {self.member['middle_name']}"
        member_name += f" {self.member['last_name']}"
        
        header = QLabel(f"<h2>Change Status for {member_name}</h2>")
        header.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(header)
        
        info = QLabel(f"<b>Member ID:</b> {self.member['member_id']}")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)
        
        # Current status
        if self.member['is_deceased']:
            current_status = "Deceased"
        elif self.member['is_active']:
            current_status = "Active"
        else:
            current_status = "Inactive"
        
        current_label = QLabel(f"<b>Current Status:</b> <span style='color: {'red' if current_status == 'Deceased' else ('green' if current_status == 'Active' else 'orange')};'>{current_status}</span>")
        current_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(current_label)
        
        # Status selection
        status_group = QGroupBox("New Status")
        status_layout = QVBoxLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(40)
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Inactive", "inactive")
        self.status_combo.addItem("Deceased", "deceased")
        
        # Set current status as default
        if self.member['is_deceased']:
            self.status_combo.setCurrentIndex(2)
        elif self.member['is_active']:
            self.status_combo.setCurrentIndex(0)
        else:
            self.status_combo.setCurrentIndex(1)
        
        self.status_combo.currentIndexChanged.connect(self.on_status_changed)
        status_layout.addWidget(self.status_combo)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Deceased date (only shown when Deceased is selected)
        self.deceased_group = QGroupBox("Deceased Date")
        deceased_layout = QFormLayout()
        
        self.deceased_date_input = QDateEdit()
        self.deceased_date_input.setMinimumHeight(40)
        self.deceased_date_input.setCalendarPopup(True)
        self.deceased_date_input.setDate(QDate.currentDate())
        
        if self.member['deceased_date']:
            self.deceased_date_input.setDate(
                QDate.fromString(self.member['deceased_date'], 'yyyy-MM-dd')
            )
        
        deceased_layout.addRow("Date:", self.deceased_date_input)
        self.deceased_group.setLayout(deceased_layout)
        layout.addWidget(self.deceased_group)
        
        # Initially hide deceased date if not deceased
        self.deceased_group.setVisible(self.member['is_deceased'])
        
        # Warning message
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: #E74C3C; padding: 10px; background-color: #3D1F1F; border-radius: 4px;")
        layout.addWidget(self.warning_label)
        self.update_warning()
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).setMinimumHeight(40)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setMinimumHeight(40)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_status_changed(self):
        """Handle status selection change"""
        status = self.status_combo.currentData()
        self.deceased_group.setVisible(status == "deceased")
        self.update_warning()
    
    def update_warning(self):
        """Update warning message based on selected status"""
        status = self.status_combo.currentData()
        
        if status == "deceased":
            self.warning_label.setText(
                "⚠️ WARNING: Marking a member as deceased is permanent and will:\n"
                "• Close all active accounts\n"
                "• Prevent any new transactions\n"
                "• Trigger death benefit processing (if enabled)"
            )
            self.warning_label.setVisible(True)
        elif status == "inactive":
            self.warning_label.setText(
                "ℹ️ Marking a member as inactive will:\n"
                "• Prevent new loans or savings accounts\n"
                "• Allow existing transactions to continue\n"
                "• Member can be reactivated later"
            )
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setVisible(False)
    
    def get_status_data(self):
        """Get status data from form"""
        status = self.status_combo.currentData()
        
        return {
            'is_active': 1 if status == "active" else 0,
            'is_deceased': 1 if status == "deceased" else 0,
            'deceased_date': self.deceased_date_input.date().toString('yyyy-MM-dd') if status == "deceased" else None
        }