import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
from datetime import datetime
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np

from gui.components import TradingTreeView, FilterFrame, StatusBar, WatchlistFrame, AdvancedAnalysisFrame
from gui.dialogs import DetailsDialog, ChartDialog, SettingsDialog, SupportDialog
from gui.enhanced_components import (
    PortfolioFrame, AlertsFrame, MLPredictionFrame, RiskManagementFrame,
    BacktestingFrame, DashboardFrame, NewsFrame
)
from services.enhanced_trading_service import EnhancedTradingService
from utils.logging_config import logger
from config.settings import settings

# Enhanced translations
ENHANCED_TRANSLATIONS = {
    'en': {
        'min_amount': 'Min Amount ($):',
        'hours_back': 'Hours Back:',
        'watchlist_hours': 'Watchlist Hours:',
        'include_sales': 'Include Sales',
        'enable_ml': 'Enable ML Predictions',
        'update': 'Update',
        'add_ticker': 'Add Ticker:',
        'add': 'Add',
        'remove': 'Remove',
        'analyze': 'Analyze',
        'manual_finnhub': 'Manual Finnhub Analysis',
        'export_csv': 'Export CSV',
        'clear': 'Clear',
        'train_models': 'Train ML Models',
        'portfolio_management': 'Portfolio Management',
        'risk_management': 'Risk Management',
        'alerts': 'Alerts',
        'backtesting': 'Backtesting',
        'dashboard': 'Dashboard',
        'news_sentiment': 'News & Sentiment',
        'ready_for_analysis': 'Ready for analysis',
        'analysis_in_progress': 'Analysis in progress...',
        'analysis_completed': 'Analysis completed',
        'ml_training_in_progress': 'ML training in progress...',
        'ml_training_completed': 'ML training completed',
        'sales_disabled_msg': 'Sales disabled. Enable "Include Sales" checkbox to load.',
        'warning_msg': 'Warning: Recommendations are not financial advice. Use at your own risk.',
        'technical_analysis': 'Technical Analysis',
        'advanced_analysis': 'Advanced Financial Analysis',
        'create_portfolio': 'Create Portfolio',
        'add_position': 'Add Position',
        'calculate_performance': 'Calculate Performance',
        'optimize_portfolio': 'Optimize Portfolio',
        'create_alert': 'Create Alert',
        'check_alerts': 'Check Alerts',
        'run_backtest': 'Run Backtest',
        'view_results': 'View Results'
    },
    'ua': {
        'min_amount': 'Мін. сума ($):',
        'hours_back': 'Годин назад:',
        'watchlist_hours': 'Watchlist годин:',
        'include_sales': 'Включити продажі',
        'enable_ml': 'Увімкнути ML прогнози',
        'update': 'Оновити',
        'add_ticker': 'Додати тікер:',
        'add': 'Додати',
        'remove': 'Видалити',
        'analyze': 'Аналізувати',
        'manual_finnhub': 'Finnhub Аналіз (Ручний)',
        'export_csv': 'Експорт CSV',
        'clear': 'Очистити',
        'train_models': 'Навчити ML Моделі',
        'portfolio_management': 'Управління Портфелем',
        'risk_management': 'Управління Ризиками',
        'alerts': 'Сповіщення',
        'backtesting': 'Бектестинг',
        'dashboard': 'Дашборд',
        'news_sentiment': 'Новини та Настрої',
        'ready_for_analysis': 'Готово до аналізу',
        'analysis_in_progress': 'Аналіз в процесі...',
        'analysis_completed': 'Аналіз завершено',
        'ml_training_in_progress': 'Навчання ML в процесі...',
        'ml_training_completed': 'Навчання ML завершено',
        'sales_disabled_msg': 'Продажі вимкнені. Увімкніть чекбокс "Включити продажі" для завантаження.',
        'warning_msg': 'Увага: Рекомендації не є фінансовими порадами. Використовуйте на власний ризик.',
        'technical_analysis': 'Технічний Аналіз',
        'advanced_analysis': 'Розширений Фінансовий Аналіз',
        'create_portfolio': 'Створити Портфель',
        'add_position': 'Додати Позицію',
        'calculate_performance': 'Розрахувати Ефективність',
        'optimize_portfolio': 'Оптимізувати Портфель',
        'create_alert': 'Створити Сповіщення',
        'check_alerts': 'Перевірити Сповіщення',
        'run_backtest': 'Запустити Бектест',
        'view_results': 'Переглянути Результати'
    }
}

