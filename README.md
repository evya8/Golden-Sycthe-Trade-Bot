# Golden Scythe Trade Bot ⚔️

A sophisticated, automated trading bot designed to manage and execute trades based on customizable strategy and market data. It integrates with the Alpaca API and features a momentum-based trading strategy.

Video Showcase - https://www.youtube.com/watch?v=PcGJbvUQ9JE

## 🌟 Features

- **Automated Trade Execution**: Executes buy and sell orders automatically based on signals.
- **User-Defined Filters**: Set filters based on symbols, sectors, and custom parameters.
- **Multiple Users**: Supporting multiple users while keeping sensitive data secure.
- **Bot Monitor**: Tracks every stage of the trade process for easy analysis.
- **Bot Performance**: Track the bot trades performance visually.
- **Account Tracking**: Displays all open positions and actions in the user account.
- **Backtesting**: Backtesting the strategy on different stocks, timeframes and trade frequencies.
- **Django + React Frontend**: A modern user interface for real-time bot monitoring and management.
- **MySQL Database**: Storing passwords and API keys in a secure manner as well as logging user and bot data.
- **Dark Mode UI**: Stylish interface with Material-UI (MUI) and a sleek dark theme.

---


![Monitor the Bot Process and Progress](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Dashboard%20-%20Stock%20Updates%2C%20News%20Feed%2C%20User%20Configurations.png)

![Monitor the Bot Process and Progress](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Dashboard%20-%20Bot%20Monitor.png)

![Backtest the Strategy - Get Detailed Graphs](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Dashboard%20-%20Bot%20Performance%20Tracking.png)

![Keep Track On Your Account](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Dashboard%20-%20Account.png)

![Backtest the Strategy - Get Stats and Insights](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Backtesting%20-%20User%20Configurations%2C%20Mid%20Frequency.png)

![Instructions For Getting Alpaca's API Keys](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Backtesting%20-%20Interactive%20Graphs%2C%20Mid%20Frequency.png)

![Backtest the Strategy - Get Stats and Insights](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/Backtesting%20-%20Returns%2C%20Metrics%2C%20Mid%20Frequency.png)

![Backtest the Strategy - Get Stats and Insights](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/API%20Keys%20-%20Detailed%20Instructions.png)

![Backtest the Strategy - Get Stats and Insights](https://github.com/evya8/Golden-Sycthe-Trade-Bot/blob/master/Screenshots/API%20Keys%20-%20Generate%20Keys%2C%20Saving%20In%20App.png)



## 📦 Installation

1. **Clone the Repository:**
  
   git clone https://github.com/evya8/golden-scythe-bot.git
   cd golden-scythe-bot


Create and Activate a Virtual Environment (Optional but Recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

Install Frontend Dependencies: Navigate to the frontend directory and install dependencies:
cd frontend
npm install


🚀 Usage

Run Backend (Django): Navigate back to the root directory and start the Django server:
python manage.py runserver

Run Frontend (React): Open another terminal, navigate to the frontend folder, and start the React development server:
cd frontend
npm start

Activate Your Bot: Once the server is running, login through the UI and toggle the bot activation in the dashboard.

Schedule the Bot: The bot is designed to run during US market hours. Make sure to configure the scheduler in the Django app (AppConfig) to start the bot.

🔧 Configuration

Alpaca API Keys:
Obtain your API keys from Alpaca.
Set your API keys securely by saving them to the database. 

Timezone:
The bot operates in US/Eastern time to align with market hours.
Ensure uniform time settings across the Django backend and React frontend.
Display local time for users.

📊 Logs & Monitoring
All bot operations are logged to the database for real-time and historical analysis. You can view:

First Screening: Stocks that passed the initial filters.
Indicator Signals: Buy or sell signals generated by indicators.
Order Status: Confirmation of executed trades or failure reasons.

Error Handling
The bot's performance and errors are tracked in the BotOperations table with detailed status and timestamp logging.

🛠️ Development

Backend:
Django for API and logic.
Django Rest Framework (DRF) for API endpoints.
JWT Authentication for secure user access.

Frontend:
React for a responsive, real-time dashboard.
Material-UI (MUI) for a modern, dark-mode UI.
Axios for API requests, with token management via interceptors.

📋 Future Improvements
Implement dynamic grid adjustments based on volatility.
Add advanced risk management features like trailing stop-loss.
Incorporate more technical indicators for diversified strategies.
Mobile app integration for real-time notifications.

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the bot.

✨ Acknowledgments
Thanks to Alpaca for providing the API to access stock market data and execute trades in the market.
Special mention to the developers behind Django, React, and Material-UI for powering the core tech stack.
vbnet
