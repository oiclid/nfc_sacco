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
        
        # Stations table with expanded columns
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
        
        # Column widths - NO cramped columns, user can scroll horizontally if needed
        self.table.setColumnWidth(0, 120)   # Station ID
        self.table.setColumnWidth(1, 200)   # Station Name - EXPANDED
        self.table.setColumnWidth(2, 150)   # City
        self.table.setColumnWidth(3, 180)   # Contact Person
        self.table.setColumnWidth(4, 130)   # Phone
        self.table.setColumnWidth(5, 130)   # Total Members
        self.table.setColumnWidth(6, 130)   # Active Members
        self.table.setColumnWidth(7, 180)   # Total Savings Balance - EXPANDED
        self.table.setColumnWidth(8, 120)   # Total Loans - shows total amount owed
        self.table.setColumnWidth(9, 200)   # Actions - enough space for two buttons
        
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
        total_loans_amount = 0
        
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
            
            # Contact Person
            contact_item = QTableWidgetItem(station.get('contact_person') or 'N/A')
            contact_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 3, contact_item)
            
            # Phone
            phone_item = QTableWidgetItem(station.get('contact_phone') or 'N/A')
            phone_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row, 4, phone_item)
            
            # Total Members
            members_item = QTableWidgetItem(str(stats['total_members']))
            members_item.setFont(QFont("Segoe UI", 10))
            members_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, members_item)
            
            # Active Members
            active_item = QTableWidgetItem(str(stats['active_members']))
            active_item.setFont(QFont("Segoe UI", 10))
            active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, active_item)
            
            # Total Savings Balance - ONLY shows the balance
            savings_item = QTableWidgetItem(f"₦{stats['total_savings']:,.2f}")
            savings_item.setFont(QFont("Segoe UI", 10))
            savings_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 7, savings_item)
            
            # Total Loans - SHOWS TOTAL AMOUNT OWED BY STATION
            loans_item = QTableWidgetItem(f"₦{stats['total_loans_amount']:,.2f}")
            loans_item.setFont(QFont("Segoe UI", 10))
            loans_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 8, loans_item)
            
            # Actions - Two separate buttons that don't squash each other
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(8)
            
            # Edit Station button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setMinimumHeight(35)
            edit_btn.setMinimumWidth(90)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, s=station: self.edit_station(s))
            actions_layout.addWidget(edit_btn)
            
            # Delete Station button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setMinimumHeight(35)
            delete_btn.setMinimumWidth(100)
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
            delete_btn.clicked.connect(lambda checked, s=station, st=stats: self.delete_station(s, st))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
            
            # Add to totals
            total_members += stats['total_members']
            total_active_members += stats['active_members']
            total_savings += stats['total_savings']
            total_loans_amount += stats['total_loans_amount']
        
        # Update summary
        self.summary_label.setText(
            f"Total Stations: {len(stations)} | "
            f"Total Members: {total_members} (Active: {total_active_members}) | "
            f"Total Savings: ₦{total_savings:,.2f} | "
            f"Total Loans Owed: ₦{total_loans_amount:,.2f}"
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
        
        # Get total loans AMOUNT (what the station owes)
        loans_result = self.db.fetchone(
            """
            SELECT COALESCE(SUM(l.balance_outstanding), 0) as total_loans_amount
            FROM loans l
            JOIN members m ON l.member_id = m.member_id
            WHERE m.station_id = ? AND l.status = 'Active'
            """,
            (station_id,)
        )
        total_loans_amount = loans_result['total_loans_amount'] if loans_result else 0
        
        return {
            'total_members': total_members,
            'active_members': active_members,
            'total_savings': total_savings,
            'total_loans_amount': total_loans_amount
        }
    
    def view_station_details(self, station, stats):
        """Show detailed view of a station"""
        dialog = StationDetailsDialog(self.db, station, stats, parent=self)
        dialog.exec()
    
    def add_station(self):
        """Show add station dialog"""
        # Get the next sequential station ID
        existing_stations = self.db.fetchall(
            "SELECT station_id FROM stations ORDER BY station_id DESC LIMIT 1"
        )
        
        if existing_stations and existing_stations[0]['station_id']:
            # Get last station ID and increment
            last_id = existing_stations[0]['station_id']
            try:
                next_num = int(last_id) + 1
                next_id = f"{next_num:02d}"  # Format as 01, 02, etc.
            except ValueError:
                # If last ID is not numeric, start from 01
                next_id = "01"
        else:
            # No stations yet, start from 01
            next_id = "01"
        
        dialog = StationDialog(self.db, next_station_id=next_id, parent=self)
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
        """Show edit station dialog with warning"""
        # WARNING DIALOG before editing
        reply = QMessageBox.warning(
            self,
            "⚠️ Edit Station - Warning",
            f"You are about to edit station '{station['station_name']}'.\n\n"
            f"Station ID: {station['station_id']}\n"
            f"City: {station.get('city', 'N/A')}\n\n"
            "⚠️ CAUTION: Editing station information may affect all members at this station.\n\n"
            "Are you sure you want to proceed?",
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
        """Delete a station with confirmation and warnings"""
        # First check: Does station have members?
        if stats['total_members'] > 0:
            QMessageBox.critical(
                self,
                "❌ Cannot Delete Station",
                f"Station '{station['station_name']}' cannot be deleted because it has {stats['total_members']} member(s).\n\n"
                "⚠️ You must transfer or remove all members from this station before it can be deleted.\n\n"
                "This safety measure prevents accidental data loss.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # WARNING DIALOG - explaining the dangers
        reply = QMessageBox.warning(
            self,
            "⚠️ DANGER - Delete Station",
            f"⚠️ ⚠️ ⚠️ PERMANENT DELETION WARNING ⚠️ ⚠️ ⚠️\n\n"
            f"You are about to PERMANENTLY DELETE:\n"
            f"  • Station Name: {station['station_name']}\n"
            f"  • Station ID: {station['station_id']}\n"
            f"  • City: {station.get('city', 'N/A')}\n\n"
            f"⚠️ DANGERS OF PROCEEDING:\n"
            f"  • This action CANNOT be undone\n"
            f"  • All station data will be permanently lost\n"
            f"  • Historical records may be affected\n"
            f"  • Reports may show incomplete data\n\n"
            f"This is a destructive operation that should only be performed\n"
            f"if you are absolutely certain this station should be removed.\n\n"
            f"Are you ABSOLUTELY SURE you want to delete this station?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        # Only proceed if user explicitly says Yes
        if reply == QMessageBox.StandardButton.Yes:
            # Second confirmation - are you REALLY sure?
            final_reply = QMessageBox.critical(
                self,
                "🛑 FINAL CONFIRMATION",
                f"This is your LAST CHANCE to cancel.\n\n"
                f"Station '{station['station_name']}' will be PERMANENTLY DELETED.\n\n"
                f"Click YES only if you are 100% certain.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if final_reply == QMessageBox.StandardButton.Yes:
                try:
                    # Delete station from database
                    self.db.execute(
                        "DELETE FROM stations WHERE station_id = ?",
                        (station['station_id'],)
                    )
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Station '{station['station_name']}' has been deleted."
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
        
        loans_label = QLabel(f"₦{self.stats['total_loans_amount']:,.2f}")
        loans_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
        stats_layout.addRow("Total Loans Owed:", loans_label)
        
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
    
    def __init__(self, db, station=None, next_station_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.station = station
        self.next_station_id = next_station_id
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
        
        # City (moved to top for new stations)
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Lagos")
        if self.is_edit_mode:
            self.city_input.setText(self.station.get('city', ''))
        else:
            # Connect city input to auto-generate station name
            self.city_input.textChanged.connect(self.auto_generate_station_name)
        form_layout.addRow("City*:", self.city_input)
        
        # Station ID (auto-filled with next sequential ID)
        self.station_id_input = QLineEdit()
        self.station_id_input.setPlaceholderText("Auto-generated (01-99)")
        if self.is_edit_mode:
            self.station_id_input.setText(self.station['station_id'])
            self.station_id_input.setEnabled(False)
        else:
            # Auto-fill with next ID
            if self.next_station_id:
                self.station_id_input.setText(self.next_station_id)
            self.station_id_input.setEnabled(False)  # Make it read-only
        form_layout.addRow("Station ID*:", self.station_id_input)
        
        # Station Name (auto-generated as NFC-City)
        self.station_name_input = QLineEdit()
        self.station_name_input.setPlaceholderText("Auto-generated: NFC-[City]")
        if self.is_edit_mode:
            self.station_name_input.setText(self.station['station_name'])
        else:
            self.station_name_input.setEnabled(False)  # Auto-generated, read-only
        form_layout.addRow("Station Name*:", self.station_name_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter full address...")
        self.address_input.setMaximumHeight(80)
        if self.is_edit_mode:
            self.address_input.setPlainText(self.station.get('address', ''))
        form_layout.addRow("Address:", self.address_input)
        
        layout.addLayout(form_layout)
        
        # Note
        if self.is_edit_mode:
            note = QLabel("* Required fields")
        else:
            note = QLabel("* Station ID and Name are auto-generated. Just enter the City name.")
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
    
    def auto_generate_station_name(self, city_text):
        """Auto-generate station name as NFC-City when city is entered"""
        if not self.is_edit_mode and city_text.strip():
            station_name = f"NFC-{city_text.strip()}"
            self.station_name_input.setText(station_name)
    
    def validate_and_accept(self):
        """Validate inputs before accepting"""
        # Check required fields
        station_id = self.station_id_input.text().strip()
        
        # Validate station ID format (must be 01-99)
        if not station_id:
            QMessageBox.warning(self, "Validation Error", "Please enter a Station ID.")
            self.station_id_input.setFocus()
            return
        
        # Check if it's a valid 2-digit number
        try:
            id_num = int(station_id)
            if id_num < 1 or id_num > 99:
                QMessageBox.warning(
                    self, 
                    "Validation Error", 
                    "Station ID must be between 01 and 99."
                )
                self.station_id_input.setFocus()
                return
            # Ensure it's 2 digits with leading zero if needed
            self.station_id_input.setText(f"{id_num:02d}")
        except ValueError:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Station ID must be a number between 01 and 99."
            )
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