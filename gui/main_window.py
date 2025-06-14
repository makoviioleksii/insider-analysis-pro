import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser
from datetime import datetime
from typing import List, Dict, Any
from gui.components import TradingTreeView, FilterFrame, StatusBar, WatchlistFrame, AdvancedAnalysisFrame
from gui.dialogs import DetailsDialog, ChartDialog, SettingsDialog, SupportDialog
from services.trading_service import TradingService
from utils.logging_config import logger
from config.settings import settings

class LogHandler:
    """Custom log handler for GUI"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def write(self, message):
        """Write message to text widget"""
        if self.text_widget and message.strip():
            self.text_widget.config(state='normal')
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.config(state='disabled')
    
    def flush(self):
        """Flush method for compatibility"""
        pass

class MainWindow:
    """Main application window with enhanced features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.trading_service = TradingService()
        self.last_trades = []
        self.auto_update_enabled = tk.BooleanVar(value=True)
        self.current_lang = 'ua'
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        self.setup_log_handler()
        
        # Start initial update
        self.start_update_thread()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Монітор Інсайдерських Торгів Pro v2.0")
        self.root.state('zoomed')
        
        # Configure modern style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern color scheme
        style.configure("Treeview", 
                       rowheight=28, 
                       font=('Segoe UI', 10),
                       background='#ffffff',
                       foreground='#333333',
                       fieldbackground='#ffffff')
        
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 10, 'bold'),
                       background='#f0f0f0',
                       foreground='#333333')
        
        style.configure("TNotebook.Tab", 
                       font=('Segoe UI', 10, 'bold'), 
                       padding=[15, 8])
        
        style.configure("TButton",
                       font=('Segoe UI', 9),
                       padding=[10, 5])
        
        # Configure colors for different states
        style.map("Treeview",
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Filter frame
        self.filter_frame = FilterFrame(self.root, self.on_update_clicked)
        self.filter_frame.pack(fill='x', padx=10, pady=5)
        
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_trading_tabs()
        self.create_analysis_tab()
        self.create_settings_tab()
        self.create_support_tab()
        self.create_logs_tab()
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        # Action buttons frame
        self.create_action_buttons()
    
    def create_trading_tabs(self):
        """Create trading-related tabs"""
        
        # Purchases tab
        purchases_frame = ttk.Frame(self.notebook)
        self.notebook.add(purchases_frame, text="Покупки")
        self.purchases_tree = TradingTreeView(purchases_frame, "purchases")
        
        # Sales tab with improved placeholder
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="Продажі")
        
        # Create container for sales content
        sales_container = ttk.Frame(sales_frame)
        sales_container.pack(fill='both', expand=True)
        
        # Sales tree (initially hidden)
        self.sales_tree = TradingTreeView(sales_container, "sales")
        
        # Compact sales placeholder
        self.sales_placeholder = ttk.Label(
            sales_container, 
            text="Продажі вимкнені. Увімкніть чекбокс 'Включити продажі' для завантаження.",
            font=('Segoe UI', 11),
            foreground='#666666',
            background='#f8f9fa',
            relief='solid',
            borderwidth=1,
            padding=10
        )
        self.sales_placeholder.pack(pady=20, padx=20, fill='x')
        
        # Watchlist tab with enhanced functionality
        watchlist_frame = ttk.Frame(self.notebook)
        self.notebook.add(watchlist_frame, text="Watchlist")
        self.watchlist_frame = WatchlistFrame(watchlist_frame, self.trading_service)
        
        self.all_trees = [self.purchases_tree, self.sales_tree, self.watchlist_frame.watchlist_tree]
    
    def create_analysis_tab(self):
        """Create advanced analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Розширений Аналіз")
        self.analysis_frame = AdvancedAnalysisFrame(analysis_frame, self.trading_service)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Налаштування")
        
        # Settings content with modern design
        title_frame = ttk.Frame(settings_frame)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(title_frame, text="⚙️ Налаштування додатку", 
                 font=('Segoe UI', 16, 'bold')).pack()
        
        # Settings sections
        sections = [
            ("🔑 API Ключі", "Налаштування ключів для зовнішніх сервісів", self.open_settings_dialog),
            ("🗂️ Управління кешем", "Очищення та статистика кешу", None),
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
        """Create financial support tab"""
        support_frame = ttk.Frame(self.notebook)
        self.notebook.add(support_frame, text="💰 Підтримка")
        
        # Support content
        title_frame = ttk.Frame(support_frame)
        title_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(title_frame, text="💰 Фінансова підтримка проекту", 
                 font=('Segoe UI', 16, 'bold')).pack()
        
        desc_text = ("Якщо цей додаток допоміг вам у торгівлі та аналізі,\n"
                    "ви можете підтримати розробку проекту.")
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
        """Create logs tab"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Логи")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap='word', 
            font=('Consolas', 9),
            state='disabled',
            background='#1e1e1e',
            foreground='#ffffff',
            insertbackground='#ffffff'
        )
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_controls, text="🔄 Оновити логи", command=self.update_log_display).pack(side='left', padx=5)
        ttk.Button(log_controls, text="🗑️ Очистити логи", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_controls, text="💾 Експорт логів", command=self.export_logs).pack(side='left', padx=5)
        
        # Auto-refresh checkbox
        self.auto_refresh_logs = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Автооновлення", 
                       variable=self.auto_refresh_logs).pack(side='right', padx=5)
    
    def create_action_buttons(self):
        """Create action buttons frame"""
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        # Left side buttons
        left_buttons = ttk.Frame(action_frame)
        left_buttons.pack(side='left')
        
        ttk.Button(left_buttons, text="📋 Деталі", command=self.show_details).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="📈 Графік", command=self.show_chart).pack(side='left', padx=5)
        ttk.Button(left_buttons, text="💾 Експорт", command=self.export_data).pack(side='left', padx=5)
        
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
    
    def setup_bindings(self):
        """Setup event bindings"""
        for tree in self.all_trees:
            tree.bind('<Double-1>', self.on_tree_double_click)
            tree.bind('<Button-3>', self.on_tree_right_click)
        
        # Keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.start_update_thread())
        self.root.bind('<Control-s>', lambda e: self.open_settings_dialog())
        self.root.bind('<Control-e>', lambda e: self.export_data())
        self.root.bind('<Control-d>', lambda e: self.show_details())
        self.root.bind('<Control-g>', lambda e: self.show_chart())
    
    def setup_log_handler(self):
        """Setup log handler for real-time log display"""
        # Start log monitoring thread
        self.start_log_monitoring()
    
    def start_log_monitoring(self):
        """Start monitoring log file for changes"""
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
    
    def on_update_clicked(self):
        """Handle update button click"""
        self.start_update_thread()
    
    def start_update_thread(self):
        """Start update in background thread"""
        def update_worker():
            try:
                self.status_bar.set_status("Оновлення даних...")
                
                # Get filter parameters
                params = self.filter_frame.get_parameters()
                
                # Fetch data with sales control
                trades = self.trading_service.fetch_and_analyze_trades(
                    hours_back=params['hours_back'],
                    min_amount=params['min_amount'],
                    include_sales=params['include_sales']
                )
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.update_gui_with_trades(trades, params))
                
            except Exception as e:
                logger.error(f"Update failed: {e}")
                self.root.after(0, lambda: messagebox.showerror("Помилка", f"Помилка оновлення: {str(e)}"))
                self.root.after(0, lambda: self.status_bar.set_status("Помилка оновлення"))
        
        threading.Thread(target=update_worker, daemon=True).start()
    
    def update_gui_with_trades(self, trades: List[Any], params: Dict[str, Any]):
        """Update GUI with new trades data"""
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
            
            # Update status
            status_msg = f"Оновлено: {len(purchase_trades)} покупок"
            if params['include_sales']:
                status_msg += f", {len(sale_trades)} продажів"
            status_msg += f", {len(watchlist_trades)} watchlist торгів"
            
            self.status_bar.set_status(status_msg)
            
            self.last_trades = trades
            logger.info(f"GUI updated with {len(trades)} trades")
            
        except Exception as e:
            logger.error(f"Failed to update GUI: {e}")
            messagebox.showerror("Помилка", f"Помилка оновлення інтерфейсу: {str(e)}")
    
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
        tree = event.widget
        item = tree.identify('item', event.x, event.y)
        if item:
            tree.selection_set(item)
            
            # Create context menu
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="📋 Показати деталі", command=self.show_details)
            context_menu.add_command(label="📈 Відкрити графік", command=self.show_chart)
            context_menu.add_command(label="🌐 Відкрити Finviz", command=lambda: self.open_finviz(tree, item))
            context_menu.add_separator()
            context_menu.add_command(label="⭐ Додати до Watchlist", command=lambda: self.add_to_watchlist(tree, item))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def open_finviz(self, tree, item):
        """Open Finviz page for selected ticker"""
        values = tree.item(item)['values']
        if len(values) > 1:
            ticker = values[1]
            webbrowser.open(f"https://finviz.com/quote.ashx?t={ticker}")
    
    def add_to_watchlist(self, tree, item):
        """Add ticker to watchlist"""
        values = tree.item(item)['values']
        if len(values) > 1:
            ticker = values[1]
            try:
                self.trading_service.add_to_watchlist(ticker)
                messagebox.showinfo("Успіх", f"{ticker} додано до watchlist")
                # Refresh watchlist display
                self.watchlist_frame.refresh_watchlist()
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося додати {ticker} до watchlist: {str(e)}")
    
    def show_details(self):
        """Show detailed analysis for selected trade"""
        selected_tree = self.get_selected_tree()
        if selected_tree:
            selection = selected_tree.selection()
            if selection:
                item = selected_tree.item(selection[0])
                ticker = item['values'][1] if len(item['values']) > 1 else None
                if ticker:
                    dialog = DetailsDialog(self.root, ticker, self.last_trades)
                    dialog.show()
    
    def show_chart(self):
        """Show chart for selected ticker"""
        selected_tree = self.get_selected_tree()
        if selected_tree:
            selection = selected_tree.selection()
            if selection:
                item = selected_tree.item(selection[0])
                ticker = item['values'][1] if len(item['values']) > 1 else None
                if ticker:
                    dialog = ChartDialog(self.root, ticker)
                    dialog.show()
    
    def get_selected_tree(self):
        """Get currently selected tree widget"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        if tab_text == "Покупки":
            return self.purchases_tree
        elif tab_text == "Продажі":
            return self.sales_tree
        elif tab_text == "Watchlist":
            return self.watchlist_frame.watchlist_tree
        return None
    
    def export_data(self):
        """Export current data to CSV"""
        try:
            selected_tree = self.get_selected_tree()
            if selected_tree:
                filename = selected_tree.export_to_csv()
                messagebox.showinfo("Успіх", f"Дані експортовано до {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка експорту: {str(e)}")
    
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
        try:
            from utils.cache_manager import cache_manager
            stats = cache_manager.get_cache_stats()
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Статистика кешу")
            dialog.geometry("500x400")
            
            text_widget = scrolledtext.ScrolledText(dialog, wrap='word', font=('Consolas', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            
            content = "📊 Статистика кешу\n" + "=" * 30 + "\n\n"
            for cache_type, info in stats.items():
                content += f"📁 {cache_type}:\n"
                content += f"   Записів: {info['entries']}\n"
                content += f"   Розмір: {info['size_mb']:.2f} MB\n"
                content += f"   Оновлено: {info['last_modified']}\n\n"
            
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка отримання статистики: {str(e)}")
    
    def update_log_display(self):
        """Update log display"""
        try:
            if not settings.LOG_FILE.exists():
                return
                
            with open(settings.LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, content)
            self.log_text.config(state='disabled')
            
            # Scroll to bottom
            self.log_text.see(tk.END)
            
        except Exception as e:
            logger.error(f"Failed to update log display: {e}")
    
    def clear_logs(self):
        """Clear log files"""
        try:
            with open(settings.LOG_FILE, 'w', encoding='utf-8') as f:
                f.write("")
            self.update_log_display()
            messagebox.showinfo("Успіх", "Логи очищено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка очищення логів: {str(e)}")
    
    def export_logs(self):
        """Export logs to file"""
        from tkinter import filedialog
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                import shutil
                shutil.copy2(settings.LOG_FILE, filename)
                messagebox.showinfo("Успіх", f"Логи експортовано до {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка експорту логів: {str(e)}")
    
    def run(self):
        """Start the application"""
        # Start auto-update loop
        self.start_auto_update_loop()
        
        # Start main loop
        self.root.mainloop()
    
    def start_auto_update_loop(self):
        """Start auto-update loop"""
        def auto_update():
            if self.auto_update_enabled.get():
                self.start_update_thread()
            
            # Schedule next update
            self.root.after(settings.AUTO_UPDATE_INTERVAL * 1000, auto_update)
        
        # Start first auto-update after 10 seconds
        self.root.after(10000, auto_update)