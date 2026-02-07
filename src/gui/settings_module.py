"""
Settings Module - System configuration
======================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QDoubleSpinBox, QCheckBox,
    QMessageBox, QSpinBox
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt


class SettingsModule(QWidget):
    """System settings module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("System Settings")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setFixedHeight(35)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)
        header_layout.addWidget(save_btn)
        
        layout.addLayout(header_layout)
        
        # Organization Info
        org_group = QGroupBox("Organization Information")
        org_layout = QFormLayout()
        
        self.org_name_input = QLineEdit()
        org_layout.addRow("Organization Name:", self.org_name_input)
        
        self.currency_input = QLineEdit()
        org_layout.addRow("Currency Symbol:", self.currency_input)
        
        org_group.setLayout(org_layout)
        layout.addWidget(org_group)
        
        # Interest Settings
        interest_group = QGroupBox("Interest Calculation")
        interest_layout = QFormLayout()
        
        self.interest_auto_check = QCheckBox("Enable automatic monthly interest calculation")
        interest_layout.addRow("", self.interest_auto_check)
        
        interest_group.setLayout(interest_layout)
        layout.addWidget(interest_group)
        
        # Death Benefit Settings
        death_group = QGroupBox("Death Benefit Settings")
        death_layout = QFormLayout()
        
        self.death_enabled_check = QCheckBox("Enable death benefit system")
        death_layout.addRow("", self.death_enabled_check)
        
        self.death_amount_input = QDoubleSpinBox()
        self.death_amount_input.setRange(0, 1000000)
        self.death_amount_input.setDecimals(2)
        self.death_amount_input.setPrefix("₦ ")
        death_layout.addRow("Charge per member:", self.death_amount_input)
        
        death_group.setLayout(death_layout)
        layout.addWidget(death_group)
        
        # Withdrawal Benefits
        withdrawal_group = QGroupBox("Withdrawal Benefit Settings")
        withdrawal_layout = QFormLayout()
        
        self.retirement_benefit_input = QDoubleSpinBox()
        self.retirement_benefit_input.setRange(0, 100)
        self.retirement_benefit_input.setDecimals(2)
        self.retirement_benefit_input.setSuffix(" %")
        withdrawal_layout.addRow("Retirement benefit:", self.retirement_benefit_input)
        
        self.non_retirement_charge_input = QDoubleSpinBox()
        self.non_retirement_charge_input.setRange(0, 100)
        self.non_retirement_charge_input.setDecimals(2)
        self.non_retirement_charge_input.setSuffix(" %")
        withdrawal_layout.addRow("Non-retirement charge:", self.non_retirement_charge_input)
        
        withdrawal_group.setLayout(withdrawal_layout)
        layout.addWidget(withdrawal_group)
        
        # ID Generation
        id_group = QGroupBox("ID Generation")
        id_layout = QFormLayout()
        
        self.next_member_input = QSpinBox()
        self.next_member_input.setRange(1, 999999)
        id_layout.addRow("Next Member Number:", self.next_member_input)
        
        self.next_station_input = QSpinBox()
        self.next_station_input.setRange(1, 999)
        id_layout.addRow("Next Station Number:", self.next_station_input)
        
        id_group.setLayout(id_layout)
        layout.addWidget(id_group)
        
        layout.addStretch()
    
    def refresh(self):
        """Refresh settings"""
        self.load_settings()
    
    def load_settings(self):
        """Load settings from database"""
        # Organization
        org_name = self.db.get_setting('organization_name')
        currency = self.db.get_setting('currency_symbol')
        
        self.org_name_input.setText(org_name or '')
        self.currency_input.setText(currency or '₦')
        
        # Interest
        interest_auto = self.db.get_setting('interest_auto_calculate')
        self.interest_auto_check.setChecked(interest_auto == '1')
        
        # Death benefit
        death_enabled = self.db.get_setting('death_benefit_enabled')
        death_amount = self.db.get_setting('death_benefit_amount')
        
        self.death_enabled_check.setChecked(death_enabled == '1')
        self.death_amount_input.setValue(float(death_amount or 0))
        
        # Withdrawal
        retirement_pct = self.db.get_setting('retirement_benefit_percentage')
        non_retirement_pct = self.db.get_setting('non_retirement_charge_percentage')
        
        self.retirement_benefit_input.setValue(float(retirement_pct or 0))
        self.non_retirement_charge_input.setValue(float(non_retirement_pct or 0))
        
        # ID Generation
        next_member = self.db.get_setting('next_member_number')
        next_station = self.db.get_setting('next_station_number')
        
        self.next_member_input.setValue(int(next_member or 1))
        self.next_station_input.setValue(int(next_station or 1))
    
    def save_settings(self):
        """Save settings to database"""
        try:
            username = self.app.current_user['username']
            
            # Organization
            self.db.update_setting('organization_name', self.org_name_input.text(), username)
            self.db.update_setting('currency_symbol', self.currency_input.text(), username)
            
            # Interest
            self.db.update_setting(
                'interest_auto_calculate',
                '1' if self.interest_auto_check.isChecked() else '0',
                username
            )
            
            # Death benefit
            self.db.update_setting(
                'death_benefit_enabled',
                '1' if self.death_enabled_check.isChecked() else '0',
                username
            )
            self.db.update_setting(
                'death_benefit_amount',
                str(self.death_amount_input.value()),
                username
            )
            
            # Withdrawal
            self.db.update_setting(
                'retirement_benefit_percentage',
                str(self.retirement_benefit_input.value()),
                username
            )
            self.db.update_setting(
                'non_retirement_charge_percentage',
                str(self.non_retirement_charge_input.value()),
                username
            )
            
            # ID Generation
            self.db.update_setting(
                'next_member_number',
                str(self.next_member_input.value()),
                username
            )
            self.db.update_setting(
                'next_station_number',
                str(self.next_station_input.value()),
                username
            )
            
            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings:\n{str(e)}"
            )
