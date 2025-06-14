import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
from typing import List, Any, Dict
from utils.logging_config import logger
from config.settings import settings

class DetailsDialog:
    """Dialog for showing detailed trade analysis with enhanced information"""
    
    def __init__(self, parent, ticker: str, trades: List[Any]):
        self.parent = parent
        self.ticker = ticker
        self.trades = trades
        self.dialog = None
    
    def show(self):
        """Show the dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Детальний аналіз - {self.ticker}")
        self.dialog.geometry("1000x800")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Text widget with scrollbar
        self.text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap='word',
            font=('Consolas', 10),
            width=120,
            height=50
        )
        self.text_widget.pack(fill='both', expand=True)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Закрити", command=self.dialog.destroy).pack(side='right')
        ttk.Button(button_frame, text="Копіювати", command=self.copy_to_clipboard).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Експорт", command=self.export_to_file).pack(side='right', padx=5)
    
    def populate_data(self):
        """Populate dialog with comprehensive trade data"""
        try:
            # Find trades for this ticker
            ticker_trades = [t for t in self.trades if t.ticker == self.ticker]
            
            if not ticker_trades:
                self.text_widget.insert('end', f"Дані для {self.ticker} не знайдено")
                return
            
            # Use the most recent trade
            trade = ticker_trades[0]
            
            content = f"📊 ДЕТАЛЬНИЙ ФІНАНСОВИЙ АНАЛІЗ - {self.ticker}\n"
            content += "=" * 80 + "\n\n"
            
            # Basic company info
            content += "🏢 ОСНОВНА ІНФОРМАЦІЯ\n"
            content += "-" * 30 + "\n"
            content += f"Тікер: {trade.ticker}\n"
            content += f"Сектор: {trade.sector}\n"
            content += f"Поточна ціна: ${trade.current_price:.2f}\n" if trade.current_price else "Поточна ціна: N/A\n"
            content += f"Загальна рекомендація: {trade.recommendation.value}\n" if trade.recommendation else "Рекомендація: N/A\n"
            content += f"Фінансова оцінка: {trade.score}/10\n\n"
            
            # Target prices with detailed breakdown
            content += "🎯 ЦІЛЬОВІ ЦІНИ ТА ПРОГНОЗИ\n"
            content += "-" * 35 + "\n"
            for source, price in trade.target_prices.items():
                if price:
                    potential = ((price - trade.current_price) / trade.current_price * 100) if trade.current_price else 0
                    content += f"{source.title()}: ${price:.2f} (потенціал: {potential:+.1f}%)\n"
                else:
                    content += f"{source.title()}: N/A\n"
            
            if trade.fair_avg:
                avg_potential = ((trade.fair_avg - trade.current_price) / trade.current_price * 100) if trade.current_price else 0
                content += f"\n📈 Середня цільова ціна: ${trade.fair_avg:.2f} (потенціал: {avg_potential:+.1f}%)\n"
            content += "\n"
            
            # Enhanced financial analysis
            content += "💰 ФІНАНСОВИЙ АНАЛІЗ\n"
            content += "-" * 25 + "\n"
            
            # Add financial metrics if available
            if hasattr(trade, 'financial_metrics'):
                metrics = trade.financial_metrics
                content += f"P/E Ratio: {metrics.get('pe_ratio', 'N/A')}\n"
                content += f"PEG Ratio: {metrics.get('peg_ratio', 'N/A')}\n"
                content += f"ROE: {metrics.get('roe', 'N/A')}\n"
                content += f"Debt/Equity: {metrics.get('debt_to_equity', 'N/A')}\n"
                content += f"Free Cash Flow: {metrics.get('free_cash_flow', 'N/A')}\n"
                content += f"EBITDA: {metrics.get('ebitda', 'N/A')}\n"
                content += f"Market Cap: {metrics.get('market_cap', 'N/A')}\n"
                content += f"Beta: {metrics.get('beta', 'N/A')}\n"
                content += f"Dividend Yield: {metrics.get('dividend_yield', 'N/A')}\n"
            
            content += "\n"
            
            # Technical analysis
            content += "📈 ТЕХНІЧНИЙ АНАЛІЗ\n"
            content += "-" * 25 + "\n"
            if hasattr(trade, 'technical_analysis') and trade.technical_analysis:
                tech = trade.technical_analysis
                content += f"RSI (14): {tech.rsi:.2f}\n" if tech.rsi else "RSI (14): N/A\n"
                content += f"MACD: {tech.macd:.4f}\n" if tech.macd else "MACD: N/A\n"
                content += f"MACD Signal: {tech.macd_signal:.4f}\n" if tech.macd_signal else "MACD Signal: N/A\n"
                content += f"SMA20: ${tech.sma20:.2f}\n" if tech.sma20 else "SMA20: N/A\n"
                content += f"EMA50: ${tech.ema50:.2f}\n" if tech.ema50 else "EMA50: N/A\n"
                content += f"Bollinger Upper: ${tech.bb_upper:.2f}\n" if tech.bb_upper else "Bollinger Upper: N/A\n"
                content += f"Bollinger Lower: ${tech.bb_lower:.2f}\n" if tech.bb_lower else "Bollinger Lower: N/A\n"
                content += f"Support: ${tech.support:.2f}\n" if tech.support else "Support: N/A\n"
                content += f"Resistance: ${tech.resistance:.2f}\n" if tech.resistance else "Resistance: N/A\n"
                content += f"Trend: {tech.trend}\n"
            else:
                content += "Технічний аналіз недоступний\n"
            content += "\n"
            
            # Analysis logic with detailed explanations
            content += "🧠 ЛОГІКА АНАЛІЗУ ТА ОБҐРУНТУВАННЯ\n"
            content += "-" * 45 + "\n"
            for i, reason in enumerate(trade.reasons, 1):
                # Add emoji indicators for positive/negative factors
                if any(word in reason.lower() for word in ['позитивний', 'відмінний', 'хороший', 'низький p/e', 'купує']):
                    content += f"✅ {i}. {reason}\n"
                elif any(word in reason.lower() for word in ['негативний', 'високий', 'продає', 'перекуплено']):
                    content += f"❌ {i}. {reason}\n"
                else:
                    content += f"➖ {i}. {reason}\n"
            content += "\n"
            
            # Risk assessment
            content += "⚠️ ОЦІНКА РИЗИКІВ\n"
            content += "-" * 20 + "\n"
            risk_score = self.calculate_risk_score(trade)
            content += f"Рівень ризику: {risk_score}/10\n"
            content += self.get_risk_explanation(risk_score)
            content += "\n"
            
            # Insider information
            content += "👤 ІНФОРМАЦІЯ ПРО ІНСАЙДЕРА\n"
            content += "-" * 35 + "\n"
            content += f"Ім'я: {trade.insider_name}\n"
            content += f"Посада: {trade.insider_title}\n"
            content += f"Тип операції: {trade.trade_type.value.title()}\n"
            content += f"Сума операції: ${trade.amount:,.2f}\n"
            content += f"Дата операції: {trade.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Calculate shares if price available
            if trade.current_price and trade.current_price > 0:
                shares = abs(trade.amount) / trade.current_price
                content += f"Приблизна кількість акцій: {shares:,.0f}\n"
            content += "\n"
            
            # Investment recommendation
            content += "💡 ІНВЕСТИЦІЙНА РЕКОМЕНДАЦІЯ\n"
            content += "-" * 35 + "\n"
            content += self.get_investment_recommendation(trade)
            content += "\n"
            
            # Disclaimer
            content += "⚠️ ЗАСТЕРЕЖЕННЯ\n"
            content += "-" * 15 + "\n"
            content += "Цей аналіз призначений виключно для інформаційних цілей.\n"
            content += "Не є фінансовою порадою. Завжди проводьте власне дослідження\n"
            content += "та консультуйтеся з фінансовими консультантами перед інвестуванням.\n"
            content += "Інвестиції завжди пов'язані з ризиком втрати капіталу.\n"
            
            self.text_widget.insert('end', content)
            
        except Exception as e:
            logger.error(f"Failed to populate details dialog: {e}")
            self.text_widget.insert('end', f"Помилка завантаження даних: {str(e)}")
    
    def calculate_risk_score(self, trade) -> int:
        """Calculate risk score from 1-10"""
        risk_score = 5  # Base risk
        
        # Adjust based on various factors
        if trade.score >= 8:
            risk_score -= 2
        elif trade.score >= 4:
            risk_score -= 1
        elif trade.score <= -4:
            risk_score += 2
        
        # Sector risk
        high_risk_sectors = ['Technology', 'Biotechnology', 'Energy']
        if trade.sector in high_risk_sectors:
            risk_score += 1
        
        # Trade type
        if trade.trade_type.value == 'purchase':
            risk_score -= 1
        else:
            risk_score += 1
        
        return max(1, min(10, risk_score))
    
    def get_risk_explanation(self, risk_score: int) -> str:
        """Get risk explanation based on score"""
        if risk_score <= 3:
            return "Низький ризик - консервативна інвестиція з хорошими фундаментальними показниками.\n"
        elif risk_score <= 6:
            return "Помірний ризик - збалансована інвестиція з середніми перспективами.\n"
        else:
            return "Високий ризик - спекулятивна інвестиція, потребує обережності.\n"
    
    def get_investment_recommendation(self, trade) -> str:
        """Get detailed investment recommendation"""
        if not trade.recommendation:
            return "Рекомендація недоступна через недостатність даних.\n"
        
        rec = trade.recommendation.value
        
        recommendations = {
            "Strong Buy": "🚀 СИЛЬНА ПОКУПКА\nКомпанія демонструє відмінні фінансові показники та технічні сигнали.\nРекомендується для агресивних інвесторів з високою толерантністю до ризику.\n",
            "Buy": "📈 ПОКУПКА\nПозитивні фундаментальні та технічні показники.\nПідходить для помірно агресивних інвесторів.\n",
            "Hold": "⏸️ УТРИМАННЯ\nЗбалансовані показники без чітких сигналів.\nРекомендується утримувати існуючі позиції.\n",
            "Sell": "📉 ПРОДАЖ\nНегативні тенденції у фінансових показниках.\nРозгляньте можливість продажу позицій.\n",
            "Strong Sell": "🔻 СИЛЬНИЙ ПРОДАЖ\nСерйозні проблеми у фінансових показниках.\nНегайно розгляньте продаж позицій.\n"
        }
        
        return recommendations.get(rec, "Невідома рекомендація.\n")
    
    def copy_to_clipboard(self):
        """Copy content to clipboard"""
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(content)
            messagebox.showinfo("Успіх", "Дані скопійовано в буфер обміну")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося скопіювати: {str(e)}")
    
    def export_to_file(self):
        """Export content to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialname=f"{self.ticker}_analysis.txt"
            )
            
            if filename:
                content = self.text_widget.get('1.0', 'end-1c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успіх", f"Аналіз збережено: {filename}")
                
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")
            messagebox.showerror("Помилка", f"Не вдалося зберегти аналіз: {str(e)}")

class ChartDialog:
    """Dialog for showing stock charts"""
    
    def __init__(self, parent, ticker: str):
        self.parent = parent
        self.ticker = ticker
        self.dialog = None
        self.period_var = None
        self.canvas = None
    
    def show(self):
        """Show the chart dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Графік - {self.ticker}")
        self.dialog.geometry("1200x800")
        self.dialog.transient(self.parent)
        
        self.create_widgets()
        self.plot_chart()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Control frame
        control_frame = ttk.Frame(self.dialog)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Period selection
        ttk.Label(control_frame, text="Період:").pack(side='left', padx=5)
        
        self.period_var = tk.StringVar(value="1y")
        periods = [
            ("5 днів", "5d"), ("1 місяць", "1mo"), ("3 місяці", "3mo"),
            ("6 місяців", "6mo"), ("1 рік", "1y"), ("2 роки", "2y"), ("Максимум", "max")
        ]
        
        for text, value in periods:
            ttk.Radiobutton(
                control_frame,
                text=text,
                variable=self.period_var,
                value=value,
                command=self.plot_chart
            ).pack(side='left', padx=2)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.dialog)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Оновити", command=self.plot_chart).pack(side='left')
        ttk.Button(button_frame, text="Зберегти", command=self.save_chart).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Закрити", command=self.dialog.destroy).pack(side='right')
    
    def plot_chart(self):
        """Plot stock chart"""
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Get data
            period = self.period_var.get()
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                ttk.Label(self.chart_frame, text="Дані недоступні").pack(expand=True)
                return
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # Price chart
            ax1.plot(hist.index, hist['Close'], label='Ціна закриття', linewidth=2)
            ax1.set_title(f'{self.ticker} - Ціна акції', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Ціна ($)')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Add target price if available
            try:
                info = stock.info
                target_price = info.get('targetMeanPrice')
                if target_price:
                    ax1.axhline(y=target_price, color='orange', linestyle='--', 
                               label=f'Цільова ціна: ${target_price:.2f}')
                    ax1.legend()
            except:
                pass
            
            # Volume chart
            ax2.bar(hist.index, hist['Volume'], alpha=0.7, color='lightblue')
            ax2.set_title('Обсяг торгів')
            ax2.set_ylabel('Обсяг')
            ax2.set_xlabel('Дата')
            ax2.grid(True, alpha=0.3)
            
            # Format dates
            fig.autofmt_xdate()
            
            # Tight layout
            plt.tight_layout()
            
            # Add to tkinter
            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
            
            logger.info(f"Chart plotted for {self.ticker}")
            
        except Exception as e:
            logger.error(f"Failed to plot chart for {self.ticker}: {e}")
            error_label = ttk.Label(self.chart_frame, text=f"Помилка: {str(e)}")
            error_label.pack(expand=True)
    
    def save_chart(self):
        """Save chart to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*")
                ],
                initialname=f"{self.ticker}_chart.png"
            )
            
            if filename and self.canvas:
                self.canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Успіх", f"Графік збережено: {filename}")
                
        except Exception as e:
            logger.error(f"Failed to save chart: {e}")
            messagebox.showerror("Помилка", f"Не вдалося зберегти графік: {str(e)}")

