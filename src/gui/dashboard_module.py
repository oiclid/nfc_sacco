"""
Dashboard Module - Home/Landing Page
=====================================
Overview dashboard with metrics, charts, and quick actions
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QGroupBox, QComboBox, QFrame, QScrollArea,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSet, QBarSeries,
    QBarCategoryAxis, QValueAxis, QLineSeries
)
from datetime import datetime, timedelta
from decimal import Decimal


class DashboardModule(QWidget):
    """Dashboard/Home page module"""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db_manager
        self.current_user = app.current_user
        
        # View mode: 'numbers', 'charts', 'graphs'
        self.view_mode = 'numbers'
        
        self.setup_ui()
        self.refresh_data()
        
        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # 30 seconds
    
    def setup_ui(self):
        """Setup user interface"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with view mode selector
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Last updated label
        self.last_updated_label = QLabel()
        self.last_updated_label.setStyleSheet("color: #7F8C8D; font-size: 10pt;")
        header_layout.addWidget(self.last_updated_label)
        
        # View mode selector
        view_label = QLabel("View Mode:")
        view_label.setStyleSheet("font-size: 11pt; margin-right: 5px;")
        header_layout.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.setMinimumHeight(40)
        self.view_combo.setMinimumWidth(150)
        self.view_combo.addItem("📊 Numbers", "numbers")
        self.view_combo.addItem("📈 Charts", "charts")
        self.view_combo.addItem("📉 Graphs", "graphs")
        self.view_combo.currentIndexChanged.connect(self.change_view_mode)
        header_layout.addWidget(self.view_combo)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setMinimumWidth(120)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Key metrics section
        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout(self.metrics_container)
        self.metrics_layout.setSpacing(15)
        layout.addWidget(self.metrics_container)
        
        # Main content area (charts/graphs)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setSpacing(20)
        layout.addWidget(self.content_container)
        
        # Quick actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        quick_actions = [
            ("➕ New Member", "members"),
            ("💰 Deposit", "savings"),
            ("💳 Loan", "loans"),
            ("📄 Report", "reports"),
            ("⚙️ Settings", "settings")
        ]
        
        for label, module in quick_actions:
            btn = QPushButton(label)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(150)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #3498DB;
                }
            """)
            # Connect to parent window's module switching
            btn.clicked.connect(lambda checked, m=module: self.switch_to_module(m))
            actions_layout.addWidget(btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def switch_to_module(self, module_name):
        """Switch to a different module"""
        # Get the main window and switch tabs
        main_window = self.parent()
        if hasattr(main_window, 'tabs'):
            tab_map = {
                'members': 0,
                'savings': 1,
                'loans': 2,
                'transactions': 3,
                'reports': 4,
                'settings': 5
            }
            if module_name in tab_map:
                main_window.tabs.setCurrentIndex(tab_map[module_name])
    
    def create_metric_card(self, title, value, subtitle="", color="#2980B9"):
        """Create a metric card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #2D2D32;
                border-left: 4px solid {color};
                border-radius: 6px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: #BDC3C7; font-size: 11pt; font-weight: 500;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24pt; font-weight: bold;")
        layout.addWidget(value_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #7F8C8D; font-size: 9pt;")
            layout.addWidget(subtitle_label)
        
        return card
    
    def change_view_mode(self):
        """Change view mode between numbers, charts, and graphs"""
        self.view_mode = self.view_combo.currentData()
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # Update timestamp
        self.last_updated_label.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        # Get statistics
        stats = self.get_statistics()
        
        # Clear existing metrics
        while self.metrics_layout.count():
            item = self.metrics_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create metric cards based on view mode
        if self.view_mode == 'numbers':
            self.show_numbers_view(stats)
        elif self.view_mode == 'charts':
            self.show_charts_view(stats)
        else:  # graphs
            self.show_graphs_view(stats)
    
    def get_statistics(self):
        """Get all statistics for dashboard"""
        stats = {}
        
        # Members statistics
        members = self.db.fetchall("SELECT is_active, is_deceased FROM members")
        stats['total_members'] = len(members)
        stats['active_members'] = sum(1 for m in members if m['is_active'] and not m['is_deceased'])
        stats['inactive_members'] = sum(1 for m in members if not m['is_active'] and not m['is_deceased'])
        stats['deceased_members'] = sum(1 for m in members if m['is_deceased'])
        
        # Savings statistics
        savings = self.db.fetchall("""
            SELECT sa.current_balance, st.type_name
            FROM savings_accounts sa
            JOIN savings_types st ON sa.savings_type_id = st.savings_type_id
        """)
        stats['total_savings'] = sum(Decimal(str(s['current_balance'])) for s in savings)
        stats['savings_accounts'] = len(savings)
        
        # Savings by type
        stats['savings_by_type'] = {}
        for saving in savings:
            type_name = saving['type_name']
            if type_name not in stats['savings_by_type']:
                stats['savings_by_type'][type_name] = Decimal('0')
            stats['savings_by_type'][type_name] += Decimal(str(saving['current_balance']))
        
        # Loans statistics
        loans = self.db.fetchall("""
            SELECT principal_amount, interest_amount, amount_paid, balance_outstanding, status
            FROM loans
        """)
        stats['total_loans'] = len(loans)
        stats['active_loans'] = sum(1 for l in loans if l['status'] == 'Active')
        stats['completed_loans'] = sum(1 for l in loans if l['status'] == 'Completed')
        
        total_disbursed = sum(Decimal(str(l['principal_amount'])) for l in loans)
        total_outstanding = sum(
            Decimal(str(l['balance_outstanding']))
            for l in loans if l['status'] == 'Active'
        )
        total_paid = sum(Decimal(str(l['amount_paid'])) for l in loans)
        
        stats['loans_disbursed'] = total_disbursed
        stats['loans_outstanding'] = total_outstanding
        stats['loans_collected'] = total_paid
        
        # Transactions (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        transactions = self.db.fetchall("""
            SELECT transaction_type, amount, transaction_date
            FROM transactions
            WHERE transaction_date >= ?
        """, (thirty_days_ago,))
        
        stats['transactions_30days'] = len(transactions)
        stats['deposits_30days'] = sum(
            Decimal(str(t['amount'])) for t in transactions 
            if t['transaction_type'] == 'Deposit'
        )
        stats['withdrawals_30days'] = sum(
            Decimal(str(t['amount'])) for t in transactions 
            if t['transaction_type'] == 'Withdrawal'
        )
        
        # Daily transactions for last 7 days
        stats['daily_transactions'] = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            day_name = (datetime.now() - timedelta(days=i)).strftime('%a')
            count = sum(1 for t in transactions if t['transaction_date'].startswith(date))
            stats['daily_transactions'][day_name] = count
        
        return stats
    
    def show_numbers_view(self, stats):
        """Show metrics as numbers"""
        # Row 0: Member metrics
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Members",
                f"{stats['total_members']:,}",
                f"Active: {stats['active_members']:,} | Inactive: {stats['inactive_members']:,}",
                "#27AE60"
            ), 0, 0
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Active Members",
                f"{stats['active_members']:,}",
                f"{(stats['active_members']/max(stats['total_members'],1)*100):.1f}% of total",
                "#2ECC71"
            ), 0, 1
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Savings Accounts",
                f"{stats['savings_accounts']:,}",
                f"Average: ₦{(stats['total_savings']/max(stats['savings_accounts'],1)):,.0f}",
                "#3498DB"
            ), 0, 2
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Savings",
                f"₦{stats['total_savings']:,.2f}",
                "All savings types",
                "#1ABC9C"
            ), 0, 3
        )
        
        # Row 1: Loan metrics
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Loans",
                f"{stats['total_loans']:,}",
                f"Active: {stats['active_loans']:,} | Completed: {stats['completed_loans']:,}",
                "#E67E22"
            ), 1, 0
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Loans Disbursed",
                f"₦{stats['loans_disbursed']:,.2f}",
                "Total principal amount",
                "#D35400"
            ), 1, 1
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Outstanding Balance",
                f"₦{stats['loans_outstanding']:,.2f}",
                "Amount to be collected",
                "#E74C3C"
            ), 1, 2
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Collected Amount",
                f"₦{stats['loans_collected']:,.2f}",
                f"{(stats['loans_collected']/(stats['loans_collected']+stats['loans_outstanding'])*100) if (stats['loans_collected']+stats['loans_outstanding']) > 0 else 0:.1f}% recovery rate",
                "#16A085"
            ), 1, 3
        )
        
        # Row 2: Transaction metrics
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Transactions (30 days)",
                f"{stats['transactions_30days']:,}",
                f"Daily average: {stats['transactions_30days']/30:.0f}",
                "#9B59B6"
            ), 2, 0
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Deposits (30 days)",
                f"₦{stats['deposits_30days']:,.2f}",
                "Money in",
                "#27AE60"
            ), 2, 1
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Withdrawals (30 days)",
                f"₦{stats['withdrawals_30days']:,.2f}",
                "Money out",
                "#E74C3C"
            ), 2, 2
        )
        
        net_flow = stats['deposits_30days'] - stats['withdrawals_30days']
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Net Flow (30 days)",
                f"₦{net_flow:,.2f}",
                "Deposits - Withdrawals",
                "#27AE60" if net_flow >= 0 else "#E74C3C"
            ), 2, 3
        )
        
        # Clear content area for numbers view
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_charts_view(self, stats):
        """Show metrics as pie charts"""
        # Show summary numbers in top row
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Members",
                f"{stats['total_members']:,}",
                f"Active: {stats['active_members']:,}",
                "#27AE60"
            ), 0, 0
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Savings",
                f"₦{stats['total_savings']:,.2f}",
                f"{stats['savings_accounts']:,} accounts",
                "#3498DB"
            ), 0, 1
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Active Loans",
                f"{stats['active_loans']:,}",
                f"₦{stats['loans_outstanding']:,.2f} outstanding",
                "#E67E22"
            ), 0, 2
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "30-Day Activity",
                f"{stats['transactions_30days']:,}",
                "transactions",
                "#9B59B6"
            ), 0, 3
        )
        
        # Clear previous charts
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(15)
        
        # Members distribution pie chart
        members_chart = self.create_pie_chart(
            "Member Status Distribution",
            [
                ("Active", stats['active_members'], "#27AE60"),
                ("Inactive", stats['inactive_members'], "#F39C12"),
                ("Deceased", stats['deceased_members'], "#E74C3C")
            ]
        )
        charts_row.addWidget(members_chart)
        
        # Savings by type pie chart
        savings_data = [
            (name, float(amount), self.get_color_for_index(i))
            for i, (name, amount) in enumerate(stats['savings_by_type'].items())
        ]
        savings_chart = self.create_pie_chart(
            "Savings Distribution by Type",
            savings_data,
            show_percentage=True
        )
        charts_row.addWidget(savings_chart)
        
        # Loans status pie chart
        loans_chart = self.create_pie_chart(
            "Loan Status Distribution",
            [
                ("Active", stats['active_loans'], "#E67E22"),
                ("Completed", stats['completed_loans'], "#27AE60")
            ]
        )
        charts_row.addWidget(loans_chart)
        
        self.content_layout.addLayout(charts_row)
    
    def show_graphs_view(self, stats):
        """Show metrics as bar/line graphs"""
        # Show summary numbers
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Members",
                f"{stats['total_members']:,}",
                f"Active: {stats['active_members']:,}",
                "#27AE60"
            ), 0, 0
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Total Savings",
                f"₦{stats['total_savings']:,.2f}",
                f"{stats['savings_accounts']:,} accounts",
                "#3498DB"
            ), 0, 1
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Loans Outstanding",
                f"₦{stats['loans_outstanding']:,.2f}",
                f"{stats['active_loans']:,} active loans",
                "#E67E22"
            ), 0, 2
        )
        
        self.metrics_layout.addWidget(
            self.create_metric_card(
                "Net Flow (30d)",
                f"₦{stats['deposits_30days'] - stats['withdrawals_30days']:,.2f}",
                "Deposits - Withdrawals",
                "#27AE60" if (stats['deposits_30days'] - stats['withdrawals_30days']) >= 0 else "#E74C3C"
            ), 0, 3
        )
        
        # Clear previous graphs
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create graphs row
        graphs_row = QHBoxLayout()
        graphs_row.setSpacing(15)
        
        # Daily transactions bar chart (last 7 days)
        daily_chart = self.create_bar_chart(
            "Daily Transactions (Last 7 Days)",
            list(reversed(list(stats['daily_transactions'].keys()))),
            [list(reversed(list(stats['daily_transactions'].values())))],
            ["Transactions"],
            ["#3498DB"]
        )
        graphs_row.addWidget(daily_chart)
        
        # Savings vs Loans comparison
        comparison_chart = self.create_bar_chart(
            "Financial Overview",
            ["Savings", "Loans Out", "Collected"],
            [
                [float(stats['total_savings']), float(stats['loans_outstanding']), float(stats['loans_collected'])]
            ],
            ["Amount (₦)"],
            ["#3498DB"]
        )
        graphs_row.addWidget(comparison_chart)
        
        self.content_layout.addLayout(graphs_row)
    
    def create_pie_chart(self, title, data, show_percentage=False):
        """Create a pie chart"""
        series = QPieSeries()
        
        total = sum(value for _, value, _ in data)
        
        for label, value, color in data:
            if value > 0:  # Only add non-zero slices
                slice = series.append(label, value)
                slice.setColor(QColor(color))
                slice.setLabelVisible(True)
                if show_percentage:
                    percentage = (value / total * 100) if total > 0 else 0
                    slice.setLabel(f"{label}\n{percentage:.1f}%")
                else:
                    slice.setLabel(f"{label}\n{int(value)}")
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#2D2D32"))
        chart.setTitleBrush(QColor("#E6E6EB"))
        chart.legend().setLabelColor(QColor("#E6E6EB"))
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(350)
        
        return chart_view
    
    def create_bar_chart(self, title, categories, data_sets, set_names, colors):
        """Create a bar chart"""
        series_list = []
        
        for i, (data, name, color) in enumerate(zip(data_sets, set_names, colors)):
            bar_set = QBarSet(name)
            bar_set.setColor(QColor(color))
            for value in data:
                bar_set.append(value)
            series_list.append(bar_set)
        
        series = QBarSeries()
        for bar_set in series_list:
            series.append(bar_set)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.setBackgroundBrush(QColor("#2D2D32"))
        chart.setTitleBrush(QColor("#E6E6EB"))
        chart.legend().setLabelColor(QColor("#E6E6EB"))
        
        # X Axis
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsColor(QColor("#E6E6EB"))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y Axis
        axis_y = QValueAxis()
        axis_y.setLabelsColor(QColor("#E6E6EB"))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(350)
        
        return chart_view
    
    def get_color_for_index(self, index):
        """Get color for chart based on index"""
        colors = ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12", "#9B59B6", "#1ABC9C", "#E67E22"]
        return colors[index % len(colors)]