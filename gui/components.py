import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from datetime import datetime
from typing import List, Any, Dict, Callable
from utils.logging_config import logger

# Translation dictionary
TRANSLATIONS = {
    'en': {
        'min_amount': 'Min Amount ($):',
        'hours_back': 'Hours Back:',
        'watchlist_hours': 'Watchlist Hours:',
        'include_sales': 'Include Sales',
        'update': 'Update',
        'add_ticker': 'Add Ticker:',
        'add': 'Add',
        'remove': 'Remove',
        'analyze': 'Analyze',
        'manual_finnhub': 'Manual Finnhub Analysis',
        'export_csv': 'Export CSV',
        'clear': 'Clear',
        'ready_for_analysis': 'Ready for analysis',
        'analysis_in_progress': 'Analysis in progress...',
        'analysis_completed': 'Analysis completed',
        'sales_disabled_msg': 'Sales disabled. Enable "Include Sales" checkbox to load.',
        'warning_msg': 'Warning: Recommendations are not financial advice. Use at your own risk.',
        'technical_analysis': 'Technical Analysis',
        'advanced_analysis': 'Advanced Financial Analysis'
    },
    'ua': {
        'min_amount': 'Мін. сума ($):',
        'hours_back': 'Годин назад:',
        'watchlist_hours': 'Watchlist годин:',
        'include_sales': 'Включити продажі',
        'update': 'Оновити',
        'add_ticker': 'Додати тікер:',
        'add': 'Додати',
        'remove': 'Видалити',
        'analyze': 'Аналізувати',
        'manual_finnhub': 'Finnhub Аналіз (Ручний)',
        'export_csv': 'Експорт CSV',
        'clear': 'Очистити',
        'ready_for_analysis': 'Готово до аналізу',
        'analysis_in_progress': 'Аналіз в процесі...',
        'analysis_completed': 'Аналіз завершено',
        'sales_disabled_msg': 'Продажі вимкнені. Увімкніть чекбокс "Включити продажі" для завантаження.',
        'warning_msg': 'Увага: Рекомендації не є фінансовими порадами. Використовуйте на власний ризик.',
        'technical_analysis': 'Технічний Аналіз',
        'advanced_analysis': 'Розширений Фінансовий Аналіз'
    }
}

