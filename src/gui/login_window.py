"""
Login Window - User authentication interface
============================================
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap


class LoginWindow(QWidget):
    """Login window"""
    
    login_successful = pyqtSignal(dict)  # Emits user data
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("NFC Cooperative - Login")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo/Title area
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        # Organization name
        org_label = QLabel("Nigerian Film Corporation")
        org_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        org_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        org_label.setStyleSheet("color: #2980B9;")
        title_layout.addWidget(org_label)
        
        # System name
        system_label = QLabel("Cooperative Management System")
        system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_layout.addWidget(system_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #7F8C8D;")
        title_layout.addWidget(version_label)
        
        layout.addLayout(title_layout)
        layout.addSpacing(30)
        
        # Login form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        form_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        self.username_input.returnPressed.connect(self.on_login)
        form_layout.addWidget(self.username_input)
        
        form_layout.addSpacing(10)
        
        # Password
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.returnPressed.connect(self.on_login)
        form_layout.addWidget(self.password_input)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Login button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setFixedHeight(45)
        self.login_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        layout.addWidget(self.login_button)
        
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2026 Nigerian Film Corporation. All rights reserved.")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #7F8C8D; font-size: 9pt;")
        layout.addWidget(footer_label)
        
        self.setLayout(layout)
        
        # Set focus
        self.username_input.setFocus()
    
    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username or not password:
            QMessageBox.warning(
                self,
                "Login Failed",
                "Please enter both username and password."
            )
            return
        
        # Authenticate
        try:
            user = self.app.db_manager.authenticate_user(username, password)
            
            if user:
                self.login_successful.emit(user)
            else:
                QMessageBox.warning(
                    self,
                    "Login Failed",
                    "Invalid username or password.\nPlease try again."
                )
                self.password_input.clear()
                self.password_input.setFocus()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Login Error",
                f"An error occurred during login:\n{str(e)}"
            )
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
