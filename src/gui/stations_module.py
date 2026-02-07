"""
Stations Module - Station management and overview
================================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QGroupBox,
    QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime


class StationsModule(QWidget):
    """Stations overview and management module"""
    
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
        
        title = QLabel("Stations Overview")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add station button
        add_btn = QPushButton("➕ Add Station")
        add_btn.setMinimumHeight(40)
        add_btn.setMinimumWidth(140)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_station)
        header_layout.addWidget(add_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setMinimumWidth(120)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Stations table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Station ID", 
            "Station Name", 
            "City",
            "Contact Person",
            "Phone",
            "Total Members",
            "Active Members",
            "Total Savings Balance",
            "Total Loans",
            "Actions"
        ])
        
        # Table settings
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Enable scrollbars
        self.table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Station ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Station Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # City
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Contact Person
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Phone
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Total Members
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Active Members
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Total Savings
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Total Loans
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)  # Actions
        
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 130)
        self.table.setColumnWidth(7, 180)
        self.table.setColumnWidth(8, 120)
        self.table.setColumnWidth(9, 160)
        
        layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #7F8C8D; font-size: 11pt; padding: 5px;")
        self.summary_label.setMinimumHeight(30)
        layout.addWidget(self.summary_label)
    
    def refresh(self):
        """Refresh stations list with summaries"""
        # Temporarily disable sorting while populating
        self.table.setSortingEnabled(False)
        
        stations = self.db.get_all_stations(enabled_only=False)
        self.populate_table(stations)
        
        # Re-enable sorting after populating
        self.table.setSortingEnabled(True)
    
    def populate_table(self, stations):
        """Populate table with stations and their summaries"""
        self.table.setRowCount(0)
        
        total_members = 0
        total_active_members = 0
        total_savings = 0
        total_loans = 0
        
        for station in stations:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            station_id = station['station_id']
            
            # Get station statistics
            stats = self._get_station_stats(station_id)
            
            # Station ID
            id_item = QTableWidgetItem(station_id)
            id_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, id_item)
            
            # Station Name
            name_item = QTableWidgetItem(station['station_name'])
            name_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 1, name_item)
            
            # City
            city_item = QTableWidgetItem(station.get('city', ''))
            city_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 2, city_item)
            
            # Total Members
            members_item = QTableWidgetItem(str(stats['total_members']))
            members_item.setFont(QFont("Segoe UI", 10))
            members_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, members_item)
            
            # Active Members
            active_item = QTableWidgetItem(str(stats['active_members']))
            active_item.setFont(QFont("Segoe UI", 10))
            active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, active_item)
            
            # Total Savings Balance
            savings_item = QTableWidgetItem(f"₦{stats['total_savings']:,.2f}")
            savings_item.setFont(QFont("Segoe UI", 10))
            savings_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, savings_item)
            
            # Total Loans
            loans_item = QTableWidgetItem(str(stats['total_loans']))
            loans_item.setFont(QFont("Segoe UI", 10))
            loans_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, loans_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("View Details")
            view_btn.setMinimumHeight(35)
            view_btn.setMinimumWidth(40)
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.clicked.connect(lambda checked, s=station, st=stats: self.view_station_details(s, st))
            actions_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit Station")
            edit_btn.setMinimumHeight(35)
            edit_btn.setMinimumWidth(40)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, s=station: self.edit_station(s))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete Station")
            delete_btn.setMinimumHeight(35)
            delete_btn.setMinimumWidth(40)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
            delete_btn.clicked.connect(lambda checked, s=station, st=stats: self.delete_station(s, st))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 7, actions_widget)
            
            # Add to totals
            total_members += stats['total_members']
            total_active_members += stats['active_members']
            total_savings += stats['total_savings']
            total_loans += stats['total_loans']
        
        # Update summary
        self.summary_label.setText(
            f"Total Stations: {len(stations)} | "
            f"Total Members: {total_members} (Active: {total_active_members}) | "
            f"Total Savings: ₦{total_savings:,.2f} | "
            f"Total Loans: {total_loans}"
        )
    
    def _get_station_stats(self, station_id):
        """Get statistics for a station"""
        # Get member counts
        members = self.db.fetchall(
            "SELECT is_active FROM members WHERE station_id = ?",
            (station_id,)
        )
        total_members = len(members)
        active_members = sum(1 for m in members if m['is_active'])
        
        # Get total savings balance
        savings_result = self.db.fetchone(
            """
            SELECT COALESCE(SUM(sa.current_balance), 0) as total_savings
            FROM savings_accounts sa
            JOIN members m ON sa.member_id = m.member_id
            WHERE m.station_id = ?
            """,
            (station_id,)
        )
        total_savings = savings_result['total_savings'] if savings_result else 0
        
        # Get total loans count
        loans_result = self.db.fetchone(
            """
            SELECT COUNT(*) as total_loans
            FROM loans l
            JOIN members m ON l.member_id = m.member_id
            WHERE m.station_id = ?
            """,
            (station_id,)
        )
        total_loans = loans_result['total_loans'] if loans_result else 0
        
        return {
            'total_members': total_members,
            'active_members': active_members,
            'total_savings': total_savings,
            'total_loans': total_loans
        }
    
    def view_station_details(self, station, stats):
        """Show detailed view of a station"""
        dialog = StationDetailsDialog(self.db, station, stats, parent=self)
        dialog.exec()
    
    def add_station(self):
        """Show add station dialog"""
        dialog = StationDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                station_data = dialog.get_station_data()
                
                # Add station to database
                self.db.execute(
                    """
                    INSERT INTO stations (station_id, station_name, city, address, enabled)
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    (
                        station_data['station_id'],
                        station_data['station_name'],
                        station_data['city'],
                        station_data['address']
                    )
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Station '{station_data['station_name']}' added successfully!"
                )
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add station:\n{str(e)}"
                )
    
    def edit_station(self, station):
        """Show edit station dialog"""
        # Warning dialog before editing
        reply = QMessageBox.question(
            self,
            "Edit Station",
            f"Do you want to edit station '{station['station_name']}'?\n\n"
            "This will update the station's information.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        dialog = StationDialog(self.db, station, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                station_data = dialog.get_station_data()
                
                # Update station in database
                self.db.execute(
                    """
                    UPDATE stations
                    SET station_name = ?, city = ?, address = ?
                    WHERE station_id = ?
                    """,
                    (
                        station_data['station_name'],
                        station_data['city'],
                        station_data['address'],
                        station['station_id']
                    )
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    "Station updated successfully!"
                )
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update station:\n{str(e)}"
                )
    
    def delete_station(self, station, stats):
        """Delete a station with confirmation"""
        # Check if station has members
        if stats['total_members'] > 0:
            QMessageBox.warning(
                self,
                "Cannot Delete Station",
                f"Station '{station['station_name']}' cannot be deleted because it has {stats['total_members']} member(s).\n\n"
                "Please transfer or remove all members before deleting this station."
            )
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete station '{station['station_name']}'?\n\n"
            f"Station ID: {station['station_id']}\n"
            f"City: {station.get('city', 'N/A')}\n\n"
            "⚠️ This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete station from database
                self.db.execute(
                    "DELETE FROM stations WHERE station_id = ?",
                    (station['station_id'],)
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Station '{station['station_name']}' deleted successfully!"
                )
                self.refresh()
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete station:\n{str(e)}"
                )


