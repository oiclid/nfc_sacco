#!/usr/bin/env python3
"""
NFC Cooperative Management System - Main Application
====================================================
Desktop application for managing cooperative operations.

Author: oïclid
Date: December 2026
Version: 1.1.8
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from database.db_manager import DatabaseManager

class NFCCooperativeApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName("NFC Cooperative Management System")
        self.setOrganizationName("Nigerian Film Corporation")
        self.setApplicationVersion("1.0.0")
        
        # Set application style
        self.setStyle("Fusion")
        self.setup_theme()
        
        # Initialize database
        self.db_manager = None
        self.init_database()
        
        # Current user
        self.current_user = None
        
        # Show login window
        self.login_window = LoginWindow(self)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
        
    def setup_theme(self):
        """Setup application theme and colors"""
        # Create dark palette
        palette = QPalette()
        
        # Define colors
        dark_bg = QColor(30, 30, 35)
        darker_bg = QColor(20, 20, 25)
        light_bg = QColor(45, 45, 50)
        text_color = QColor(230, 230, 235)
        accent_color = QColor(41, 128, 185)  # Professional blue
        hover_color = QColor(52, 152, 219)
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, dark_bg)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, darker_bg)
        palette.setColor(QPalette.ColorRole.AlternateBase, light_bg)
        palette.setColor(QPalette.ColorRole.ToolTipBase, darker_bg)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, light_bg)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Link, accent_color)
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        self.setPalette(palette)
        
        # Set default font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Set stylesheet for additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E23;
            }
            
            QPushButton {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 8px 16px;
                color: #E6E6EB;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #3498DB;
                border-color: #3498DB;
            }
            
            QPushButton:pressed {
                background-color: #2980B9;
            }
            
            QPushButton:disabled {
                background-color: #252529;
                color: #606066;
                border-color: #303035;
            }
            
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #14141A;
                border: 1px solid #3D3D42;
                border-radius: 4px;
                padding: 6px;
                color: #E6E6EB;
            }
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #2980B9;
            }
            
            QTableWidget {
                background-color: #14141A;
                alternate-background-color: #1A1A20;
                border: 1px solid #3D3D42;
                gridline-color: #3D3D42;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #2980B9;
            }
            
            QHeaderView::section {
                background-color: #2D2D32;
                padding: 8px;
                border: none;
                border-right: 1px solid #3D3D42;
                border-bottom: 1px solid #3D3D42;
                font-weight: 600;
            }
            
            QTabWidget::pane {
                border: 1px solid #3D3D42;
                background-color: #1E1E23;
            }
            
            QTabBar::tab {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #1E1E23;
                border-bottom: 2px solid #2980B9;
            }
            
            QTabBar::tab:hover {
                background-color: #3D3D42;
            }
            
            QMenuBar {
                background-color: #2D2D32;
                border-bottom: 1px solid #3D3D42;
            }
            
            QMenuBar::item {
                padding: 8px 12px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #3D3D42;
            }
            
            QMenu {
                background-color: #2D2D32;
                border: 1px solid #3D3D42;
            }
            
            QMenu::item {
                padding: 8px 24px;
            }
            
            QMenu::item:selected {
                background-color: #2980B9;
            }
            
            QStatusBar {
                background-color: #2D2D32;
                border-top: 1px solid #3D3D42;
            }
            
            QGroupBox {
                border: 1px solid #3D3D42;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: 600;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #1E1E23;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3D3D42;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #4D4D52;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QMessageBox {
                background-color: #1E1E23;
            }
        """)
    
    def init_database(self):
        """Initialize database connection"""
        try:
            db_path = os.path.join(
                os.path.dirname(__file__), 
                'data', 
                'nfc_cooperative.db'
            )
            
            if not os.path.exists(db_path):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    None,
                    "Database Error",
                    f"Database not found at:\n{db_path}\n\n"
                    "Please run the migration script first:\n"
                    "python migrations/migrate.py"
                )
                sys.exit(1)
            
            self.db_manager = DatabaseManager(db_path)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to initialize database:\n{str(e)}"
            )
            sys.exit(1)
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        
        # Close login window
        self.login_window.close()
        
        # Show main window
        self.main_window = MainWindow(self)
        self.main_window.show()


def main():
    """Application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = NFCCooperativeApp(sys.argv)
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