class FilterFrame(ttk.Frame):
    """Filter controls frame"""
    
    def __init__(self, parent, update_callback: Callable):
        super().__init__(parent, padding="10")
        self.update_callback = update_callback
        self.current_lang = 'ua'
        self.create_widgets()
    
    def create_widgets(self):
        """Create filter widgets"""
        
        # Min amount
        self.min_amount_label = ttk.Label(self, text=TRANSLATIONS[self.current_lang]['min_amount'])
        self.min_amount_label.pack(side='left', padx=(0, 5))
        self.min_amount_var = tk.StringVar(value="100000")
        self.min_amount_entry = ttk.Entry(self, textvariable=self.min_amount_var, width=12)
        self.min_amount_entry.pack(side='left', padx=(0, 10))
        
        # Hours back
        self.hours_back_label = ttk.Label(self, text=TRANSLATIONS[self.current_lang]['hours_back'])
        self.hours_back_label.pack(side='left', padx=(0, 5))
        self.hours_back_var = tk.StringVar(value="12")
        self.hours_back_entry = ttk.Entry(self, textvariable=self.hours_back_var, width=10)
        self.hours_back_entry.pack(side='left', padx=(0, 10))
        
        # Watchlist hours
        self.watchlist_hours_label = ttk.Label(self, text=TRANSLATIONS[self.current_lang]['watchlist_hours'])
        self.watchlist_hours_label.pack(side='left', padx=(15, 5))
        self.watchlist_hours_var = tk.StringVar(value="720")
        self.watchlist_hours_entry = ttk.Entry(self, textvariable=self.watchlist_hours_var, width=10)
        self.watchlist_hours_entry.pack(side='left', padx=(0, 10))
        
        # Sales checkbox - DISABLED BY DEFAULT
        self.include_sales_var = tk.BooleanVar(value=False)
        self.sales_checkbox = ttk.Checkbutton(
            self, 
            text=TRANSLATIONS[self.current_lang]['include_sales'], 
            variable=self.include_sales_var
        )
        self.sales_checkbox.pack(side='left', padx=(15, 10))
        
        # Update button
        self.update_button = ttk.Button(self, text=TRANSLATIONS[self.current_lang]['update'], command=self.update_callback)
        self.update_button.pack(side='left', padx=(10, 0))
        
        # Language toggle
        self.lang_button = ttk.Button(self, text="EN", command=self.toggle_language)
        self.lang_button.pack(side='right')
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get filter parameters"""
        try:
            return {
                'min_amount': float(self.min_amount_var.get()),
                'hours_back': int(self.hours_back_var.get()),
                'watchlist_hours': int(self.watchlist_hours_var.get()),
                'include_sales': self.include_sales_var.get()
            }
        except ValueError as e:
            logger.error(f"Invalid filter parameters: {e}")
            raise ValueError("Введіть коректні числові значення")
    
    def toggle_language(self):
        """Toggle language"""
        self.current_lang = 'en' if self.current_lang == 'ua' else 'ua'
        self.lang_button.config(text="UA" if self.current_lang == 'en' else "EN")
        self.update_language()
    
    def update_language(self):
        """Update widget texts with current language"""
        self.min_amount_label.config(text=TRANSLATIONS[self.current_lang]['min_amount'])
        self.hours_back_label.config(text=TRANSLATIONS[self.current_lang]['hours_back'])
        self.watchlist_hours_label.config(text=TRANSLATIONS[self.current_lang]['watchlist_hours'])
        self.sales_checkbox.config(text=TRANSLATIONS[self.current_lang]['include_sales'])
        self.update_button.config(text=TRANSLATIONS[self.current_lang]['update'])

class StatusBar(ttk.Frame):
    """Status bar widget"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.status_var = tk.StringVar(value="Готово")
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_var, 
            relief='sunken', 
            anchor='w',
            padding=5
        )
        self.status_label.pack(fill='x')
    
    def set_status(self, message: str):
        """Set status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"{timestamp} - {message}")

class TradingTreeView(ttk.Treeview):
    """Enhanced treeview for trading data"""
    
    def __init__(self, parent, tree_type: str):
        self.tree_type = tree_type
        
        # Define columns
        self.columns = (
            'Date', 'Ticker', 'Sector', 'Insider', 'Type', 'Amount',
            'Current Price', 'Fair (Yahoo)', 'Fair (Finviz)', 'Fair (StockAnalysis)',
            'Fair Avg', 'Rec.', 'Score'
        )
        
        super().__init__(parent, columns=self.columns, show='headings')
        
        self.setup_columns()
        self.setup_tags()
        self.setup_scrollbars()
    
    def setup_columns(self):
        """Setup column properties"""
        column_config = {
            'Date': {'width': 140, 'anchor': 'w'},
            'Ticker': {'width': 70, 'anchor': 'center'},
            'Sector': {'width': 120, 'anchor': 'w'},
            'Insider': {'width': 250, 'anchor': 'w'},
            'Type': {'width': 120, 'anchor': 'center'},
            'Amount': {'width': 120, 'anchor': 'e'},
            'Current Price': {'width': 100, 'anchor': 'e'},
            'Fair (Yahoo)': {'width': 100, 'anchor': 'e'},
            'Fair (Finviz)': {'width': 100, 'anchor': 'e'},
            'Fair (StockAnalysis)': {'width': 100, 'anchor': 'e'},
            'Fair Avg': {'width': 100, 'anchor': 'e'},
            'Rec.': {'width': 90, 'anchor': 'center'},
            'Score': {'width': 70, 'anchor': 'e'}
        }
        
        for col in self.columns:
            self.heading(col, text=col)
            config = column_config.get(col, {'width': 100, 'anchor': 'w'})
            self.column(col, width=config['width'], anchor=config['anchor'])
    
    def setup_tags(self):
        """Setup row tags for styling"""
        # Recommendation tags
        recommendation_colors = {
            'Strong Buy': '#aaffaa',
            'Buy': '#e0ffe0',
            'Hold': '#f8f8f8',
            'Sell': '#ffe0e0',
            'Strong Sell': '#ffb6b6'
        }
        
        for rec, color in recommendation_colors.items():
            self.tag_configure(rec, background=color)
        
        # Trade type tags
        self.tag_configure('Purchase', foreground='green')
        self.tag_configure('Sale', foreground='red')
    
    def setup_scrollbars(self):
        """Setup scrollbars"""
        # Create frame for tree and scrollbars
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(fill='both', expand=True)
        
        # Move tree to frame
        self.pack_forget()
        self.pack(in_=self.tree_frame, fill='both', expand=True, side='left')
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.yview)
        v_scrollbar.pack(side='right', fill='y')
        self.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient='horizontal', command=self.xview)
        h_scrollbar.pack(side='bottom', fill='x')
        self.configure(xscrollcommand=h_scrollbar.set)
    
    def update_trades(self, trades: List[Any]):
        """Update tree with new trades"""
        # Clear existing items
        for item in self.get_children():
            self.delete(item)
        
        # Add new trades
        for trade in trades:
            self.insert_trade(trade)
        
        logger.debug(f"Updated {self.tree_type} tree with {len(trades)} trades")
    
    def insert_trade(self, trade):
        """Insert a single trade into the tree"""
        try:
            # Format values
            values = (
                trade.date.strftime('%Y-%m-%d %H:%M:%S'),
                trade.ticker,
                trade.sector,
                f"{trade.insider_name} ({trade.insider_title})",
                trade.trade_type.value.title(),
                f"${trade.amount:,.2f}",
                f"${trade.current_price:.2f}" if trade.current_price else "N/A",
                f"${trade.target_prices.get('yahoo'):.2f}" if trade.target_prices.get('yahoo') else "N/A",
                f"${trade.target_prices.get('finviz'):.2f}" if trade.target_prices.get('finviz') else "N/A",
                f"${trade.target_prices.get('stockanalysis'):.2f}" if trade.target_prices.get('stockanalysis') else "N/A",
                f"${trade.fair_avg:.2f}" if trade.fair_avg else "N/A",
                trade.recommendation.value if trade.recommendation else "N/A",
                str(trade.score)
            )
            
            # Determine tags
            tags = []
            if trade.recommendation:
                tags.append(trade.recommendation.value)
            tags.append('Purchase' if trade.amount > 0 else 'Sale')
            
            # Insert item
            self.insert('', 'end', values=values, tags=tags)
            
        except Exception as e:
            logger.error(f"Failed to insert trade for {trade.ticker}: {e}")
    
    def export_to_csv(self) -> str:
        """Export tree data to CSV"""
        try:
            # Get all data
            data = []
            for item in self.get_children():
                data.append(self.item(item)['values'])
            
            if not data:
                raise ValueError("No data to export")
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=self.columns)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.tree_type}_trades_{timestamp}.csv"
            
            # Save to CSV
            df.to_csv(filename, index=False, encoding='utf-8')
            
            logger.info(f"Exported {len(data)} rows to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

class WatchlistFrame(ttk.Frame):
    """Enhanced watchlist frame with add/remove functionality"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.current_lang = 'ua'
        self.create_widgets()
    
    def create_widgets(self):
        """Create watchlist widgets"""
        
        # Control frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Add ticker controls
        self.add_label = ttk.Label(control_frame, text=TRANSLATIONS[self.current_lang]['add_ticker'])
        self.add_label.pack(side='left', padx=5)
        
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(control_frame, textvariable=self.ticker_var, width=10)
        self.ticker_entry.pack(side='left', padx=5)
        self.ticker_entry.bind('<Return>', self.add_ticker)
        
        self.add_button = ttk.Button(control_frame, text=TRANSLATIONS[self.current_lang]['add'], command=self.add_ticker)
        self.add_button.pack(side='left', padx=5)
        
        self.remove_button = ttk.Button(control_frame, text=TRANSLATIONS[self.current_lang]['remove'], command=self.remove_ticker)
        self.remove_button.pack(side='left', padx=5)
        
        # Tree for watchlist
        self.watchlist_tree = TradingTreeView(self, "watchlist")
        
        # Auto-refresh watchlist
        self.refresh_watchlist()
    
    def add_ticker(self, event=None):
        """Add ticker to watchlist"""
        ticker = self.ticker_var.get().strip().upper()
        if ticker:
            try:
                self.trading_service.add_to_watchlist(ticker)
                self.ticker_var.set("")
                self.refresh_watchlist()
                logger.info(f"Added {ticker} to watchlist")
            except Exception as e:
                logger.error(f"Failed to add {ticker} to watchlist: {e}")
    
    def remove_ticker(self):
        """Remove selected ticker from watchlist"""
        selection = self.watchlist_tree.selection()
        if selection:
            item = self.watchlist_tree.item(selection[0])
            ticker = item['values'][1] if len(item['values']) > 1 else None
            if ticker:
                try:
                    self.trading_service.remove_from_watchlist(ticker)
                    self.refresh_watchlist()
                    logger.info(f"Removed {ticker} from watchlist")
                except Exception as e:
                    logger.error(f"Failed to remove {ticker} from watchlist: {e}")
    
    def refresh_watchlist(self):
        """Refresh watchlist display"""
        # This will be called by the main window when watchlist data is updated
        pass
    
    def update_language(self, lang: str):
        """Update language"""
        self.current_lang = lang
        self.add_label.config(text=TRANSLATIONS[lang]['add_ticker'])
        self.add_button.config(text=TRANSLATIONS[lang]['add'])
        self.remove_button.config(text=TRANSLATIONS[lang]['remove'])

