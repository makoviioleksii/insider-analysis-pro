import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from datetime import datetime
from typing import List, Any, Dict, Callable
from utils.logging_config import logger

class FilterFrame(ttk.Frame):
    """Filter controls frame"""
    
    def __init__(self, parent, update_callback: Callable):
        super().__init__(parent, padding="10")
        self.update_callback = update_callback
        self.create_widgets()
    
    def create_widgets(self):
        """Create filter widgets"""
        
        # Min amount
        ttk.Label(self, text="Мін. сума ($):").pack(side='left', padx=(0, 5))
        self.min_amount_var = tk.StringVar(value="100000")
        self.min_amount_entry = ttk.Entry(self, textvariable=self.min_amount_var, width=12)
        self.min_amount_entry.pack(side='left', padx=(0, 10))
        
        # Hours back
        ttk.Label(self, text="Годин назад:").pack(side='left', padx=(0, 5))
        self.hours_back_var = tk.StringVar(value="12")
        self.hours_back_entry = ttk.Entry(self, textvariable=self.hours_back_var, width=10)
        self.hours_back_entry.pack(side='left', padx=(0, 10))
        
        # Watchlist hours
        ttk.Label(self, text="Watchlist годин:").pack(side='left', padx=(15, 5))
        self.watchlist_hours_var = tk.StringVar(value="720")
        self.watchlist_hours_entry = ttk.Entry(self, textvariable=self.watchlist_hours_var, width=10)
        self.watchlist_hours_entry.pack(side='left', padx=(0, 10))
        
        # Sales checkbox - DISABLED BY DEFAULT
        self.include_sales_var = tk.BooleanVar(value=False)
        self.sales_checkbox = ttk.Checkbutton(
            self, 
            text="Включити продажі", 
            variable=self.include_sales_var
        )
        self.sales_checkbox.pack(side='left', padx=(15, 10))
        
        # Update button
        self.update_button = ttk.Button(self, text="Оновити", command=self.update_callback)
        self.update_button.pack(side='left', padx=(10, 0))
        
        # Language toggle (placeholder)
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
        """Toggle language (placeholder)"""
        current = self.lang_button['text']
        self.lang_button.config(text="UA" if current == "EN" else "EN")

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
        self.pack(fill='both', expand=True)
        
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
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.master, orient='vertical', command=self.yview)
        v_scrollbar.pack(side='right', fill='y')
        self.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.master, orient='horizontal', command=self.xview)
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

class AnalysisFrame(ttk.Frame):
    """Frame for technical analysis with enhanced watchlist support"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create analysis widgets"""
        
        # Title
        title_label = ttk.Label(self, text="Технічний Аналіз Watchlist", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Analysis tree
        self.analysis_columns = (
            'Ticker', 'Current Price', 'Target Price', 'SMA20', 'EMA50',
            'RSI', 'MACD', 'Support', 'Resistance', 'Trend', 'Recommendation'
        )
        
        self.analysis_tree = ttk.Treeview(self, columns=self.analysis_columns, show='headings')
        self.analysis_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Setup columns
        for col in self.analysis_columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=100)
        
        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Аналізувати", command=self.analyze_watchlist).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Finnhub Аналіз (Ручний)", command=self.manual_finnhub_analysis).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Експорт CSV", command=self.export_analysis).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистити", command=self.clear_analysis).pack(side='left', padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Готово до аналізу")
        status_label = ttk.Label(button_frame, textvariable=self.status_var)
        status_label.pack(side='right', padx=5)
        
        # Warning
        warning_label = ttk.Label(
            self, 
            text="Увага: Рекомендації не є фінансовими порадами. Використовуйте на власний ризик.",
            foreground='red'
        )
        warning_label.pack(pady=5)
    
    def analyze_watchlist(self):
        """Analyze watchlist tickers with full data sources"""
        import threading
        
        def analysis_worker():
            try:
                self.status_var.set("Аналіз в процесі...")
                
                # Perform enhanced analysis for watchlist
                watchlist_items = self.trading_service.analyze_watchlist_enhanced()
                
                # Update GUI in main thread
                self.master.after(0, lambda: self.update_analysis_results(watchlist_items))
                
            except Exception as e:
                logger.error(f"Watchlist analysis failed: {e}")
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
            
            self.status_var.set(f"Аналіз завершено: {len(watchlist_items)} тікерів")
            logger.info(f"Analysis results updated: {len(watchlist_items)} items")
            
        except Exception as e:
            logger.error(f"Failed to update analysis results: {e}")
            self.status_var.set(f"Помилка оновлення: {str(e)}")
    
    def format_analysis_item(self, item) -> tuple:
        """Format watchlist item for display"""
        try:
            tech = item.technical_analysis
            
            return (
                item.ticker,
                f"${item.current_price:.2f}" if item.current_price else "N/A",
                f"${item.target_price:.2f}" if item.target_price else "N/A",
                f"{tech.sma20:.2f}" if tech and tech.sma20 else "N/A",
                f"{tech.ema50:.2f}" if tech and tech.ema50 else "N/A",
                f"{tech.rsi:.2f}" if tech and tech.rsi else "N/A",
                f"{tech.macd:.4f}" if tech and tech.macd else "N/A",
                f"${tech.support:.2f}" if tech and tech.support else "N/A",
                f"${tech.resistance:.2f}" if tech and tech.resistance else "N/A",
                tech.trend if tech else "N/A",
                item.recommendation.value if item.recommendation else "N/A"
            )
        except Exception as e:
            logger.error(f"Failed to format analysis item for {item.ticker}: {e}")
            return (item.ticker, "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error")
    
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
            filename = f"watchlist_analysis_{timestamp}.csv"
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
        self.status_var.set("Результати очищено")