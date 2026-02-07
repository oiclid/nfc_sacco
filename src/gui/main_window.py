"""
Main Window - Primary application interface
===========================================
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox,
    QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QIcon
from datetime import datetime

# Import modules - using relative imports from same directory
from .dashboard_module import DashboardModule
from .stations_module import StationsModule
from .members_module import MembersModule
from .savings_module import SavingsModule
from .loans_module import LoansModule
from .transactions_module import TransactionsModule
from .reports_module import ReportsModule
from .settings_module import SettingsModule



class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_user = app.current_user
        self.db = app.db_manager
        
        self.setup_ui()
        self.setup_menu()
        self.update_status_bar()
        
        # Update clock every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status_bar)
        self.timer.start(1000)
    
    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("NFC Cooperative Management System")
        
        # Get available screen geometry (excludes taskbar)
        screen = self.screen().availableGeometry()
        
        # Set reasonable minimum size
        self.setMinimumSize(1024, 600)
        
        # For larger screens, start maximized
        if screen.width() >= 1920 and screen.height() >= 1080:
            # Large screen - start maximized
            self.showMaximized()
        elif screen.width() >= 1366 and screen.height() >= 768:
            # Medium screen - use 90% of screen
            window_width = int(screen.width() * 0.90)
            window_height = int(screen.height() * 0.90)
            self.resize(window_width, window_height)
            # Center window
            x = (screen.width() - window_width) // 2
            y = (screen.height() - window_height) // 2
            self.move(screen.x() + x, screen.y() + y)
        else:
            # Smaller screen - use 95% of screen
            window_width = int(screen.width() * 0.95)
            window_height = int(screen.height() * 0.95)
            self.resize(window_width, window_height)
            # Center window
            x = (screen.width() - window_width) // 2
            y = (screen.height() - window_height) // 2
            self.move(screen.x() + x, screen.y() + y)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        
        # Sidebar navigation
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Main content area
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack, 1)
        
        main_layout.addLayout(content_layout, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Load modules
        self.load_modules()
    
    def create_header(self):
        """Create header bar"""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background-color: #2D2D32;
                border-bottom: 2px solid #2980B9;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title = QLabel("NFC Cooperative")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2980B9; border: none;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Management System")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #BDC3C7; border: none;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # User info
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        user_name = QLabel(f"👤 {self.current_user['username']}")
        user_name.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        user_name.setStyleSheet("color: #E6E6EB; border: none;")
        user_layout.addWidget(user_name)
        
        user_role = QLabel(f"Role: {self.current_user['role']}")
        user_role.setFont(QFont("Segoe UI", 9))
        user_role.setStyleSheet("color: #BDC3C7; border: none;")
        user_layout.addWidget(user_role)
        
        layout.addLayout(user_layout)
        
        return header
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2D2D32;
                border-right: 1px solid #3D3D42;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(5)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Define navigation items based on permissions
        nav_items = []
        
        # Dashboard (everyone can see)
        nav_items.append(("🏠 Dashboard", 0))

        # Stations (Maintain permission)
        if self.current_user['can_maintain']:
            nav_items.append(("🏢 Stations", 6))
        
        # Members (Maintain permission)
        if self.current_user['can_maintain']:
            nav_items.append(("👥 Members", 1))
        
        # Savings (Operate permission)
        if self.current_user['can_operate']:
            nav_items.append(("💰 Savings", 2))
            nav_items.append(("💳 Loans", 3))
            nav_items.append(("📊 Transactions", 4))
        
        # Reports (Reports permission)
        if self.current_user['can_view_reports']:
            nav_items.append(("📈 Reports", 5))
        
        # Settings (Maintain permission)
        if self.current_user['can_maintain']:
            nav_items.append(("⚙️ Settings", 7))
        
        # Create buttons
        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    color: #BDC3C7;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #3D3D42;
                    color: #E6E6EB;
                }
                QPushButton:checked {
                    background-color: #1E1E23;
                    border-left: 3px solid #2980B9;
                    color: #3498DB;
                    font-weight: 600;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self.switch_module(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setFixedHeight(50)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFont(QFont("Segoe UI", 11))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #C0392B;
                border: none;
                color: white;
                margin: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E74C3C;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def load_modules(self):
        """Load application modules"""
        # Create module instances
        self.modules = []
        
        # Dashboard module (always first, everyone can see)
        dashboard_module = DashboardModule(self.app, self)
        self.content_stack.addWidget(dashboard_module)
        self.modules.append(dashboard_module)
        
        # Members module
        if self.current_user['can_maintain']:
            members_module = MembersModule(self.app, self)
            self.content_stack.addWidget(members_module)
            self.modules.append(members_module)
        
        # Savings module
        if self.current_user['can_operate']:
            savings_module = SavingsModule(self.app, self)
            self.content_stack.addWidget(savings_module)
            self.modules.append(savings_module)
            
            # Loans module
            loans_module = LoansModule(self.app, self)
            self.content_stack.addWidget(loans_module)
            self.modules.append(loans_module)
            
            # Transactions module
            transactions_module = TransactionsModule(self.app, self)
            self.content_stack.addWidget(transactions_module)
            self.modules.append(transactions_module)
        
        # Reports module
        if self.current_user['can_view_reports']:
            reports_module = ReportsModule(self.app, self)
            self.content_stack.addWidget(reports_module)
            self.modules.append(reports_module)
        
        # Stations module
        if self.current_user['can_maintain']:
            stations_module = StationsModule(self.app, self)
            self.content_stack.addWidget(stations_module)
            self.modules.append(stations_module)
        
        # Settings module
        if self.current_user['can_maintain']:
            settings_module = SettingsModule(self.app, self)
            self.content_stack.addWidget(settings_module)
            self.modules.append(settings_module)
        
        # Activate first module (Dashboard)
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            self.content_stack.setCurrentIndex(0)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_module)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def switch_module(self, index):
        """Switch to a different module"""
        # Uncheck all other buttons
        for i, btn in enumerate(self.nav_buttons):
            if i != index:
                btn.setChecked(False)
        
        # Switch content
        self.content_stack.setCurrentIndex(index)
        
        # Refresh module
        if index < len(self.modules):
            module = self.modules[index]
            if hasattr(module, 'refresh'):
                module.refresh()
    
    @property
    def tabs(self):
        """Provide tabs interface for dashboard quick actions"""
        class TabsProxy:
            def __init__(self, main_window):
                self.main_window = main_window
            
            def setCurrentIndex(self, index):
                # Map tab indices to navigation buttons
                # Dashboard quick actions use old index system
                # Adjust for dashboard being first (index 0)
                adjusted_index = index + 1  # +1 because dashboard is now index 0
                
                # Find and activate the correct nav button
                if adjusted_index < len(self.main_window.nav_buttons):
                    self.main_window.nav_buttons[adjusted_index].click()
        
        return TabsProxy(self)
    
    def refresh_current_module(self):
        """Refresh current module"""
        index = self.content_stack.currentIndex()
        if index < len(self.modules):
            module = self.modules[index]
            if hasattr(module, 'refresh'):
                module.refresh()
    
    def update_status_bar(self):
        """Update status bar"""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%A, %B %d, %Y")
        
        self.status_bar.showMessage(
            f"  {date_str} | {time_str}  |  User: {self.current_user['username']} ({self.current_user['role']})"
        )
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from .login_window import LoginWindow
            self.app.login_window = LoginWindow(self.app)
            self.app.login_window.show()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About NFC Cooperative System",
            "<h2>NFC Cooperative Management System</h2>"
            "<p><b>Version:</b> 1.0.0</p>"
            "<p><b>Organization:</b> Nigerian Film Corporation</p>"
            "<p><b>Description:</b> Comprehensive cooperative management solution "
            "for savings, loans, and financial operations.</p>"
            "<p><b>Created:</b> February 2026</p>"
            "<hr>"
            "<p><small>© 2026 Nigerian Film Corporation. All rights reserved.</small></p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()