class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.settings_vars = {}
    
    def show(self):
        """Show settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Налаштування")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Notebook for different setting categories
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # API Settings
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API Ключі")
        self.create_api_settings(api_frame)
        
        # Cache Settings
        cache_frame = ttk.Frame(notebook)
        notebook.add(cache_frame, text="Кеш")
        self.create_cache_settings(cache_frame)
        
        # GUI Settings
        gui_frame = ttk.Frame(notebook)
        notebook.add(gui_frame, text="Інтерфейс")
        self.create_gui_settings(gui_frame)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Зберегти", command=self.save_settings).pack(side='right')
        ttk.Button(button_frame, text="Скасувати", command=self.dialog.destroy).pack(side='right', padx=5)
        ttk.Button(button_frame, text="За замовчуванням", command=self.reset_to_defaults).pack(side='left')
    
    def create_api_settings(self, parent):
        """Create API settings widgets"""
        # Finnhub API Key
        ttk.Label(parent, text="Finnhub API Key:").pack(anchor='w', pady=5)
        self.settings_vars['finnhub_key'] = tk.StringVar()
        finnhub_entry = ttk.Entry(parent, textvariable=self.settings_vars['finnhub_key'], width=50, show='*')
        finnhub_entry.pack(fill='x', pady=5)
        
        # Alpha Vantage API Key
        ttk.Label(parent, text="Alpha Vantage API Key:").pack(anchor='w', pady=5)
        self.settings_vars['alpha_vantage_key'] = tk.StringVar()
        av_entry = ttk.Entry(parent, textvariable=self.settings_vars['alpha_vantage_key'], width=50, show='*')
        av_entry.pack(fill='x', pady=5)
        
        # Polygon API Key
        ttk.Label(parent, text="Polygon API Key:").pack(anchor='w', pady=5)
        self.settings_vars['polygon_key'] = tk.StringVar()
        polygon_entry = ttk.Entry(parent, textvariable=self.settings_vars['polygon_key'], width=50, show='*')
        polygon_entry.pack(fill='x', pady=5)
        
        # Rate limiting
        ttk.Label(parent, text="Запитів на хвилину:").pack(anchor='w', pady=5)
        self.settings_vars['requests_per_minute'] = tk.StringVar()
        rpm_entry = ttk.Entry(parent, textvariable=self.settings_vars['requests_per_minute'], width=20)
        rpm_entry.pack(anchor='w', pady=5)
    
    def create_cache_settings(self, parent):
        """Create cache settings widgets"""
        # Cache duration
        ttk.Label(parent, text="Тривалість кешу (години):").pack(anchor='w', pady=5)
        self.settings_vars['cache_duration'] = tk.StringVar()
        cache_entry = ttk.Entry(parent, textvariable=self.settings_vars['cache_duration'], width=20)
        cache_entry.pack(anchor='w', pady=5)
        
        # Finnhub cache TTL
        ttk.Label(parent, text="Finnhub кеш TTL (секунди):").pack(anchor='w', pady=5)
        self.settings_vars['finnhub_cache_ttl'] = tk.StringVar()
        finnhub_ttl_entry = ttk.Entry(parent, textvariable=self.settings_vars['finnhub_cache_ttl'], width=20)
        finnhub_ttl_entry.pack(anchor='w', pady=5)
    
    def create_gui_settings(self, parent):
        """Create GUI settings widgets"""
        # Auto-update interval
        ttk.Label(parent, text="Інтервал автооновлення (секунди):").pack(anchor='w', pady=5)
        self.settings_vars['auto_update_interval'] = tk.StringVar()
        auto_update_entry = ttk.Entry(parent, textvariable=self.settings_vars['auto_update_interval'], width=20)
        auto_update_entry.pack(anchor='w', pady=5)
        
        # Default min amount
        ttk.Label(parent, text="Мінімальна сума за замовчуванням:").pack(anchor='w', pady=5)
        self.settings_vars['default_min_amount'] = tk.StringVar()
        min_amount_entry = ttk.Entry(parent, textvariable=self.settings_vars['default_min_amount'], width=20)
        min_amount_entry.pack(anchor='w', pady=5)
        
        # Log level
        ttk.Label(parent, text="Рівень логування:").pack(anchor='w', pady=5)
        self.settings_vars['log_level'] = tk.StringVar()
        log_level_combo = ttk.Combobox(
            parent,
            textvariable=self.settings_vars['log_level'],
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            state='readonly'
        )
        log_level_combo.pack(anchor='w', pady=5)
    
    def load_current_settings(self):
        """Load current settings into widgets"""
        # Load from environment or settings
        self.settings_vars['finnhub_key'].set(settings.FINNHUB_API_KEY)
        self.settings_vars['alpha_vantage_key'].set(settings.ALPHA_VANTAGE_API_KEY)
        self.settings_vars['polygon_key'].set(settings.POLYGON_API_KEY)
        self.settings_vars['requests_per_minute'].set(str(settings.REQUESTS_PER_MINUTE))
        self.settings_vars['cache_duration'].set(str(settings.CACHE_DURATION_HOURS))
        self.settings_vars['finnhub_cache_ttl'].set(str(settings.FINNHUB_CACHE_TTL))
        self.settings_vars['auto_update_interval'].set(str(settings.AUTO_UPDATE_INTERVAL))
        self.settings_vars['default_min_amount'].set(str(settings.DEFAULT_MIN_AMOUNT))
        self.settings_vars['log_level'].set(settings.LOG_LEVEL)
    
    def save_settings(self):
        """Save settings to .env file"""
        try:
            env_file = settings.BASE_DIR / '.env'
            
            # Read existing .env file
            env_content = {}
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            env_content[key] = value
            
            # Update with new values
            env_content.update({
                'FINNHUB_API_KEY': self.settings_vars['finnhub_key'].get(),
                'ALPHA_VANTAGE_API_KEY': self.settings_vars['alpha_vantage_key'].get(),
                'POLYGON_API_KEY': self.settings_vars['polygon_key'].get(),
                'REQUESTS_PER_MINUTE': self.settings_vars['requests_per_minute'].get(),
                'CACHE_DURATION_HOURS': self.settings_vars['cache_duration'].get(),
                'FINNHUB_CACHE_TTL': self.settings_vars['finnhub_cache_ttl'].get(),
                'AUTO_UPDATE_INTERVAL': self.settings_vars['auto_update_interval'].get(),
                'DEFAULT_MIN_AMOUNT': self.settings_vars['default_min_amount'].get(),
                'LOG_LEVEL': self.settings_vars['log_level'].get()
            })
            
            # Write back to .env file
            with open(env_file, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")
            
            messagebox.showinfo("Успіх", "Налаштування збережено. Перезапустіть додаток для застосування змін.")
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        defaults = {
            'finnhub_key': '',
            'alpha_vantage_key': '',
            'polygon_key': '',
            'requests_per_minute': '60',
            'cache_duration': '1',
            'finnhub_cache_ttl': '86400',
            'auto_update_interval': '180',
            'default_min_amount': '100000',
            'log_level': 'INFO'
        }
        
        for key, value in defaults.items():
            self.settings_vars[key].set(value)

class SupportDialog:
    """Financial support dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Show support dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Підтримка проекту")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create support widgets"""
        # Title
        title_label = ttk.Label(
            self.dialog, 
            text="💰 Підтримка проекту", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Description
        desc_text = """Якщо цей додаток допоміг вам у торгівлі та аналізі,
ви можете підтримати розробку проекту."""
        
        desc_label = ttk.Label(self.dialog, text=desc_text, justify='center')
        desc_label.pack(pady=10)
        
        # Payment methods
        methods = [
            ("🏦 Monobank", "https://send.monobank.ua/jar/8HL6KzZqVE"),
            ("💳 Картка", "5375411208279047"),
            ("₿ Bitcoin", "bc1q4fr0efqjuwv273lcncqgvw5lqayt5rnrz6j2s6"),
            ("Ξ Ethereum", "0xa4E8ECf18A7704d1a276FCdC448515Ec82e48E2c"),
            ("💰 Bitcoin Cash", "qr47gm66wcnr9xyfu70utyrdlqsshdt67g636rt9c5")
        ]
        
        for method, value in methods:
            frame = ttk.Frame(self.dialog)
            frame.pack(fill='x', padx=20, pady=10)
            
            # Method label
            method_label = ttk.Label(frame, text=method, font=('Arial', 12, 'bold'))
            method_label.pack(anchor='w')
            
            # Value frame with copy button
            value_frame = ttk.Frame(frame)
            value_frame.pack(fill='x', pady=5)
            
            # Value entry (readonly)
            value_var = tk.StringVar(value=value)
            value_entry = ttk.Entry(value_frame, textvariable=value_var, state='readonly', width=50)
            value_entry.pack(side='left', fill='x', expand=True)
            
            # Copy button
            copy_button = ttk.Button(
                value_frame, 
                text="📋", 
                width=3,
                command=lambda v=value: self.copy_to_clipboard(v)
            )
            copy_button.pack(side='right', padx=(5, 0))
        
        # Thank you message
        thanks_label = ttk.Label(
            self.dialog, 
            text="Дякуємо за підтримку! 🙏", 
            font=('Arial', 12, 'italic'),
            foreground='green'
        )
        thanks_label.pack(pady=20)
        
        # Close button
        close_button = ttk.Button(self.dialog, text="Закрити", command=self.dialog.destroy)
        close_button.pack(pady=10)
    
    def copy_to_clipboard(self, value: str):
        """Copy value to clipboard"""
        try:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(value)
            
            # Show temporary success message
            success_label = ttk.Label(self.dialog, text="✅ Скопійовано!", foreground='green')
            success_label.pack()
            
            # Remove success message after 2 seconds
            self.dialog.after(2000, success_label.destroy)
            
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            messagebox.showerror("Помилка", "Не вдалося скопіювати")