class EnhancedMainWindow:
    """Enhanced main application window with advanced features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.trading_service = EnhancedTradingService()
        self.last_trades = []
        self.auto_update_enabled = tk.BooleanVar(value=True)
        self.ml_enabled = tk.BooleanVar(value=settings.AI_PREDICTIONS_ENABLED)
        self.current_lang = settings.LANGUAGE
        
        # Enhanced state management
        self.current_portfolio = None
        self.dashboard_data = {}
        self.alert_check_interval = 60000  # 1 minute
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        self.setup_log_handler()
        
        # Start enhanced services
        self.start_alert_monitoring()
        self.start_initial_update()
    
    def setup_window(self):
        """Setup enhanced main window properties"""
        self.root.title("Insider Trading Monitor Pro v3.0 - Enhanced Edition")
        self.root.state('zoomed')
        
        # Enhanced modern style
        style = ttk.Style()
        
        # Try to use modern theme
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Enhanced color scheme
        colors = {
            'bg_primary': '#1e1e1e' if settings.THEME == 'dark' else '#ffffff',
            'bg_secondary': '#2d2d2d' if settings.THEME == 'dark' else '#f5f5f5',
            'fg_primary': '#ffffff' if settings.THEME == 'dark' else '#333333',
            'fg_secondary': '#cccccc' if settings.THEME == 'dark' else '#666666',
            'accent': '#0078d4',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
        
        # Configure enhanced styles
        style.configure("Treeview", 
                       rowheight=30, 
                       font=('Segoe UI', 10),
                       background=colors['bg_primary'],
                       foreground=colors['fg_primary'],
                       fieldbackground=colors['bg_primary'])
        
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 10, 'bold'),
                       background=colors['bg_secondary'],
                       foreground=colors['fg_primary'])
        
        style.configure("TNotebook.Tab", 
                       font=('Segoe UI', 10, 'bold'), 
                       padding=[15, 10])
        
        style.configure("TButton",
                       font=('Segoe UI', 9),
                       padding=[12, 6])
        
        style.configure("Accent.TButton",
                       font=('Segoe UI', 9, 'bold'),
                       padding=[12, 6])
        
        # Configure colors for different states
        style.map("Treeview",
                 background=[('selected', colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.map("Accent.TButton",
                 background=[('active', colors['accent'])])
    
    def create_widgets(self):
        """Create all enhanced GUI widgets"""
        
        # Enhanced filter frame
        self.filter_frame = self.create_enhanced_filter_frame()
        self.filter_frame.pack(fill='x', padx=10, pady=5)
        
        # Main notebook with enhanced tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create enhanced tabs
        self.create_enhanced_trading_tabs()
        self.create_enhanced_analysis_tabs()
        self.create_portfolio_management_tab()
        self.create_risk_management_tab()
        self.create_alerts_tab()
        self.create_backtesting_tab()
        self.create_dashboard_tab()
        self.create_news_sentiment_tab()
        self.create_settings_tab()
        self.create_support_tab()
        self.create_logs_tab()
        
        # Enhanced status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        # Enhanced action buttons
        self.create_enhanced_action_buttons()
    
    def create_enhanced_filter_frame(self):
        """Create enhanced filter frame with ML options"""
        
        filter_frame = ttk.Frame(self.root, padding="10")
        
        # Left side - basic filters
        left_frame = ttk.Frame(filter_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        # Min amount
        ttk.Label(left_frame, text=ENHANCED_TRANSLATIONS[self.current_lang]['min_amount']).pack(side='left', padx=(0, 5))
        self.min_amount_var = tk.StringVar(value=str(settings.DEFAULT_MIN_AMOUNT))
        ttk.Entry(left_frame, textvariable=self.min_amount_var, width=12).pack(side='left', padx=(0, 10))
        
        # Hours back
        ttk.Label(left_frame, text=ENHANCED_TRANSLATIONS[self.current_lang]['hours_back']).pack(side='left', padx=(0, 5))
        self.hours_back_var = tk.StringVar(value=str(settings.DEFAULT_HOURS_BACK))
        ttk.Entry(left_frame, textvariable=self.hours_back_var, width=10).pack(side='left', padx=(0, 10))
        
        # Watchlist hours
        ttk.Label(left_frame, text=ENHANCED_TRANSLATIONS[self.current_lang]['watchlist_hours']).pack(side='left', padx=(15, 5))
        self.watchlist_hours_var = tk.StringVar(value="720")
        ttk.Entry(left_frame, textvariable=self.watchlist_hours_var, width=10).pack(side='left', padx=(0, 10))
        
        # Middle - checkboxes
        middle_frame = ttk.Frame(filter_frame)
        middle_frame.pack(side='left', padx=20)
        
        # Sales checkbox
        self.include_sales_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            middle_frame, 
            text=ENHANCED_TRANSLATIONS[self.current_lang]['include_sales'], 
            variable=self.include_sales_var
        ).pack(anchor='w')
        
        # ML predictions checkbox
        ttk.Checkbutton(
            middle_frame, 
            text=ENHANCED_TRANSLATIONS[self.current_lang]['enable_ml'], 
            variable=self.ml_enabled
        ).pack(anchor='w')
        
        # Right side - action buttons
        right_frame = ttk.Frame(filter_frame)
        right_frame.pack(side='right')
        
        # Update button
        ttk.Button(
            right_frame, 
            text=ENHANCED_TRANSLATIONS[self.current_lang]['update'], 
            command=self.on_update_clicked,
            style="Accent.TButton"
        ).pack(side='left', padx=5)
        
        # Train ML models button
        ttk.Button(
            right_frame, 
            text=ENHANCED_TRANSLATIONS[self.current_lang]['train_models'], 
            command=self.train_ml_models
        ).pack(side='left', padx=5)
        
        # Language toggle
        self.lang_button = ttk.Button(
            right_frame, 
            text="EN" if self.current_lang == 'ua' else "UA", 
            command=self.toggle_language
        )
        self.lang_button.pack(side='right', padx=5)
        
        return filter_frame
    
    def create_enhanced_trading_tabs(self):
        """Create enhanced trading tabs with improved functionality"""
        
        # Purchases tab
        purchases_frame = ttk.Frame(self.notebook)
        self.notebook.add(purchases_frame, text="📈 Покупки")
        self.purchases_tree = TradingTreeView(purchases_frame, "purchases")
        
        # Sales tab
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="📉 Продажі")
        
        sales_container = ttk.Frame(sales_frame)
        sales_container.pack(fill='both', expand=True)
        
        self.sales_tree = TradingTreeView(sales_container, "sales")
        
        # Enhanced sales placeholder
        self.sales_placeholder = ttk.Label(
            sales_container, 
            text=ENHANCED_TRANSLATIONS[self.current_lang]['sales_disabled_msg'],
            font=('Segoe UI', 12),
            foreground='#666666',
            background='#f8f9fa',
            relief='solid',
            borderwidth=1,
            padding=15
        )
        self.sales_placeholder.pack(pady=30, padx=30, fill='x')
        
        # Enhanced watchlist tab
        watchlist_frame = ttk.Frame(self.notebook)
        self.notebook.add(watchlist_frame, text="⭐ Watchlist")
        self.watchlist_frame = WatchlistFrame(watchlist_frame, self.trading_service)
        
        self.all_trees = [self.purchases_tree, self.sales_tree, self.watchlist_frame.watchlist_tree]
    
    def create_enhanced_analysis_tabs(self):
        """Create enhanced analysis tabs"""
        
        # Advanced analysis tab
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🔬 Розширений Аналіз")
        self.analysis_frame = AdvancedAnalysisFrame(analysis_frame, self.trading_service)
        
        # ML Predictions tab
        ml_frame = ttk.Frame(self.notebook)
        self.notebook.add(ml_frame, text="🤖 ML Прогнози")
        self.ml_frame = MLPredictionFrame(ml_frame, self.trading_service)
    
    def create_portfolio_management_tab(self):
        """Create portfolio management tab"""
        
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="💼 Портфель")
        self.portfolio_frame = PortfolioFrame(portfolio_frame, self.trading_service)
    
    def create_risk_management_tab(self):
        """Create risk management tab"""
        
        risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(risk_frame, text="⚠️ Ризики")
        self.risk_frame = RiskManagementFrame(risk_frame, self.trading_service)
    
    def create_alerts_tab(self):
        """Create alerts management tab"""
        
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="🔔 Сповіщення")
        self.alerts_frame = AlertsFrame(alerts_frame, self.trading_service)
    
    def create_backtesting_tab(self):
        """Create backtesting tab"""
        
        backtest_frame = ttk.Frame(self.notebook)
        self.notebook.add(backtest_frame, text="📊 Бектестинг")
        self.backtest_frame = BacktestingFrame(backtest_frame, self.trading_service)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📋 Дашборд")
        self.dashboard_frame = DashboardFrame(dashboard_frame, self.trading_service)
    
    def create_news_sentiment_tab(self):
        """Create news and sentiment analysis tab"""
        
        news_frame = ttk.Frame(self.notebook)
        self.notebook.add(news_frame, text="📰 Новини")
        self.news_frame = NewsFrame(news_frame, self.trading_service)
    
    def create_settings_tab(self):
        """Create enhanced settings tab"""
        
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Налаштування")
        
        # Settings content with enhanced design
        title_frame = ttk.Frame(settings_frame)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(title_frame, text="⚙️ Розширені Налаштування", 
                 font=('Segoe UI', 16, 'bold')).pack()
        
        # Enhanced settings sections
        sections = [
            ("🔑 API Ключі", "Налаштування ключів для зовнішніх сервісів", self.open_settings_dialog),
            ("🤖 ML Налаштування", "Конфігурація машинного навчання", self.open_ml_settings),
            ("⚠️ Управління Ризиками", "Параметри ризик-менеджменту", self.open_risk_settings),
            ("🔔 Сповіщення", "Налаштування алертів та нотифікацій", self.open_notification_settings),
            ("🗂️ Управління Кешем", "Очищення та статистика кешу", None),
            ("📊 Finnhub API", "Інформація про використання Finnhub", None)
        ]
        
        for title, desc, command in sections:
            section_frame = ttk.LabelFrame(settings_frame, text=title, padding=15)
            section_frame.pack(fill='x', padx=20, pady=10)
            
            ttk.Label(section_frame, text=desc, font=('Segoe UI', 10)).pack(anchor='w')
            
            if command:
                ttk.Button(section_frame, text="Відкрити", command=command).pack(anchor='w', pady=(10, 0))
            elif "кешем" in title:
                cache_buttons = ttk.Frame(section_frame)
                cache_buttons.pack(anchor='w', pady=(10, 0))
                ttk.Button(cache_buttons, text="Очистити кеш", command=self.clear_cache).pack(side='left', padx=(0, 10))
                ttk.Button(cache_buttons, text="Статистика", command=self.show_cache_stats).pack(side='left')
            elif "Finnhub" in title:
                info_text = ("Finnhub API використовується тільки вручну через обмеження.\n"
                           "Використовуйте кнопку 'Finnhub Аналіз (Ручний)' в розділі Розширений Аналіз.")
                ttk.Label(section_frame, text=info_text, foreground='#0066cc', 
                         font=('Segoe UI', 9)).pack(anchor='w', pady=(10, 0))
    
    def create_support_tab(self):
        """Create enhanced support tab"""
        
        support_frame = ttk.Frame(self.notebook)
        self.notebook.add(support_frame, text="💰 Підтримка")
        
        # Support content
        title_frame = ttk.Frame(support_frame)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(title_frame, text="💰 Фінансова підтримка проекту", 
                 font=('Segoe UI', 16, 'bold')).pack()
        
        desc_text = ("Якщо цей додаток допоміг вам у торгівлі та аналізі,\n"
                    "ви можете підтримати розробку проекту.\n\n"
                    "Нові функції v3.0:\n"
                    "• Машинне навчання та AI прогнози\n"
                    "• Розширений ризик-менеджмент\n"
                    "• Портфельна оптимізація\n"
                    "• Бектестинг стратегій\n"
                    "• Система сповіщень")
        
        ttk.Label(title_frame, text=desc_text, font=('Segoe UI', 11), 
                 justify='center').pack(pady=10)
        
        # Support button
        support_button = ttk.Button(
            title_frame, 
            text="🎁 Показати реквізити", 
            command=self.show_support_dialog,
            style="Accent.TButton"
        )
        support_button.pack(pady=20)
        
        # Thank you message
        thanks_frame = ttk.Frame(support_frame)
        thanks_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(thanks_frame, text="Дякуємо за використання нашого додатку! 🙏", 
                 font=('Segoe UI', 12, 'italic'), foreground='#28a745').pack()
    
    def create_logs_tab(self):
        """Create enhanced logs tab"""
        
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📝 Логи")
        
        # Log display with enhanced styling
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap='word', 
            font=('Consolas', 9),
            state='disabled',
            background='#1e1e1e' if settings.THEME == 'dark' else '#ffffff',
            foreground='#ffffff' if settings.THEME == 'dark' else '#333333',
            insertbackground='#ffffff' if settings.THEME == 'dark' else '#333333'
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Enhanced log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_controls, text="🔄 Оновити логи", command=self.update_log_display).pack(side='left', padx=5)
        ttk.Button(log_controls, text="🗑️ Очистити логи", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_controls, text="💾 Експорт логів", command=self.export_logs).pack(side='left', padx=5)
        ttk.Button(log_controls, text="🔍 Фільтр логів", command=self.filter_logs).pack(side='left', padx=5)
        
        # Auto-refresh checkbox
        self.auto_refresh_logs = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Автооновлення", 
                       variable=self.auto_refresh_logs).pack(side='right', padx=5)
        
        # Log level filter
        ttk.Label(log_controls, text="Рівень:").pack(side='right', padx=5)
        self.log_level_var = tk.StringVar(value="ALL")
        log_level_combo = ttk.Combobox(
            log_controls, 
            textvariable=self.log_level_var,
            values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
            width=10,
            state='readonly'
        )
        log_level_combo.pack(side='right', padx=5)
        log_level_combo.bind('<<ComboboxSelected>>', self.filter_logs)
    
    def create_enhanced_action_buttons(self):
        """Create enhanced action buttons frame"""
        
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        # Left side buttons
        left_buttons = ttk.Frame(action_frame)
        left_buttons.pack(side='left')
        
        ttk.Button(left_buttons, text="📋 Деталі", command=self.show_details).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="📈 Графік", command=self.show_chart).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="💾 Експорт", command=self.export_data).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="🔄 Синхронізація", command=self.sync_data).pack(side='left', padx=5)
        
        # Center - status indicators
        center_frame = ttk.Frame(action_frame)
        center_frame.pack(side='left', expand=True, fill='x', padx=20)
        
        # ML status indicator
        self.ml_status_label = ttk.Label(center_frame, text="🤖 ML: Готово", foreground='green')
        self.ml_status_label.pack(side='left', padx=10)
        
        # Alert status indicator
        self.alert_status_label = ttk.Label(center_frame, text="🔔 Алерти: Активні", foreground='blue')
        self.alert_status_label.pack(side='left', padx=10)
        
        # Right side controls
        right_controls = ttk.Frame(action_frame)
        right_controls.pack(side='right')
        
        # Auto-update checkbox
        auto_update_check = ttk.Checkbutton(
            right_controls, 
            text="🔄 Автооновлення", 
            variable=self.auto_update_enabled
        )
        auto_update_check.pack(side='right', padx=5)
        
        # Theme toggle
        ttk.Button(
            right_controls, 
            text="🌙" if settings.THEME == 'light' else "☀️", 
            command=self.toggle_theme
        ).pack(side='right', padx=5)
    
    def setup_bindings(self):
        """Setup enhanced event bindings"""
        
        for tree in self.all_trees:
            tree.bind('<Double-1>', self.on_tree_double_click)
            tree.bind('<Button-3>', self.on_tree_right_click)
        
        # Enhanced keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.start_update_thread())
        self.root.bind('<Control-s>', lambda e: self.open_settings_dialog())
        self.root.bind('<Control-e>', lambda e: self.export_data())
        self.root.bind('<Control-d>', lambda e: self.show_details())
        self.root.bind('<Control-g>', lambda e: self.show_chart())
        self.root.bind('<Control-t>', lambda e: self.train_ml_models())
        self.root.bind('<Control-p>', lambda e: self.notebook.select(self.portfolio_frame))
        self.root.bind('<Control-r>', lambda e: self.notebook.select(self.risk_frame))
        self.root.bind('<Control-b>', lambda e: self.notebook.select(self.backtest_frame))
        self.root.bind('<F1>', lambda e: self.show_help())
    
    def setup_log_handler(self):
        """Setup enhanced log handler for real-time log display"""
        self.start_log_monitoring()
    
    def start_log_monitoring(self):
        """Start enhanced log monitoring thread"""
        
        def monitor_logs():
            import time
            last_size = 0
            
            while True:
                try:
                    if self.auto_refresh_logs.get() and settings.LOG_FILE.exists():
                        current_size = settings.LOG_FILE.stat().st_size
                        if current_size != last_size:
                            self.root.after(0, self.update_log_display)
                            last_size = current_size
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Log monitoring error: {e}")
                    time.sleep(5)
        
        threading.Thread(target=monitor_logs, daemon=True).start()
    
    def start_alert_monitoring(self):
        """Start alert monitoring"""
        
        def check_alerts():
            try:
                triggered_alerts = self.trading_service.check_alerts()
                if triggered_alerts:
                    self.root.after(0, lambda: self.handle_triggered_alerts(triggered_alerts))
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
            
            # Schedule next check
            self.root.after(self.alert_check_interval, check_alerts)
        
        # Start first check after 10 seconds
        self.root.after(10000, check_alerts)
    
    def handle_triggered_alerts(self, alerts: List[Dict[str, Any]]):
        """Handle triggered alerts"""
        
        for alert in alerts:
            message = (f"🔔 АЛЕРТ СПРАЦЮВАВ!\n\n"
                      f"Тікер: {alert['ticker']}\n"
                      f"Тип: {alert['alert_type']}\n"
                      f"Умова: {alert['condition']}\n"
                      f"Поріг: {alert['threshold']}\n"
                      f"Поточне значення: {alert['current_value']}\n"
                      f"Час: {alert['triggered_date']}")
            
            messagebox.showwarning("Алерт спрацював", message)
        
        # Update alert status
        self.alert_status_label.config(text=f"🔔 Алерти: {len(alerts)} спрацювали", foreground='red')
        
        # Update alerts frame if visible
        if hasattr(self, 'alerts_frame'):
            self.alerts_frame.refresh_alerts()
    
    def on_update_clicked(self):
        """Handle enhanced update button click"""
        self.start_update_thread()
    
    def start_update_thread(self):
        """Start enhanced update in background thread"""
        
        def update_worker():
            try:
                self.status_bar.set_status("Оновлення даних...")
                
                # Get filter parameters
                params = self.get_filter_parameters()
                
                # Enhanced data fetching with ML predictions
                trades = self.trading_service.fetch_and_analyze_trades_enhanced(
                    hours_back=params['hours_back'],
                    min_amount=params['min_amount'],
                    include_sales=params['include_sales'],
                    enable_ml_predictions=params['enable_ml']
                )
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.update_gui_with_trades(trades, params))
                
            except Exception as e:
                logger.error(f"Enhanced update failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Помилка", f"Помилка оновлення: {str(e)}"))
                self.root.after(0, lambda: self.status_bar.set_status("Помилка оновлення"))
        
        threading.Thread(target=update_worker, daemon=True).start()
    
    def get_filter_parameters(self) -> Dict[str, Any]:
        """Get enhanced filter parameters"""
        
        try:
            return {
                'min_amount': float(self.min_amount_var.get()),
                'hours_back': int(self.hours_back_var.get()),
                'watchlist_hours': int(self.watchlist_hours_var.get()),
                'include_sales': self.include_sales_var.get(),
                'enable_ml': self.ml_enabled.get()
            }
        except ValueError as e:
            logger.error(f"Invalid filter parameters: {e}")
            raise ValueError("Введіть коректні числові значення")
    
    def update_gui_with_trades(self, trades: List[Any], params: Dict[str, Any]):
        """Update GUI with enhanced trades data"""
        
        try:
            # Check for new trades and play sound
            if trades and len(trades) > len(self.last_trades):
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except ImportError:
                    pass
            
            # Filter trades by type and time
            from datetime import datetime, timedelta
            
            now = datetime.now()
            main_threshold = now - timedelta(hours=params['hours_back'])
            watchlist_threshold = now - timedelta(hours=params.get('watchlist_hours', 720))
            
            # Separate trades
            purchase_trades = [t for t in trades if t.trade_type.value == 'purchase' and t.date >= main_threshold]
            sale_trades = [t for t in trades if t.trade_type.value == 'sale' and t.date >= main_threshold]
            
            # Watchlist trades
            watchlist_tickers = self.trading_service.load_watchlist()
            watchlist_trades = [t for t in trades if t.ticker in watchlist_tickers and t.date >= watchlist_threshold]
            
            # Update trees
            self.purchases_tree.update_trades(purchase_trades)
            
            # Handle sales tree based on checkbox
            if params['include_sales']:
                self.sales_placeholder.pack_forget()
                self.sales_tree.pack(fill='both', expand=True)
                self.sales_tree.update_trades(sale_trades)
            else:
                self.sales_tree.pack_forget()
                self.sales_tree.update_trades([])
                self.sales_placeholder.pack(pady=20, padx=20, fill='x')
            
            self.watchlist_frame.watchlist_tree.update_trades(watchlist_trades)
            
            # Update enhanced status
            status_msg = f"Оновлено: {len(purchase_trades)} покупок"
            if params['include_sales']:
                status_msg += f", {len(sale_trades)} продажів"
            status_msg += f", {len(watchlist_trades)} watchlist торгів"
            
            if params['enable_ml']:
                ml_predictions = sum(1 for t in trades if hasattr(t, 'price_prediction_1d') and t.price_prediction_1d)
                status_msg += f", {ml_predictions} ML прогнозів"
            
            self.status_bar.set_status(status_msg)
            
            # Update dashboard data
            self.dashboard_data = {
                'total_trades': len(trades),
                'purchase_trades': len(purchase_trades),
                'sale_trades': len(sale_trades),
                'watchlist_trades': len(watchlist_trades),
                'ml_predictions': sum(1 for t in trades if hasattr(t, 'price_prediction_1d') and t.price_prediction_1d),
                'avg_score': np.mean([t.composite_score for t in trades if t.composite_score]) if trades else 0,
                'last_updated': datetime.now()
            }
            
            # Update dashboard if visible
            if hasattr(self, 'dashboard_frame'):
                self.dashboard_frame.update_dashboard(self.dashboard_data)
            
            self.last_trades = trades
            logger.info(f"Enhanced GUI updated with {len(trades)} trades")
            
        except Exception as e:
            logger.error(f"Failed to update enhanced GUI: {e}")
            messagebox.showerror("Помилка", f"Помилка оновлення інтерфейсу: {str(e)}")
    
    def train_ml_models(self):
        """Train ML models in background thread"""
        
        def training_worker():
            try:
                self.status_bar.set_status(ENHANCED_TRANSLATIONS[self.current_lang]['ml_training_in_progress'])
                self.ml_status_label.config(text="🤖 ML: Навчання...", foreground='orange')
                
                # Train models
                result = self.trading_service.train_ml_models(retrain=True)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.handle_ml_training_result(result))
                
            except Exception as e:
                logger.error(f"ML training failed: {e}")
                self.root.after(0, lambda: self.handle_ml_training_error(str(e)))
        
        threading.Thread(target=training_worker, daemon=True).start()
    
    def handle_ml_training_result(self, result: Dict[str, Any]):
        """Handle ML training result"""
        
        if result.get('status') == 'training_completed':
            self.status_bar.set_status(ENHANCED_TRANSLATIONS[self.current_lang]['ml_training_completed'])
            self.ml_status_label.config(text="🤖 ML: Готово", foreground='green')
            
            message = (f"ML моделі успішно навчені!\n\n"
                      f"Зразків для навчання: {result.get('training_samples', 'N/A')}\n"
                      f"Кількість ознак: {result.get('features', 'N/A')}\n"
                      f"Результати моделей: {len(result.get('model_results', {}))}")
            
            messagebox.showinfo("ML Навчання", message)
            
        elif result.get('status') == 'loaded_existing':
            self.status_bar.set_status("ML моделі завантажені з кешу")
            self.ml_status_label.config(text="🤖 ML: Готово", foreground='green')
            
        else:
            self.handle_ml_training_error(result.get('error', 'Unknown error'))
    
    def handle_ml_training_error(self, error: str):
        """Handle ML training error"""
        
        self.status_bar.set_status("Помилка навчання ML")
        self.ml_status_label.config(text="🤖 ML: Помилка", foreground='red')
        
        messagebox.showerror("Помилка ML", f"Помилка навчання ML моделей:\n{error}")
    
    def start_initial_update(self):
        """Start initial update"""
        self.start_update_thread()
    
    def toggle_language(self):
        """Toggle language"""
        self.current_lang = 'en' if self.current_lang == 'ua' else 'ua'
        self.lang_button.config(text="UA" if self.current_lang == 'en' else "EN")
        self.update_language()
    
    def update_language(self):
        """Update all widget texts with current language"""
        # This would update all translatable text in the interface
        pass
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        # This would implement theme switching
        pass
    
    def sync_data(self):
        """Synchronize data across all components"""
        
        def sync_worker():
            try:
                self.status_bar.set_status("Синхронізація даних...")
                
                # Refresh all components
                if hasattr(self, 'portfolio_frame'):
                    self.portfolio_frame.refresh_portfolios()
                
                if hasattr(self, 'alerts_frame'):
                    self.alerts_frame.refresh_alerts()
                
                if hasattr(self, 'risk_frame'):
                    self.risk_frame.refresh_risk_data()
                
                self.root.after(0, lambda: self.status_bar.set_status("Синхронізація завершена"))
                
            except Exception as e:
                logger.error(f"Data sync failed: {e}")
                self.root.after(0, lambda: self.status_bar.set_status("Помилка синхронізації"))
        
        threading.Thread(target=sync_worker, daemon=True).start()
    
    def filter_logs(self, event=None):
        """Filter logs by level"""
        # This would implement log filtering functionality
        pass
    
    def show_help(self):
        """Show help dialog"""
        
        help_text = """
        🚀 Insider Trading Monitor Pro v3.0 - Довідка
        
        Гарячі клавіші:
        F5 - Оновити дані
        Ctrl+S - Налаштування
        Ctrl+E - Експорт
        Ctrl+D - Деталі
        Ctrl+G - Графік
        Ctrl+T - Навчити ML
        Ctrl+P - Портфель
        Ctrl+R - Ризики
        Ctrl+B - Бектестинг
        F1 - Ця довідка
        
        Нові функції v3.0:
        • Машинне навчання та AI прогнози
        • Розширений ризик-менеджмент
        • Портфельна оптимізація
        • Бектестинг стратегій
        • Система сповіщень
        • Аналіз новин та настроїв
        • Інтерактивний дашборд
        """
        
        messagebox.showinfo("Довідка", help_text)
    
    # Placeholder methods for new functionality
    def open_ml_settings(self):
        """Open ML settings dialog"""
        messagebox.showinfo("ML Налаштування", "ML налаштування будуть доступні в наступній версії")
    
    def open_risk_settings(self):
        """Open risk management settings"""
        messagebox.showinfo("Ризик Налаштування", "Налаштування ризиків будуть доступні в наступній версії")
    
    def open_notification_settings(self):
        """Open notification settings"""
        messagebox.showinfo("Сповіщення", "Налаштування сповіщень будуть доступні в наступній версії")
    
    # Existing methods (simplified for brevity)
    def on_tree_double_click(self, event):
        """Handle tree double-click"""
        tree = event.widget
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            ticker = item['values'][1] if len(item['values']) > 1 else None
            if ticker:
                webbrowser.open(f"https://finviz.com/quote.ashx?t={ticker}")
    
    def on_tree_right_click(self, event):
        """Handle tree right-click context menu"""
        # Implementation would be similar to original but enhanced
        pass
    
    def show_details(self):
        """Show detailed analysis for selected trade"""
        # Enhanced implementation
        pass
    
    def show_chart(self):
        """Show chart for selected ticker"""
        # Enhanced implementation
        pass
    
    def export_data(self):
        """Export current data to CSV"""
        # Enhanced implementation
        pass
    
    def open_settings_dialog(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root)
        dialog.show()
    
    def show_support_dialog(self):
        """Show support dialog"""
        dialog = SupportDialog(self.root)
        dialog.show()
    
    def clear_cache(self):
        """Clear application cache"""
        try:
            from utils.cache_manager import cache_manager
            cache_manager.clear_cache()
            messagebox.showinfo("Успіх", "Кеш очищено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка очищення кешу: {str(e)}")
    
    def show_cache_stats(self):
        """Show cache statistics"""
        # Implementation similar to original
        pass
    
    def update_log_display(self):
        """Update log display"""
        # Enhanced implementation with filtering
        pass
    
    def clear_logs(self):
        """Clear log files"""
        # Implementation similar to original
        pass
    
    def export_logs(self):
        """Export logs to file"""
        # Implementation similar to original
        pass
    
    def run(self):
        """Start the enhanced application"""
        
        # Start auto-update loop
        self.start_auto_update_loop()
        
        # Start main loop
        self.root.mainloop()
    
    def start_auto_update_loop(self):
        """Start enhanced auto-update loop"""
        
        def auto_update():
            if self.auto_update_enabled.get():
                self.start_update_thread()
            
            # Schedule next update
            self.root.after(settings.AUTO_UPDATE_INTERVAL * 1000, auto_update)
        
        # Start first auto-update after 10 seconds
        self.root.after(10000, auto_update)