class AdvancedAnalysisFrame(ttk.Frame):
    """Advanced financial analysis frame with comprehensive data sources"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.current_lang = 'ua'
        self.create_widgets()
    
    def create_widgets(self):
        """Create advanced analysis widgets"""
        
        # Title
        self.title_label = ttk.Label(self, text=TRANSLATIONS[self.current_lang]['advanced_analysis'], 
                                   font=('Arial', 14, 'bold'))
        self.title_label.pack(pady=10)
        
        # Analysis tree with comprehensive columns
        self.analysis_columns = (
            'Ticker', 'Current Price', 'Target Price', 'P/E', 'PEG', 'ROE', 'Debt/Equity',
            'Free Cash Flow', 'EBITDA', 'RSI', 'MACD', 'SMA20', 'EMA50', 'Support', 'Resistance',
            'Trend', 'Recommendation', 'Score', 'Sector', 'Market Cap'
        )
        
        # Create frame for tree and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.analysis_tree = ttk.Treeview(tree_frame, columns=self.analysis_columns, show='headings')
        self.analysis_tree.pack(fill='both', expand=True, side='left')
        
        # Setup columns
        for col in self.analysis_columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.analysis_tree.yview)
        v_scrollbar.pack(side='right', fill='y')
        self.analysis_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.analysis_tree.xview)
        h_scrollbar.pack(side='bottom', fill='x')
        self.analysis_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_button = ttk.Button(button_frame, text=TRANSLATIONS[self.current_lang]['analyze'], 
                                       command=self.analyze_watchlist)
        self.analyze_button.pack(side='left', padx=5)
        
        self.manual_finnhub_button = ttk.Button(button_frame, text=TRANSLATIONS[self.current_lang]['manual_finnhub'], 
                                              command=self.manual_finnhub_analysis)
        self.manual_finnhub_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(button_frame, text=TRANSLATIONS[self.current_lang]['export_csv'], 
                                      command=self.export_analysis)
        self.export_button.pack(side='left', padx=5)
        
        self.clear_button = ttk.Button(button_frame, text=TRANSLATIONS[self.current_lang]['clear'], 
                                     command=self.clear_analysis)
        self.clear_button.pack(side='left', padx=5)
        
        # Status
        self.status_var = tk.StringVar(value=TRANSLATIONS[self.current_lang]['ready_for_analysis'])
        status_label = ttk.Label(button_frame, textvariable=self.status_var)
        status_label.pack(side='right', padx=5)
        
        # Warning
        self.warning_label = ttk.Label(
            self, 
            text=TRANSLATIONS[self.current_lang]['warning_msg'],
            foreground='red'
        )
        self.warning_label.pack(pady=5)
    
    def analyze_watchlist(self):
        """Analyze watchlist tickers with all data sources"""
        import threading
        
        def analysis_worker():
            try:
                self.status_var.set(TRANSLATIONS[self.current_lang]['analysis_in_progress'])
                
                # Perform comprehensive analysis
                watchlist_items = self.trading_service.analyze_watchlist_comprehensive()
                
                # Update GUI in main thread
                self.master.after(0, lambda: self.update_analysis_results(watchlist_items))
                
            except Exception as e:
                logger.error(f"Comprehensive analysis failed: {e}")
                self.master.after(0, lambda: self.status_var.set(f"Помилка: {str(e)}"))
        
        threading.Thread(target=analysis_worker, daemon=True).start()
    
    def manual_finnhub_analysis(self):
        """Manual Finnhub analysis for selected ticker"""
        selection = self.analysis_tree.selection()
        if not selection:
            self.status_var.set("Оберіть тікер для Finnhub аналізу")
            return
        
        item = self.analysis_tree.item(selection[0])
        ticker = item['values'][0]
        
        import threading
        
        def finnhub_worker():
            try:
                self.status_var.set(f"Finnhub аналіз {ticker}...")
                
                # Manual Finnhub analysis
                result = self.trading_service.manual_finnhub_analysis(ticker)
                
                # Update GUI in main thread
                self.master.after(0, lambda: self.show_finnhub_results(ticker, result))
                
            except Exception as e:
                logger.error(f"Finnhub analysis failed for {ticker}: {e}")
                self.master.after(0, lambda: self.status_var.set(f"Finnhub помилка: {str(e)}"))
        
        threading.Thread(target=finnhub_worker, daemon=True).start()
    
    def show_finnhub_results(self, ticker: str, result: Dict[str, Any]):
        """Show Finnhub analysis results"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Finnhub Аналіз - {ticker}")
        dialog.geometry("800x600")
        
        text_widget = tk.Text(dialog, wrap='word', font=('Consolas', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Format results
        content = f"FINNHUB АНАЛІЗ - {ticker}\n"
        content += "=" * 50 + "\n\n"
        
        for key, value in result.items():
            content += f"{key}: {value}\n"
        
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        
        self.status_var.set(f"Finnhub аналіз завершено для {ticker}")
    
    def update_analysis_results(self, watchlist_items: List[Any]):
        """Update analysis results in tree"""
        try:
            # Clear existing items
            for item in self.analysis_tree.get_children():
                self.analysis_tree.delete(item)
            
            # Add new results
            for item in watchlist_items:
                values = self.format_analysis_item(item)
                self.analysis_tree.insert('', 'end', values=values)
            
            self.status_var.set(f"{TRANSLATIONS[self.current_lang]['analysis_completed']}: {len(watchlist_items)} тікерів")
            logger.info(f"Analysis results updated: {len(watchlist_items)} items")
            
        except Exception as e:
            logger.error(f"Failed to update analysis results: {e}")
            self.status_var.set(f"Помилка оновлення: {str(e)}")
    
    def format_analysis_item(self, item) -> tuple:
        """Format analysis item for display"""
        try:
            tech = item.technical_analysis
            
            return (
                item.ticker,
                f"${item.current_price:.2f}" if item.current_price else "N/A",
                f"${item.target_price:.2f}" if item.target_price else "N/A",
                f"{item.pe_ratio:.2f}" if hasattr(item, 'pe_ratio') and item.pe_ratio else "N/A",
                f"{item.peg_ratio:.2f}" if hasattr(item, 'peg_ratio') and item.peg_ratio else "N/A",
                f"{item.roe:.2%}" if hasattr(item, 'roe') and item.roe else "N/A",
                f"{item.debt_to_equity:.2f}" if hasattr(item, 'debt_to_equity') and item.debt_to_equity else "N/A",
                f"${item.free_cash_flow/1e9:.2f}B" if hasattr(item, 'free_cash_flow') and item.free_cash_flow else "N/A",
                f"${item.ebitda/1e9:.2f}B" if hasattr(item, 'ebitda') and item.ebitda else "N/A",
                f"{tech.rsi:.2f}" if tech and tech.rsi else "N/A",
                f"{tech.macd:.4f}" if tech and tech.macd else "N/A",
                f"{tech.sma20:.2f}" if tech and tech.sma20 else "N/A",
                f"{tech.ema50:.2f}" if tech and tech.ema50 else "N/A",
                f"${tech.support:.2f}" if tech and tech.support else "N/A",
                f"${tech.resistance:.2f}" if tech and tech.resistance else "N/A",
                tech.trend if tech else "N/A",
                item.recommendation.value if item.recommendation else "N/A",
                str(item.score) if hasattr(item, 'score') else "N/A",
                item.sector if hasattr(item, 'sector') else "N/A",
                f"${item.market_cap/1e9:.2f}B" if hasattr(item, 'market_cap') and item.market_cap else "N/A"
            )
        except Exception as e:
            logger.error(f"Failed to format analysis item for {item.ticker}: {e}")
            return (item.ticker, "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", 
                   "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error")
    
    def export_analysis(self):
        """Export analysis to CSV"""
        try:
            # Get data from tree
            data = []
            for item in self.analysis_tree.get_children():
                data.append(self.analysis_tree.item(item)['values'])
            
            if not data:
                raise ValueError("No analysis data to export")
            
            # Create DataFrame and save
            df = pd.DataFrame(data, columns=self.analysis_columns)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_analysis_{timestamp}.csv"
            df.to_csv(filename, index=False, encoding='utf-8')
            
            self.status_var.set(f"Експортовано до {filename}")
            logger.info(f"Analysis exported to {filename}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.status_var.set(f"Помилка експорту: {str(e)}")
    
    def clear_analysis(self):
        """Clear analysis results"""
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        self.status_var.set(TRANSLATIONS[self.current_lang]['ready_for_analysis'])
    
    def update_language(self, lang: str):
        """Update language"""
        self.current_lang = lang
        self.title_label.config(text=TRANSLATIONS[lang]['advanced_analysis'])
        self.analyze_button.config(text=TRANSLATIONS[lang]['analyze'])
        self.manual_finnhub_button.config(text=TRANSLATIONS[lang]['manual_finnhub'])
        self.export_button.config(text=TRANSLATIONS[lang]['export_csv'])
        self.clear_button.config(text=TRANSLATIONS[lang]['clear'])
        self.warning_label.config(text=TRANSLATIONS[lang]['warning_msg'])
        if self.status_var.get() == TRANSLATIONS['ua']['ready_for_analysis'] or self.status_var.get() == TRANSLATIONS['en']['ready_for_analysis']:
            self.status_var.set(TRANSLATIONS[lang]['ready_for_analysis'])