class StationDetailsDialog(QDialog):
    """Dialog showing detailed station information"""
    
    def __init__(self, db, station, stats, parent=None):
        super().__init__(parent)
        self.db = db
        self.station = station
        self.stats = stats
        self.setWindowTitle(f"Station Details - {station['station_name']}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel(f"{self.station['station_name']}")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        basic_layout.setSpacing(10)
        
        basic_layout.addRow("Station ID:", QLabel(self.station['station_id']))
        basic_layout.addRow("Station Name:", QLabel(self.station['station_name']))
        basic_layout.addRow("City:", QLabel(self.station.get('city', 'N/A')))
        basic_layout.addRow("Address:", QLabel(self.station.get('address', 'N/A')))
        
        status = "Enabled" if self.station.get('enabled', 1) else "Disabled"
        status_label = QLabel(status)
        status_label.setStyleSheet(f"color: {'green' if self.station.get('enabled', 1) else 'red'}; font-weight: bold;")
        basic_layout.addRow("Status:", status_label)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Statistics Group
        stats_group = QGroupBox("Station Statistics")
        stats_layout = QFormLayout()
        stats_layout.setSpacing(10)
        
        stats_layout.addRow("Total Members:", QLabel(str(self.stats['total_members'])))
        stats_layout.addRow("Active Members:", QLabel(str(self.stats['active_members'])))
        
        inactive_members = self.stats['total_members'] - self.stats['active_members']
        stats_layout.addRow("Inactive Members:", QLabel(str(inactive_members)))
        
        savings_label = QLabel(f"₦{self.stats['total_savings']:,.2f}")
        savings_label.setStyleSheet("font-weight: bold; color: #27AE60;")
        stats_layout.addRow("Total Savings Balance:", savings_label)
        
        stats_layout.addRow("Total Loans:", QLabel(str(self.stats['total_loans'])))
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Members List
        members_group = QGroupBox("Members at This Station")
        members_layout = QVBoxLayout()
        
        members_table = QTableWidget()
        members_table.setColumnCount(5)
        members_table.setHorizontalHeaderLabels([
            "Member ID", "Name", "Phone", "Date Joined", "Status"
        ])
        members_table.horizontalHeader().setStretchLastSection(True)
        members_table.setMinimumHeight(250)
        
        # Enable sorting
        members_table.setSortingEnabled(True)
        
        # Get members for this station
        members = self.db.fetchall(
            "SELECT * FROM members WHERE station_id = ? ORDER BY member_id",
            (self.station['station_id'],)
        )
        
        # Temporarily disable sorting while populating
        members_table.setSortingEnabled(False)
        
        members_table.setRowCount(len(members))
        for row, member in enumerate(members):
            # Member ID
            members_table.setItem(row, 0, QTableWidgetItem(member['member_id']))
            
            # Name
            full_name = f"{member['first_name']} {member.get('middle_name', '')} {member['last_name']}".strip()
            members_table.setItem(row, 1, QTableWidgetItem(full_name))
            
            # Phone
            members_table.setItem(row, 2, QTableWidgetItem(member.get('phone_number', '')))
            
            # Date Joined
            members_table.setItem(row, 3, QTableWidgetItem(member.get('date_joined', '')))
            
            # Status
            if member['is_deceased']:
                status = "Deceased"
            elif member['is_active']:
                status = "Active"
            else:
                status = "Inactive"
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(
                Qt.GlobalColor.red if status == "Deceased" else 
                (Qt.GlobalColor.darkGreen if status == "Active" else Qt.GlobalColor.darkYellow)
            )
            members_table.setItem(row, 4, status_item)
        
        # Re-enable sorting
        members_table.setSortingEnabled(True)
        
        members_layout.addWidget(members_table)
        members_group.setLayout(members_layout)
        layout.addWidget(members_group)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class StationDialog(QDialog):
    """Dialog for adding/editing stations"""
    
    def __init__(self, db, station=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.station = station
        self.is_edit_mode = station is not None
        
        title = "Edit Station" if self.is_edit_mode else "Add New Station"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Station ID (disabled in edit mode)
        self.station_id_input = QLineEdit()
        self.station_id_input.setPlaceholderText("e.g., NFC-JOS")
        if self.is_edit_mode:
            self.station_id_input.setText(self.station['station_id'])
            self.station_id_input.setEnabled(False)
        form_layout.addRow("Station ID*:", self.station_id_input)
        
        # Station Name
        self.station_name_input = QLineEdit()
        self.station_name_input.setPlaceholderText("e.g., Jos Station")
        if self.is_edit_mode:
            self.station_name_input.setText(self.station['station_name'])
        form_layout.addRow("Station Name*:", self.station_name_input)
        
        # City
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Jos")
        if self.is_edit_mode:
            self.city_input.setText(self.station.get('city', ''))
        form_layout.addRow("City*:", self.city_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter full address...")
        self.address_input.setMaximumHeight(80)
        if self.is_edit_mode:
            self.address_input.setPlainText(self.station.get('address', ''))
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Note
        note = QLabel("* Required fields")
        note.setStyleSheet("color: #E67E22; font-size: 9pt; font-style: italic;")
        layout.addWidget(note)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def validate_and_accept(self):
        """Validate inputs before accepting"""
        # Check required fields
        if not self.station_id_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Station ID.")
            self.station_id_input.setFocus()
            return
        
        if not self.station_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Station Name.")
            self.station_name_input.setFocus()
            return
        
        if not self.city_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a City.")
            self.city_input.setFocus()
            return
        
        # Check for duplicate station ID (only in add mode)
        if not self.is_edit_mode:
            existing = self.db.fetchone(
                "SELECT station_id FROM stations WHERE station_id = ?",
                (self.station_id_input.text().strip(),)
            )
            if existing:
                QMessageBox.warning(
                    self,
                    "Duplicate Station ID",
                    f"Station ID '{self.station_id_input.text().strip()}' already exists.\n"
                    "Please use a different Station ID."
                )
                self.station_id_input.setFocus()
                return
        
        self.accept()
    
    def get_station_data(self):
        """Get station data from form"""
        return {
            'station_id': self.station_id_input.text().strip(),
            'station_name': self.station_name_input.text().strip(),
            'city': self.city_input.text().strip(),
            'address': self.address_input.toPlainText().strip()
        }
