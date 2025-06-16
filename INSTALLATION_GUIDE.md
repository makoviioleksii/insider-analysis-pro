# Посібник з встановлення - Insider Trading Monitor Pro v3.0

## 📋 Зміст

1. [Системні вимоги](#системні-вимоги)
2. [Швидке встановлення](#швидке-встановлення)
3. [Детальне встановлення](#детальне-встановлення)
4. [Конфігурація](#конфігурація)
5. [Перший запуск](#перший-запуск)
6. [Усунення неполадок](#усунення-неполадок)
7. [Оновлення](#оновлення)

## 💻 Системні вимоги

### Мінімальні вимоги
- **ОС**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 або новіший
- **RAM**: 4GB (рекомендовано 8GB+)
- **Диск**: 2GB вільного місця
- **Інтернет**: Стабільне з'єднання для API запитів

### Рекомендовані вимоги
- **ОС**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.11
- **RAM**: 16GB
- **Диск**: 10GB вільного місця (SSD)
- **CPU**: 4+ ядра для ML обробки
- **GPU**: Опціонально для прискорення ML (CUDA-сумісна)

### Додаткові компоненти (опціонально)
- **PostgreSQL**: Для продуктивної БД
- **Redis**: Для швидкого кешування
- **MongoDB**: Для неструктурованих даних
- **Docker**: Для контейнеризації

## ⚡ Швидке встановлення

### Автоматичний інсталятор (Windows)

1. **Завантажте інсталятор**
```bash
# Завантажте setup.exe з GitHub Releases
# https://github.com/your-repo/insider-trading-monitor/releases/latest
```

2. **Запустіть інсталятор**
```bash
# Подвійний клік на setup.exe
# Слідуйте інструкціям майстра встановлення
```

3. **Запустіть додаток**
```bash
# Знайдіть "Insider Trading Monitor Pro" в меню Пуск
# Або запустіть з робочого столу
```

### Швидке встановлення через pip

```bash
# Встановлення через pip (коли буде доступно)
pip install insider-trading-monitor-pro

# Запуск
insider-trading-monitor
```

## 🔧 Детальне встановлення

### Крок 1: Підготовка системи

#### Windows
```powershell
# Встановіть Python 3.11
# Завантажте з https://python.org/downloads/

# Перевірте встановлення
python --version
pip --version

# Встановіть Git (якщо потрібно)
# Завантажте з https://git-scm.com/download/win
```

#### macOS
```bash
# Встановіть Homebrew (якщо не встановлено)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Встановіть Python
brew install python@3.11

# Встановіть Git
brew install git
```

#### Ubuntu/Debian
```bash
# Оновіть систему
sudo apt update && sudo apt upgrade -y

# Встановіть Python та залежності
sudo apt install python3.11 python3.11-pip python3.11-venv git -y

# Встановіть додаткові залежності для компіляції
sudo apt install build-essential python3.11-dev -y
```

### Крок 2: Клонування репозиторію

```bash
# Клонуйте репозиторій
git clone https://github.com/your-repo/insider-trading-monitor-v3.git
cd insider-trading-monitor-v3

# Або завантажте ZIP архів
# https://github.com/your-repo/insider-trading-monitor-v3/archive/main.zip
```

### Крок 3: Створення віртуального середовища

#### Windows
```powershell
# Створіть віртуальне середовище
python -m venv venv

# Активуйте середовище
venv\Scripts\activate

# Перевірте активацію
where python
```

#### macOS/Linux
```bash
# Створіть віртуальне середовище
python3.11 -m venv venv

# Активуйте середовище
source venv/bin/activate

# Перевірте активацію
which python
```

### Крок 4: Встановлення залежностей

```bash
# Оновіть pip
python -m pip install --upgrade pip

# Встановіть основні залежності
pip install -r requirements.txt

# Для розробки (опціонально)
pip install -r requirements-dev.txt
```

#### Альтернативне встановлення по групах

```bash
# Базові залежності
pip install pandas numpy matplotlib seaborn

# Машинне навчання
pip install scikit-learn xgboost lightgbm catboost tensorflow

# Фінансові дані
pip install yfinance finnhub-python alpha-vantage

# Веб-скрапінг
pip install requests beautifulsoup4 cloudscraper

# GUI
pip install tkinter-tooltip

# Додаткові
pip install python-dotenv pydantic aiohttp asyncio-throttle
```

### Крок 5: Конфігурація середовища

```bash
# Скопіюйте файл конфігурації
cp .env.example .env

# Відредагуйте конфігурацію
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

## ⚙️ Конфігурація

### Базова конфігурація (.env файл)

```env
# =============================================================================
# INSIDER TRADING MONITOR PRO v3.0 - КОНФІГУРАЦІЯ
# =============================================================================

# -----------------------------------------------------------------------------
# API КЛЮЧІ (Опціонально, але рекомендовано)
# -----------------------------------------------------------------------------

# Finnhub API (Безкоштовний рівень: 60 запитів/хвилину)
# Реєстрація: https://finnhub.io/register
FINNHUB_API_KEY=your_finnhub_api_key_here

# Alpha Vantage API (Безкоштовний рівень: 5 запитів/хвилину)
# Реєстрація: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Polygon API (Безкоштовний рівень: 5 запитів/хвилину)
# Реєстрація: https://polygon.io/
POLYGON_API_KEY=your_polygon_key_here

# Quandl API (Опціонально)
QUANDL_API_KEY=your_quandl_key_here

# FRED API (Безкоштовний)
# Реєстрація: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your_fred_key_here

# News API (Опціонально)
NEWS_API_KEY=your_news_api_key_here

# -----------------------------------------------------------------------------
# AI СЕРВІСИ (Опціонально)
# -----------------------------------------------------------------------------

# OpenAI API (Для розширеного NLP)
OPENAI_API_KEY=your_openai_key_here

# Anthropic API (Альтернатива OpenAI)
ANTHROPIC_API_KEY=your_anthropic_key_here

# -----------------------------------------------------------------------------
# НАЛАШТУВАННЯ КЕШУ
# -----------------------------------------------------------------------------

# Тривалість кешу в годинах
CACHE_DURATION_HOURS=1

# TTL для Finnhub кешу в секундах
FINNHUB_CACHE_TTL=86400

# TTL для Redis кешу в секундах
REDIS_CACHE_TTL=3600

# -----------------------------------------------------------------------------
# RATE LIMITING
# -----------------------------------------------------------------------------

# Запитів на хвилину (загальний ліміт)
REQUESTS_PER_MINUTE=60

# Максимальна кількість одночасних запитів
MAX_CONCURRENT_REQUESTS=10

# -----------------------------------------------------------------------------
# МАШИННЕ НАВЧАННЯ
# -----------------------------------------------------------------------------

# Інтервал оновлення ML моделей (години)
ML_MODEL_UPDATE_INTERVAL=24

# Увімкнути аналіз настроїв
SENTIMENT_ANALYSIS_ENABLED=true

# Увімкнути AI прогнози
AI_PREDICTIONS_ENABLED=true

# -----------------------------------------------------------------------------
# РИЗИК-МЕНЕДЖМЕНТ
# -----------------------------------------------------------------------------

# Максимальний розмір позиції (частка портфеля)
MAX_POSITION_SIZE=0.05

# Відсоток стоп-лосу
STOP_LOSS_PERCENTAGE=0.10

# Відсоток тейк-профіту
TAKE_PROFIT_PERCENTAGE=0.20

# -----------------------------------------------------------------------------
# GUI НАЛАШТУВАННЯ
# -----------------------------------------------------------------------------

# Інтервал автооновлення (секунди)
AUTO_UPDATE_INTERVAL=180

# Мінімальна сума за замовчуванням
DEFAULT_MIN_AMOUNT=100000

# Годин назад за замовчуванням
DEFAULT_HOURS_BACK=12

# Тема (light/dark)
THEME=dark

# Мова (ua/en)
LANGUAGE=ua

# -----------------------------------------------------------------------------
# СПОВІЩЕННЯ
# -----------------------------------------------------------------------------

# Email сповіщення
EMAIL_NOTIFICATIONS=false
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Telegram сповіщення
TELEGRAM_NOTIFICATIONS=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord сповіщення
DISCORD_NOTIFICATIONS=false
DISCORD_WEBHOOK_URL=your_discord_webhook

# -----------------------------------------------------------------------------
# БАЗИ ДАНИХ (Опціонально)
# -----------------------------------------------------------------------------

# Основна БД (SQLite за замовчуванням)
DATABASE_URL=sqlite:///insider_trading.db
# Для PostgreSQL: postgresql://user:pass@localhost/insider_trading

# Redis (для кешування)
REDIS_URL=redis://localhost:6379/0

# MongoDB (для неструктурованих даних)
MONGODB_URL=mongodb://localhost:27017/

# Elasticsearch (для пошуку)
ELASTICSEARCH_URL=http://localhost:9200

# -----------------------------------------------------------------------------
# РОЗШИРЕНІ ФУНКЦІЇ
# -----------------------------------------------------------------------------

# Увімкнути бектестинг
ENABLE_BACKTESTING=true

# Увімкнути паперову торгівлю
ENABLE_PAPER_TRADING=true

# Увімкнути реальні алерти
ENABLE_REAL_TIME_ALERTS=true

# Увімкнути оптимізацію портфеля
ENABLE_PORTFOLIO_OPTIMIZATION=true

# -----------------------------------------------------------------------------
# ЛОГУВАННЯ
# -----------------------------------------------------------------------------

# Рівень логування (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Максимальний розмір лог файлу (MB)
LOG_MAX_SIZE=10

# Кількість backup файлів
LOG_BACKUP_COUNT=5
```

### Отримання API ключів

#### 1. Finnhub API
```bash
# 1. Перейдіть на https://finnhub.io/register
# 2. Зареєструйтеся безкоштовно
# 3. Підтвердіть email
# 4. Скопіюйте API ключ з Dashboard
# 5. Додайте в .env файл: FINNHUB_API_KEY=your_key_here
```

#### 2. Alpha Vantage API
```bash
# 1. Перейдіть на https://www.alphavantage.co/support/#api-key
# 2. Введіть email та отримайте ключ
# 3. Додайте в .env файл: ALPHA_VANTAGE_API_KEY=your_key_here
```

#### 3. Polygon API
```bash
# 1. Перейдіть на https://polygon.io/
# 2. Зареєструйтеся безкоштовно
# 3. Підтвердіть email
# 4. Скопіюйте API ключ
# 5. Додайте в .env файл: POLYGON_API_KEY=your_key_here
```

### Створення директорій

```bash
# Створіть необхідні директорії
mkdir -p cache logs data models exports

# Встановіть права доступу (Linux/macOS)
chmod 755 cache logs data models exports
```

## 🚀 Перший запуск

### Перевірка встановлення

```bash
# Активуйте віртуальне середовище
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Перевірте Python
python --version
# Очікуваний результат: Python 3.8+ (рекомендовано 3.11)

# Перевірте залежності
python -c "import pandas, numpy, sklearn, xgboost; print('All dependencies OK')"

# Перевірте структуру проекту
ls -la
# Повинні бути: main.py, requirements.txt, .env, config/, models/, etc.
```

### Запуск додатку

```bash
# Запустіть головний файл
python main.py
```

### Перший запуск - що очікувати

1. **Перевірка залежностей** (30-60 секунд)
   ```
   Starting Insider Trading Monitor Pro v3.0
   Checking requirements...
   All packages installed successfully!
   ```

2. **Ініціалізація середовища** (10-30 секунд)
   ```
   Environment setup completed
   Loading existing ML models...
   No existing ML models found
   ```

3. **Запуск GUI** (5-10 секунд)
   ```
   Starting GUI...
   Enhanced main window initialized
   ```

4. **Перше завантаження даних** (1-3 хвилини)
   ```
   Fetching insider trades...
   Fetched 45 insider trades from OpenInsider
   Enhanced analysis completed for 45 trades
   ```

### Налаштування після першого запуску

#### 1. Налаштування Watchlist
```bash
# Відредагуйте файл watchlist
# Windows: notepad data/watchlist.txt
# macOS: open -e data/watchlist.txt
# Linux: nano data/watchlist.txt

# Додайте ваші улюблені тікери:
AAPL
MSFT
GOOGL
TSLA
NVDA
```

#### 2. Навчання ML моделей
```bash
# В GUI натисніть кнопку "Навчити ML Моделі"
# Або запустіть через код:
python -c "
from services.enhanced_trading_service import EnhancedTradingService
service = EnhancedTradingService()
result = service.train_ml_models()
print('Training result:', result)
"
```

#### 3. Створення першого портфеля
```bash
# В GUI:
# 1. Перейдіть на вкладку "💼 Портфель"
# 2. Натисніть "Створити"
# 3. Введіть назву: "Мій перший портфель"
# 4. Додайте позиції через форму
```

## 🔧 Усунення неполадок

### Поширені проблеми

#### 1. Помилка встановлення залежностей

**Проблема:**
```bash
ERROR: Failed building wheel for some-package
```

**Рішення:**
```bash
# Windows
pip install --upgrade setuptools wheel
pip install --no-cache-dir -r requirements.txt

# macOS (якщо проблеми з компіляцією)
brew install cmake
export CC=clang
export CXX=clang++
pip install -r requirements.txt

# Ubuntu (встановіть додаткові залежності)
sudo apt install python3-dev build-essential
pip install -r requirements.txt
```

#### 2. Помилка запуску GUI

**Проблема:**
```bash
ModuleNotFoundError: No module named 'tkinter'
```

**Рішення:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (зазвичай вже встановлено)
brew install python-tk
```

#### 3. Проблеми з API ключами

**Проблема:**
```bash
WARNING: Finnhub API key not configured
```

**Рішення:**
```bash
# 1. Перевірте .env файл
cat .env | grep FINNHUB_API_KEY

# 2. Переконайтеся, що ключ правильний
# 3. Перезапустіть додаток
```

#### 4. Повільна робота

**Проблема:**
```bash
Analysis taking too long...
```

**Рішення:**
```bash
# 1. Зменшіть кількість тікерів у watchlist
# 2. Збільшіть інтервали кешування в .env:
CACHE_DURATION_HOURS=6
REQUESTS_PER_MINUTE=30

# 3. Вимкніть ML прогнози для тестування:
AI_PREDICTIONS_ENABLED=false
```

#### 5. Проблеми з пам'яттю

**Проблема:**
```bash
MemoryError: Unable to allocate array
```

**Рішення:**
```bash
# 1. Закрийте інші програми
# 2. Зменшіть розмір даних для ML:
# В коді змініть period="6mo" замість period="2y"

# 3. Увімкніть swap (Linux):
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Діагностичні команди

```bash
# Перевірка системи
python -c "
import sys, platform
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Architecture: {platform.architecture()}')
"

# Перевірка пам'яті
python -c "
import psutil
print(f'RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB')
print(f'Available: {psutil.virtual_memory().available / (1024**3):.1f} GB')
"

# Перевірка залежностей
python -c "
import pkg_resources
installed = [d.project_name for d in pkg_resources.working_set]
required = ['pandas', 'numpy', 'scikit-learn', 'xgboost', 'yfinance']
missing = [pkg for pkg in required if pkg not in installed]
print('Missing packages:', missing if missing else 'None')
"

# Перевірка API з'єднань
python -c "
import requests
try:
    r = requests.get('https://finnhub.io/api/v1/quote?symbol=AAPL&token=demo', timeout=5)
    print('Finnhub API:', 'OK' if r.status_code == 200 else 'Error')
except:
    print('Finnhub API: Connection failed')
"
```

### Логи та діагностика

```bash
# Перегляд логів
# Windows: type logs\insider_trading.log
# macOS/Linux: tail -f logs/insider_trading.log

# Пошук помилок в логах
grep -i error logs/insider_trading.log

# Перегляд останніх 50 рядків
tail -n 50 logs/insider_trading.log

# Очищення логів (якщо потрібно)
# Windows: del logs\insider_trading.log
# macOS/Linux: rm logs/insider_trading.log
```

## 🔄 Оновлення

### Оновлення до нової версії

```bash
# 1. Зробіть backup поточної версії
cp -r insider-trading-monitor-v3 insider-trading-monitor-v3-backup

# 2. Завантажте нову версію
git pull origin main
# Або завантажте новий ZIP архів

# 3. Оновіть залежності
pip install -r requirements.txt --upgrade

# 4. Перенесіть конфігурацію
cp insider-trading-monitor-v3-backup/.env .env
cp -r insider-trading-monitor-v3-backup/data/* data/

# 5. Запустіть міграції (якщо потрібно)
python migrate.py

# 6. Перезапустіть додаток
python main.py
```

### Автоматичне оновлення

```bash
# Створіть скрипт оновлення (update.sh)
#!/bin/bash
echo "Updating Insider Trading Monitor Pro..."

# Backup
cp .env .env.backup
cp -r data data.backup

# Update
git pull origin main
pip install -r requirements.txt --upgrade

# Restore config
cp .env.backup .env

echo "Update completed!"
```

### Перевірка версії

```bash
# В додатку
python -c "
from config.settings import settings
print('Version: 3.0')
print('Python:', sys.version)
print('Last updated:', datetime.now())
"

# Через GUI
# Меню -> Про програму -> Версія
```

## 📞 Підтримка

### Отримання допомоги

1. **Документація**: Прочитайте README_v3.md та TECHNICAL_DOCUMENTATION.md
2. **GitHub Issues**: https://github.com/your-repo/insider-trading-monitor/issues
3. **Email**: support@insider-trading-monitor.com
4. **Telegram**: @InsiderTradingMonitor

### Повідомлення про баги

```bash
# Зберіть діагностичну інформацію
python -c "
import sys, platform, pkg_resources
print('=== SYSTEM INFO ===')
print(f'OS: {platform.platform()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.architecture()}')
print('\n=== INSTALLED PACKAGES ===')
for d in pkg_resources.working_set:
    print(f'{d.project_name}=={d.version}')
" > debug_info.txt

# Додайте логи
tail -n 100 logs/insider_trading.log >> debug_info.txt

# Відправте debug_info.txt разом з описом проблеми
```

### Корисні ресурси

- **Офіційна документація**: [README_v3.md](README_v3.md)
- **Технічна документація**: [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
- **Приклади використання**: [examples/](examples/)
- **FAQ**: [FAQ.md](FAQ.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Вітаємо з успішним встановленням Insider Trading Monitor Pro v3.0!** 🎉

Тепер ви готові до професійного аналізу інсайдерських торгів з використанням найсучасніших технологій машинного навчання та ризик-менеджменту.

*Якщо у вас виникли питання, не соромтеся звертатися за підтримкою!*