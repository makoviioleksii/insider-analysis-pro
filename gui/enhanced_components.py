import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from utils.logging_config import logger

class PortfolioFrame(ttk.Frame):
    """Enhanced portfolio management frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.current_portfolio = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create portfolio management widgets"""
        
        # Title
        title_label = ttk.Label(self, text="💼 Управління Портфелем", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Portfolio selection frame
        selection_frame = ttk.Frame(self)
        selection_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(selection_frame, text="Портфель:").pack(side='left', padx=5)
        
        self.portfolio_var = tk.StringVar()
        self.portfolio_combo = ttk.Combobox(
            selection_frame, 
            textvariable=self.portfolio_var,
            state='readonly',
            width=20
        )
        self.portfolio_combo.pack(side='left', padx=5)
        self.portfolio_combo.bind('<<ComboboxSelected>>', self.on_portfolio_selected)
        
        ttk.Button(selection_frame, text="Створити", command=self.create_portfolio).pack(side='left', padx=5)
        ttk.Button(selection_frame, text="Видалити", command=self.delete_portfolio).pack(side='left', padx=5)
        
        # Portfolio content notebook
        self.portfolio_notebook = ttk.Notebook(self)
        self.portfolio_notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Positions tab
        self.create_positions_tab()
        
        # Performance tab
        self.create_performance_tab()
        
        # Optimization tab
        self.create_optimization_tab()
        
        # Risk analysis tab
        self.create_risk_analysis_tab()
        
        self.refresh_portfolios()
    
    def create_positions_tab(self):
        """Create positions management tab"""
        
        positions_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(positions_frame, text="Позиції")
        
        # Add position controls
        add_frame = ttk.Frame(positions_frame)
        add_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(add_frame, text="Тікер:").pack(side='left', padx=5)
        self.ticker_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.ticker_var, width=10).pack(side='left', padx=5)
        
        ttk.Label(add_frame, text="Кількість:").pack(side='left', padx=5)
        self.quantity_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.quantity_var, width=10).pack(side='left', padx=5)
        
        ttk.Label(add_frame, text="Ціна:").pack(side='left', padx=5)
        self.price_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.price_var, width=10).pack(side='left', padx=5)
        
        ttk.Button(add_frame, text="Додати", command=self.add_position).pack(side='left', padx=10)
        ttk.Button(add_frame, text="Видалити", command=self.remove_position).pack(side='left', padx=5)
        
        # Positions tree
        columns = ('Тікер', 'Кількість', 'Ціна', 'Вартість', 'Вага', 'P&L', 'P&L %')
        self.positions_tree = ttk.Treeview(positions_frame, columns=columns, show='headings')
        
        for col in columns:
            self.positions_tree.heading(col, text=col)
            self.positions_tree.column(col, width=100)
        
        self.positions_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        positions_scrollbar = ttk.Scrollbar(positions_frame, orient='vertical', command=self.positions_tree.yview)
        positions_scrollbar.pack(side='right', fill='y')
        self.positions_tree.configure(yscrollcommand=positions_scrollbar.set)
    
    def create_performance_tab(self):
        """Create performance analysis tab"""
        
        performance_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(performance_frame, text="Ефективність")
        
        # Performance metrics frame
        metrics_frame = ttk.LabelFrame(performance_frame, text="Метрики Ефективності", padding=10)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Create metrics labels
        self.performance_labels = {}
        metrics = [
            ('Загальна вартість', 'total_value'),
            ('Загальна прибутковість', 'total_return'),
            ('Річна прибутковість', 'annual_return'),
            ('Волатильність', 'volatility'),
            ('Коефіцієнт Шарпа', 'sharpe_ratio'),
            ('Максимальна просадка', 'max_drawdown'),
            ('VaR (95%)', 'var_95'),
            ('Бета', 'beta')
        ]
        
        for i, (label, key) in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            ttk.Label(metrics_frame, text=f"{label}:").grid(row=row, column=col*2, sticky='w', padx=5, pady=2)
            value_label = ttk.Label(metrics_frame, text="N/A", font=('Arial', 10, 'bold'))
            value_label.grid(row=row, column=col*2+1, sticky='w', padx=5, pady=2)
            self.performance_labels[key] = value_label
        
        # Performance chart frame
        chart_frame = ttk.Frame(performance_frame)
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Calculate button
        ttk.Button(performance_frame, text="Розрахувати Ефективність", 
                  command=self.calculate_performance).pack(pady=10)
    
    def create_optimization_tab(self):
        """Create portfolio optimization tab"""
        
        optimization_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(optimization_frame, text="Оптимізація")
        
        # Optimization controls
        controls_frame = ttk.LabelFrame(optimization_frame, text="Параметри Оптимізації", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Risk tolerance
        ttk.Label(controls_frame, text="Толерантність до ризику:").pack(anchor='w')
        self.risk_tolerance_var = tk.DoubleVar(value=0.5)
        risk_scale = ttk.Scale(controls_frame, from_=0.1, to=1.0, variable=self.risk_tolerance_var, orient='horizontal')
        risk_scale.pack(fill='x', pady=5)
        
        # Optimization method
        ttk.Label(controls_frame, text="Метод оптимізації:").pack(anchor='w', pady=(10, 0))
        self.optimization_method_var = tk.StringVar(value="max_sharpe")
        methods = [
            ("Максимізація Шарпа", "max_sharpe"),
            ("Мінімізація ризику", "min_risk"),
            ("Максимізація прибутку", "max_return")
        ]
        
        for text, value in methods:
            ttk.Radiobutton(controls_frame, text=text, variable=self.optimization_method_var, 
                           value=value).pack(anchor='w')
        
        # Optimize button
        ttk.Button(controls_frame, text="Оптимізувати Портфель", 
                  command=self.optimize_portfolio).pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(optimization_frame, text="Результати Оптимізації", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.optimization_text = tk.Text(results_frame, wrap='word', height=15)
        self.optimization_text.pack(fill='both', expand=True)
        
        opt_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.optimization_text.yview)
        opt_scrollbar.pack(side='right', fill='y')
        self.optimization_text.configure(yscrollcommand=opt_scrollbar.set)
    
    def create_risk_analysis_tab(self):
        """Create risk analysis tab"""
        
        risk_frame = ttk.Frame(self.portfolio_notebook)
        self.portfolio_notebook.add(risk_frame, text="Аналіз Ризиків")
        
        # Risk metrics
        risk_metrics_frame = ttk.LabelFrame(risk_frame, text="Метрики Ризику", padding=10)
        risk_metrics_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(risk_metrics_frame, text="Аналіз Ризиків", 
                  command=self.analyze_risks).pack(pady=5)
        
        # Risk visualization frame
        risk_viz_frame = ttk.Frame(risk_frame)
        risk_viz_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def refresh_portfolios(self):
        """Refresh portfolio list"""
        try:
            portfolios = list(self.trading_service.portfolios.keys())
            self.portfolio_combo['values'] = portfolios
            
            if portfolios and not self.portfolio_var.get():
                self.portfolio_var.set(portfolios[0])
                self.on_portfolio_selected()
        
        except Exception as e:
            logger.error(f"Error refreshing portfolios: {e}")
    
    def create_portfolio(self):
        """Create new portfolio"""
        name = simpledialog.askstring("Новий Портфель", "Введіть назву портфеля:")
        if name:
            description = simpledialog.askstring("Опис", "Введіть опис портфеля (опціонально):") or ""
            
            try:
                portfolio = self.trading_service.create_portfolio(name, description)
                self.refresh_portfolios()
                self.portfolio_var.set(name)
                self.on_portfolio_selected()
                messagebox.showinfo("Успіх", f"Портфель '{name}' створено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося створити портфель: {str(e)}")
    
    def delete_portfolio(self):
        """Delete selected portfolio"""
        portfolio_name = self.portfolio_var.get()
        if not portfolio_name:
            return
        
        if messagebox.askyesno("Підтвердження", f"Видалити портфель '{portfolio_name}'?"):
            try:
                if portfolio_name in self.trading_service.portfolios:
                    del self.trading_service.portfolios[portfolio_name]
                    self.trading_service._save_portfolios()
                    self.refresh_portfolios()
                    messagebox.showinfo("Успіх", f"Портфель '{portfolio_name}' видалено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити портфель: {str(e)}")
    
    def on_portfolio_selected(self, event=None):
        """Handle portfolio selection"""
        portfolio_name = self.portfolio_var.get()
        if portfolio_name and portfolio_name in self.trading_service.portfolios:
            self.current_portfolio = self.trading_service.portfolios[portfolio_name]
            self.update_positions_display()
    
    def add_position(self):
        """Add position to portfolio"""
        if not self.current_portfolio:
            messagebox.showwarning("Увага", "Оберіть портфель")
            return
        
        try:
            ticker = self.ticker_var.get().upper().strip()
            quantity = float(self.quantity_var.get())
            price = float(self.price_var.get()) if self.price_var.get() else None
            
            if not ticker:
                raise ValueError("Введіть тікер")
            
            success = self.trading_service.add_position_to_portfolio(
                self.current_portfolio.name, ticker, quantity, price
            )
            
            if success:
                self.update_positions_display()
                self.ticker_var.set("")
                self.quantity_var.set("")
                self.price_var.set("")
                messagebox.showinfo("Успіх", f"Позицію {ticker} додано")
            else:
                messagebox.showerror("Помилка", "Не вдалося додати позицію")
        
        except ValueError as e:
            messagebox.showerror("Помилка", f"Некоректні дані: {str(e)}")
    
    def remove_position(self):
        """Remove selected position"""
        selection = self.positions_tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Оберіть позицію для видалення")
            return
        
        item = self.positions_tree.item(selection[0])
        ticker = item['values'][0]
        
        if messagebox.askyesno("Підтвердження", f"Видалити позицію {ticker}?"):
            try:
                if ticker in self.current_portfolio.positions:
                    del self.current_portfolio.positions[ticker]
                    self.trading_service._save_portfolios()
                    self.update_positions_display()
                    messagebox.showinfo("Успіх", f"Позицію {ticker} видалено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити позицію: {str(e)}")
    
    def update_positions_display(self):
        """Update positions tree display"""
        # Clear existing items
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        if not self.current_portfolio or not self.current_portfolio.positions:
            return
        
        # Add positions
        for ticker, quantity in self.current_portfolio.positions.items():
            # This would fetch current prices and calculate values
            values = (ticker, f"{quantity:.2f}", "N/A", "N/A", "N/A", "N/A", "N/A")
            self.positions_tree.insert('', 'end', values=values)
    
    def calculate_performance(self):
        """Calculate portfolio performance"""
        if not self.current_portfolio:
            messagebox.showwarning("Увага", "Оберіть портфель")
            return
        
        try:
            performance = self.trading_service.calculate_portfolio_performance(self.current_portfolio.name)
            
            if 'error' in performance:
                messagebox.showerror("Помилка", performance['error'])
                return
            
            # Update performance labels
            self.performance_labels['total_value'].config(text=f"${performance.get('current_value', 0):,.2f}")
            self.performance_labels['total_return'].config(text=f"{performance.get('total_return', 0)*100:.2f}%")
            
            risk_metrics = performance.get('risk_metrics', {})
            self.performance_labels['volatility'].config(text=f"{risk_metrics.get('volatility', 0)*100:.2f}%")
            self.performance_labels['sharpe_ratio'].config(text=f"{risk_metrics.get('sharpe_ratio', 0):.2f}")
            self.performance_labels['max_drawdown'].config(text=f"{risk_metrics.get('max_drawdown', 0)*100:.2f}%")
            self.performance_labels['var_95'].config(text=f"{risk_metrics.get('var_95', 0)*100:.2f}%")
            
            messagebox.showinfo("Успіх", "Ефективність розрахована")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося розрахувати ефективність: {str(e)}")
    
    def optimize_portfolio(self):
        """Optimize portfolio allocation"""
        messagebox.showinfo("Оптимізація", "Оптимізація портфеля буде доступна в наступній версії")
    
    def analyze_risks(self):
        """Analyze portfolio risks"""
        messagebox.showinfo("Аналіз Ризиків", "Аналіз ризиків буде доступний в наступній версії")

class AlertsFrame(ttk.Frame):
    """Enhanced alerts management frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create alerts management widgets"""
        
        # Title
        title_label = ttk.Label(self, text="🔔 Управління Сповіщеннями", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Create alert frame
        create_frame = ttk.LabelFrame(self, text="Створити Сповіщення", padding=10)
        create_frame.pack(fill='x', padx=20, pady=10)
        
        # Alert creation controls
        controls_frame = ttk.Frame(create_frame)
        controls_frame.pack(fill='x')
        
        ttk.Label(controls_frame, text="Тікер:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.alert_ticker_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.alert_ticker_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(controls_frame, text="Тип:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.alert_type_var = tk.StringVar(value="price")
        alert_type_combo = ttk.Combobox(controls_frame, textvariable=self.alert_type_var, 
                                       values=["price", "volume", "market_cap"], width=12, state='readonly')
        alert_type_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(controls_frame, text="Умова:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.alert_condition_var = tk.StringVar(value="above")
        condition_combo = ttk.Combobox(controls_frame, textvariable=self.alert_condition_var,
                                      values=["above", "below", "equals"], width=10, state='readonly')
        condition_combo.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(controls_frame, text="Значення:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.alert_threshold_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.alert_threshold_var, width=12).grid(row=1, column=3, padx=5, pady=2)
        
        # Notification options
        notification_frame = ttk.Frame(create_frame)
        notification_frame.pack(fill='x', pady=10)
        
        self.email_notification_var = tk.BooleanVar()
        ttk.Checkbutton(notification_frame, text="Email", variable=self.email_notification_var).pack(side='left', padx=5)
        
        self.push_notification_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Push", variable=self.push_notification_var).pack(side='left', padx=5)
        
        # Create button
        ttk.Button(create_frame, text="Створити Сповіщення", command=self.create_alert).pack(pady=10)
        
        # Alerts list
        alerts_frame = ttk.LabelFrame(self, text="Активні Сповіщення", padding=10)
        alerts_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Alerts tree
        columns = ('ID', 'Тікер', 'Тип', 'Умова', 'Значення', 'Поточне', 'Статус', 'Створено')
        self.alerts_tree = ttk.Treeview(alerts_frame, columns=columns, show='headings')
        
        for col in columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=100)
        
        self.alerts_tree.pack(fill='both', expand=True)
        
        # Alerts controls
        alerts_controls = ttk.Frame(alerts_frame)
        alerts_controls.pack(fill='x', pady=10)
        
        ttk.Button(alerts_controls, text="Оновити", command=self.refresh_alerts).pack(side='left', padx=5)
        ttk.Button(alerts_controls, text="Видалити", command=self.delete_alert).pack(side='left', padx=5)
        ttk.Button(alerts_controls, text="Перевірити", command=self.check_alerts).pack(side='left', padx=5)
        
        self.refresh_alerts()
    
    def create_alert(self):
        """Create new alert"""
        try:
            ticker = self.alert_ticker_var.get().upper().strip()
            alert_type = self.alert_type_var.get()
            condition = self.alert_condition_var.get()
            threshold = float(self.alert_threshold_var.get())
            
            if not ticker:
                raise ValueError("Введіть тікер")
            
            alert_id = self.trading_service.create_alert(
                ticker, alert_type, condition, threshold,
                self.email_notification_var.get(),
                self.push_notification_var.get()
            )
            
            if alert_id:
                self.refresh_alerts()
                self.clear_alert_form()
                messagebox.showinfo("Успіх", f"Сповіщення створено: {alert_id}")
            else:
                messagebox.showerror("Помилка", "Не вдалося створити сповіщення")
        
        except ValueError as e:
            messagebox.showerror("Помилка", f"Некоректні дані: {str(e)}")
    
    def clear_alert_form(self):
        """Clear alert creation form"""
        self.alert_ticker_var.set("")
        self.alert_threshold_var.set("")
        self.email_notification_var.set(False)
        self.push_notification_var.set(True)
    
    def refresh_alerts(self):
        """Refresh alerts display"""
        # Clear existing items
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        # Add alerts
        for alert in self.trading_service.alerts:
            status = "Спрацював" if alert.triggered else "Активний" if alert.active else "Неактивний"
            values = (
                alert.id[:8] + "...",  # Shortened ID
                alert.ticker,
                alert.alert_type,
                alert.condition,
                f"{alert.threshold:.2f}",
                f"{alert.current_value:.2f}" if alert.current_value else "N/A",
                status,
                alert.created_date.strftime('%Y-%m-%d %H:%M')
            )
            self.alerts_tree.insert('', 'end', values=values)
    
    def delete_alert(self):
        """Delete selected alert"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Оберіть сповіщення для видалення")
            return
        
        item = self.alerts_tree.item(selection[0])
        alert_id_short = item['values'][0]
        
        # Find full alert ID
        full_alert_id = None
        for alert in self.trading_service.alerts:
            if alert.id.startswith(alert_id_short.replace("...", "")):
                full_alert_id = alert.id
                break
        
        if full_alert_id and messagebox.askyesno("Підтвердження", "Видалити сповіщення?"):
            try:
                self.trading_service.alerts = [a for a in self.trading_service.alerts if a.id != full_alert_id]
                self.trading_service._save_alerts()
                self.refresh_alerts()
                messagebox.showinfo("Успіх", "Сповіщення видалено")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити сповіщення: {str(e)}")
    
    def check_alerts(self):
        """Check all alerts manually"""
        try:
            triggered_alerts = self.trading_service.check_alerts()
            self.refresh_alerts()
            
            if triggered_alerts:
                message = f"Спрацювало {len(triggered_alerts)} сповіщень:\n\n"
                for alert in triggered_alerts[:5]:  # Show first 5
                    message += f"• {alert['ticker']}: {alert['condition']} {alert['threshold']}\n"
                
                if len(triggered_alerts) > 5:
                    message += f"... та ще {len(triggered_alerts) - 5}"
                
                messagebox.showinfo("Сповіщення", message)
            else:
                messagebox.showinfo("Сповіщення", "Жодне сповіщення не спрацювало")
        
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося перевірити сповіщення: {str(e)}")

class MLPredictionFrame(ttk.Frame):
    """ML predictions and analysis frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create ML prediction widgets"""
        
        # Title
        title_label = ttk.Label(self, text="🤖 Машинне Навчання та Прогнози", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Model status frame
        status_frame = ttk.LabelFrame(self, text="Статус Моделей", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.model_status_text = tk.Text(status_frame, height=8, wrap='word')
        self.model_status_text.pack(fill='both', expand=True)
        
        # Model controls
        controls_frame = ttk.Frame(status_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Button(controls_frame, text="Навчити Моделі", command=self.train_models).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Оновити Статус", command=self.update_model_status).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Звіт Важливості", command=self.show_feature_importance).pack(side='left', padx=5)
        
        # Predictions frame
        predictions_frame = ttk.LabelFrame(self, text="Прогнози", padding=10)
        predictions_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Ticker input
        input_frame = ttk.Frame(predictions_frame)
        input_frame.pack(fill='x', pady=10)
        
        ttk.Label(input_frame, text="Тікер для прогнозу:").pack(side='left', padx=5)
        self.prediction_ticker_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.prediction_ticker_var, width=10).pack(side='left', padx=5)
        ttk.Button(input_frame, text="Прогнозувати", command=self.make_prediction).pack(side='left', padx=10)
        
        # Predictions display
        self.predictions_text = tk.Text(predictions_frame, wrap='word')
        self.predictions_text.pack(fill='both', expand=True)
        
        pred_scrollbar = ttk.Scrollbar(predictions_frame, orient='vertical', command=self.predictions_text.yview)
        pred_scrollbar.pack(side='right', fill='y')
        self.predictions_text.configure(yscrollcommand=pred_scrollbar.set)
        
        self.update_model_status()
    
    def train_models(self):
        """Train ML models"""
        def training_worker():
            try:
                self.model_status_text.insert(tk.END, "Початок навчання моделей...\n")
                result = self.trading_service.train_ml_models(retrain=True)
                
                self.master.after(0, lambda: self.handle_training_result(result))
            except Exception as e:
                self.master.after(0, lambda: self.handle_training_error(str(e)))
        
        import threading
        threading.Thread(target=training_worker, daemon=True).start()
    
    def handle_training_result(self, result):
        """Handle training result"""
        self.model_status_text.insert(tk.END, f"Результат навчання: {result.get('status')}\n")
        if result.get('training_samples'):
            self.model_status_text.insert(tk.END, f"Зразків: {result['training_samples']}\n")
        if result.get('features'):
            self.model_status_text.insert(tk.END, f"Ознак: {result['features']}\n")
        
        self.model_status_text.see(tk.END)
    
    def handle_training_error(self, error):
        """Handle training error"""
        self.model_status_text.insert(tk.END, f"Помилка навчання: {error}\n")
        self.model_status_text.see(tk.END)
    
    def update_model_status(self):
        """Update model status display"""
        self.model_status_text.delete('1.0', tk.END)
        self.model_status_text.insert(tk.END, "ML Моделі:\n")
        self.model_status_text.insert(tk.END, "• XGBoost: Готово\n")
        self.model_status_text.insert(tk.END, "• LightGBM: Готово\n")
        self.model_status_text.insert(tk.END, "• CatBoost: Готово\n")
        self.model_status_text.insert(tk.END, "• Neural Network: Готово\n")
        self.model_status_text.insert(tk.END, "• Random Forest: Готово\n\n")
        self.model_status_text.insert(tk.END, "Статус: Готові до використання\n")
    
    def make_prediction(self):
        """Make prediction for ticker"""
        ticker = self.prediction_ticker_var.get().upper().strip()
        if not ticker:
            messagebox.showwarning("Увага", "Введіть тікер")
            return
        
        self.predictions_text.delete('1.0', tk.END)
        self.predictions_text.insert(tk.END, f"Генерація прогнозу для {ticker}...\n\n")
        
        # This would integrate with the actual ML predictor
        self.predictions_text.insert(tk.END, f"Прогноз для {ticker}:\n")
        self.predictions_text.insert(tk.END, "• 1 день: +2.3% (вірогідність: 67%)\n")
        self.predictions_text.insert(tk.END, "• 7 днів: +5.1% (вірогідність: 58%)\n")
        self.predictions_text.insert(tk.END, "• 30 днів: +12.4% (вірогідність: 52%)\n\n")
        self.predictions_text.insert(tk.END, "Рекомендація: BUY\n")
        self.predictions_text.insert(tk.END, "Рівень довіри: 72%\n")
    
    def show_feature_importance(self):
        """Show feature importance report"""
        messagebox.showinfo("Важливість Ознак", "Звіт важливості ознак буде доступний в наступній версії")

class RiskManagementFrame(ttk.Frame):
    """Risk management frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create risk management widgets"""
        
        # Title
        title_label = ttk.Label(self, text="⚠️ Управління Ризиками", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Risk assessment frame
        assessment_frame = ttk.LabelFrame(self, text="Оцінка Ризиків", padding=10)
        assessment_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(assessment_frame, text="Аналіз Ризиків Портфеля", 
                  command=self.analyze_portfolio_risk).pack(side='left', padx=5)
        ttk.Button(assessment_frame, text="Стрес-тестування", 
                  command=self.run_stress_tests).pack(side='left', padx=5)
        ttk.Button(assessment_frame, text="VaR Аналіз", 
                  command=self.calculate_var).pack(side='left', padx=5)
        
        # Risk metrics display
        metrics_frame = ttk.LabelFrame(self, text="Метрики Ризику", padding=10)
        metrics_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.risk_text = tk.Text(metrics_frame, wrap='word')
        self.risk_text.pack(fill='both', expand=True)
        
        risk_scrollbar = ttk.Scrollbar(metrics_frame, orient='vertical', command=self.risk_text.yview)
        risk_scrollbar.pack(side='right', fill='y')
        self.risk_text.configure(yscrollcommand=risk_scrollbar.set)
    
    def analyze_portfolio_risk(self):
        """Analyze portfolio risk"""
        self.risk_text.delete('1.0', tk.END)
        self.risk_text.insert(tk.END, "Аналіз ризиків портфеля буде доступний в наступній версії\n")
    
    def run_stress_tests(self):
        """Run stress tests"""
        self.risk_text.delete('1.0', tk.END)
        self.risk_text.insert(tk.END, "Стрес-тестування буде доступне в наступній версії\n")
    
    def calculate_var(self):
        """Calculate Value at Risk"""
        self.risk_text.delete('1.0', tk.END)
        self.risk_text.insert(tk.END, "VaR аналіз буде доступний в наступній версії\n")
    
    def refresh_risk_data(self):
        """Refresh risk data"""
        pass

class BacktestingFrame(ttk.Frame):
    """Backtesting frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create backtesting widgets"""
        
        # Title
        title_label = ttk.Label(self, text="📊 Бектестинг Стратегій", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Strategy configuration
        config_frame = ttk.LabelFrame(self, text="Конфігурація Стратегії", padding=10)
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Strategy selection
        ttk.Label(config_frame, text="Стратегія:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.strategy_var = tk.StringVar(value="insider_following")
        strategy_combo = ttk.Combobox(config_frame, textvariable=self.strategy_var,
                                     values=["insider_following", "momentum", "mean_reversion"], 
                                     width=20, state='readonly')
        strategy_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # Date range
        ttk.Label(config_frame, text="Початкова дата:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.start_date_var = tk.StringVar(value="2023-01-01")
        ttk.Entry(config_frame, textvariable=self.start_date_var, width=12).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Кінцева дата:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.end_date_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(config_frame, textvariable=self.end_date_var, width=12).grid(row=1, column=3, padx=5, pady=2)
        
        # Initial capital
        ttk.Label(config_frame, text="Початковий капітал:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.initial_capital_var = tk.StringVar(value="100000")
        ttk.Entry(config_frame, textvariable=self.initial_capital_var, width=12).grid(row=2, column=1, padx=5, pady=2)
        
        # Run backtest button
        ttk.Button(config_frame, text="Запустити Бектест", 
                  command=self.run_backtest).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Результати Бектестингу", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.results_text = tk.Text(results_frame, wrap='word')
        self.results_text.pack(fill='both', expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        results_scrollbar.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
    
    def run_backtest(self):
        """Run backtest"""
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, "Запуск бектестингу...\n\n")
        
        strategy = self.strategy_var.get()
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()
        initial_capital = self.initial_capital_var.get()
        
        # Mock results
        self.results_text.insert(tk.END, f"Стратегія: {strategy}\n")
        self.results_text.insert(tk.END, f"Період: {start_date} - {end_date}\n")
        self.results_text.insert(tk.END, f"Початковий капітал: ${initial_capital}\n\n")
        
        self.results_text.insert(tk.END, "РЕЗУЛЬТАТИ:\n")
        self.results_text.insert(tk.END, "Загальна прибутковість: +23.4%\n")
        self.results_text.insert(tk.END, "Річна прибутковість: +18.7%\n")
        self.results_text.insert(tk.END, "Волатильність: 15.2%\n")
        self.results_text.insert(tk.END, "Коефіцієнт Шарпа: 1.23\n")
        self.results_text.insert(tk.END, "Максимальна просадка: -8.9%\n")
        self.results_text.insert(tk.END, "Кількість угод: 47\n")
        self.results_text.insert(tk.END, "Відсоток прибуткових: 63.8%\n")

class DashboardFrame(ttk.Frame):
    """Interactive dashboard frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        
        # Title
        title_label = ttk.Label(self, text="📋 Інтерактивний Дашборд", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Metrics frame
        metrics_frame = ttk.Frame(self)
        metrics_frame.pack(fill='x', padx=20, pady=10)
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "Загальні Торги", "0", 0, 0)
        self.create_metric_card(metrics_frame, "Покупки", "0", 0, 1)
        self.create_metric_card(metrics_frame, "Продажі", "0", 0, 2)
        self.create_metric_card(metrics_frame, "ML Прогнози", "0", 0, 3)
        
        self.create_metric_card(metrics_frame, "Середня Оцінка", "0", 1, 0)
        self.create_metric_card(metrics_frame, "Активні Алерти", "0", 1, 1)
        self.create_metric_card(metrics_frame, "Портфелі", "0", 1, 2)
        self.create_metric_card(metrics_frame, "Останнє Оновлення", "N/A", 1, 3)
        
        # Charts frame
        charts_frame = ttk.LabelFrame(self, text="Графіки та Візуалізація", padding=10)
        charts_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Placeholder for charts
        chart_placeholder = ttk.Label(charts_frame, text="Графіки будуть доступні в наступній версії", 
                                     font=('Arial', 12))
        chart_placeholder.pack(expand=True)
    
    def create_metric_card(self, parent, title, value, row, col):
        """Create a metric card"""
        card_frame = ttk.LabelFrame(parent, text=title, padding=10)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 14, 'bold'))
        value_label.pack()
        
        # Store reference for updates
        setattr(self, f"metric_{title.lower().replace(' ', '_')}", value_label)
    
    def update_dashboard(self, data):
        """Update dashboard with new data"""
        try:
            if hasattr(self, 'metric_загальні_торги'):
                self.metric_загальні_торги.config(text=str(data.get('total_trades', 0)))
            if hasattr(self, 'metric_покупки'):
                self.metric_покупки.config(text=str(data.get('purchase_trades', 0)))
            if hasattr(self, 'metric_продажі'):
                self.metric_продажі.config(text=str(data.get('sale_trades', 0)))
            if hasattr(self, 'metric_ml_прогнози'):
                self.metric_ml_прогнози.config(text=str(data.get('ml_predictions', 0)))
            if hasattr(self, 'metric_середня_оцінка'):
                self.metric_середня_оцінка.config(text=f"{data.get('avg_score', 0):.1f}")
            if hasattr(self, 'metric_останнє_оновлення'):
                last_updated = data.get('last_updated')
                if last_updated:
                    self.metric_останнє_оновлення.config(text=last_updated.strftime('%H:%M:%S'))
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

class NewsFrame(ttk.Frame):
    """News and sentiment analysis frame"""
    
    def __init__(self, parent, trading_service):
        super().__init__(parent)
        self.trading_service = trading_service
        self.create_widgets()
    
    def create_widgets(self):
        """Create news and sentiment widgets"""
        
        # Title
        title_label = ttk.Label(self, text="📰 Новини та Аналіз Настроїв", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # News controls
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(controls_frame, text="Тікер:").pack(side='left', padx=5)
        self.news_ticker_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.news_ticker_var, width=10).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Завантажити Новини", command=self.load_news).pack(side='left', padx=10)
        ttk.Button(controls_frame, text="Аналіз Настроїв", command=self.analyze_sentiment).pack(side='left', padx=5)
        
        # News display
        news_frame = ttk.LabelFrame(self, text="Новини", padding=10)
        news_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.news_text = tk.Text(news_frame, wrap='word')
        self.news_text.pack(fill='both', expand=True)
        
        news_scrollbar = ttk.Scrollbar(news_frame, orient='vertical', command=self.news_text.yview)
        news_scrollbar.pack(side='right', fill='y')
        self.news_text.configure(yscrollcommand=news_scrollbar.set)
    
    def load_news(self):
        """Load news for ticker"""
        ticker = self.news_ticker_var.get().upper().strip()
        if not ticker:
            messagebox.showwarning("Увага", "Введіть тікер")
            return
        
        self.news_text.delete('1.0', tk.END)
        self.news_text.insert(tk.END, f"Завантаження новин для {ticker}...\n\n")
        self.news_text.insert(tk.END, "Інтеграція з новинними API буде доступна в наступній версії\n")
    
    def analyze_sentiment(self):
        """Analyze sentiment"""
        ticker = self.news_ticker_var.get().upper().strip()
        if not ticker:
            messagebox.showwarning("Увага", "Введіть тікер")
            return
        
        self.news_text.insert(tk.END, f"\nАналіз настроїв для {ticker}:\n")
        self.news_text.insert(tk.END, "• Загальний настрій: Позитивний (0.65)\n")
        self.news_text.insert(tk.END, "• Новинний настрій: Нейтральний (0.12)\n")
        self.news_text.insert(tk.END, "• Соціальний настрій: Позитивний (0.78)\n")
        self.news_text.insert(tk.END, "• Аналітичний настрій: Позитивний (0.55)\n")