Set Alert for NSE Shares
This project analyzes National Stock Exchange (NSE) stocks by calculating Price-to-Earnings (P/E), Price-to-Book (P/B), and Exponential Moving Average (EMA) metrics, sending Telegram alerts when user-defined thresholds are breached. A GitHub Action runs the analysis daily at 6:00 PM IST (12:30 PM UTC), using Yahoo Finance (yfinance) data and python-telegram-bot for notifications.
Features

Financial Metrics:
P/E Ratio: Trailing 12-month EPS-based (from yfinance trailingPE and calculated as Price / TTM EPS).
P/B Ratio: Book value-based (from yfinance priceToBook and calculated as Price / Book Value).
EMA: 20-day Exponential Moving Average for trend analysis.


Threshold Alerts:
P/E and P/B: Alerts if metrics are less than ("lt") or greater than ("gt") the threshold.
EMA:
"lt": Alerts if previous day's closing price > current day's closing price and previous day's EMA > current EMA.
"gt": Alerts if current EMA is above the threshold.




Automation: GitHub Action executes daily at 6:00 PM IST.
Output: Saves results to a CSV and displays metrics in the console.
Configurable Input: Define stocks, thresholds, and comparison ("gt" or "lt") via nse_stocks.json.

Repository Structure
set_alart_for_nse_shares/
├── calculate_pe_ema_pb_ratios.py    # Python script for analysis and alerts
├── nse_stocks.json                  # Input JSON with stock codes and thresholds
├── .github/
│   └── workflows/
│       └── run_stock_analysis.yml    # GitHub Action workflow
└── README.md                        # Project documentation

Prerequisites

Python 3.9+ (recommend 3.10+ to avoid urllib3 warnings on macOS).
GitHub Account: For forking and hosting the repository.
Telegram Bot:
Create a bot via @BotFather to get a bot token (e.g., 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11).
Get a chat ID (e.g., 123456789) using @userinfobot or @GetIDsBot.


SSH Key: For Git operations (optional, HTTPS with PAT also supported).

Setup Instructions
1. Fork the Repository
To use or contribute, fork the repository:

Go to the repository on GitHub.
Click Fork (top-right) to create a copy under your GitHub account.
Clone your fork:git clone git@github.com:YOUR_USERNAME/set_alart_for_nse_shares.git
cd set_alart_for_nse_shares


Replace YOUR_USERNAME with your GitHub username.
For HTTPS:git clone https://github.com/YOUR_USERNAME/set_alart_for_nse_shares.git





2. Install Dependencies
Set up a virtual environment and install libraries:
python3 -m venv venv
source venv/bin/activate
pip install yfinance pandas numpy python-telegram-bot

3. Configure nse_stocks.json
Edit nse_stocks.json to specify stocks, thresholds, and comparison. Two formats are supported:
Format 1: Stocks with Thresholds (Recommended)
[
    {
        "name": "RELIANCE.NS",
        "threshold_type": "EMA",
        "threshold_number": 2800,
        "comparison": "lt"
    },
    {
        "name": "HDFCBANK.NS",
        "threshold_type": "PE",
        "threshold_number": 20,
        "comparison": "lt"
    },
    {
        "name": "TCS.NS",
        "threshold_type": "PB",
        "threshold_number": 2,
        "comparison": "gt"
    }
]


Fields:
name: NSE stock ticker (e.g., RELIANCE.NS, must end with .NS).
threshold_type: "PE", "EMA", or "PB".
threshold_number: Numeric threshold (e.g., 2800 for EMA, 20 for P/E, 2 for P/B).
comparison: "gt" (greater than) or "lt" (less than, default).


Alert Logic:
P/E, P/B: Alerts if metric is < (for "lt") or > (for "gt") the threshold.
EMA:
"lt": Alerts if previous day's close > current day's close and previous day's EMA > current EMA.
"gt": Alerts if current EMA > threshold.





Format 2: Simple Stock List
{
    "stocks": ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]
}


Behavior: Analyzes stocks without thresholds or alerts.

4. Set Up Telegram Notifications
Configure Telegram for alerts:
Create a Telegram Bot

In Telegram, start a chat with @BotFather.
Send /newbot, name your bot, and receive a bot token (e.g., 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11).
Copy the token securely.

Get Chat ID

Message your bot or add it to a group.
Use @userinfobot or @GetIDsBot to get the chat ID (e.g., 123456789).
Alternatively, check https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates after messaging the bot.

Local Testing
Test alerts locally:
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
python3 calculate_pe_ema_pb_ratios.py


Verify alerts in your Telegram chat.

GitHub Secrets for Actions
Store credentials in GitHub Secrets for the Action:

Go to your forked repository’s Settings > Secrets and variables > Actions > New repository secret.
Add:
Name: TELEGRAM_BOT_TOKEN, Value: Your bot token.
Name: TELEGRAM_CHAT_ID, Value: Your chat ID.


Confirm secrets are listed under Repository secrets.

5. Test Locally
Run the script:
python3 calculate_pe_ema_pb_ratios.py


Output:
Console: Alerts (e.g., ALERT: RELIANCE.NS EMA conditions met: Previous close (2810.00) > Current close (2800.50), Previous EMA (2760.00) > Current EMA (2750.30)!) and results table.
Telegram: Alerts sent to the chat.
CSV: Results in pe_pb_ema_ratios_YYYYMMDD_HHMMSS.csv with columns: ticker, current_price, ttm_eps, pe_ratio, calculated_pe_ratio, book_value, pb_ratio, calculated_pb_ratio, ema, prev_day_close, current_day_close, prev_day_ema, threshold_type, threshold_number, comparison.



6. Configure GitHub Action
The GitHub Action (run_stock_analysis.yml) runs daily at 6:00 PM IST (12:30 PM UTC).
Workflow Details

Schedule: Cron 30 12 * * *.
Steps: Checks out repository, sets up Python 3.9, installs dependencies, runs script.
Environment: Uses TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID secrets.

Verify Action

Visit your repository’s Actions tab.
Workflow runs daily or can be triggered manually (Run workflow).
Check logs for execution and alerts.

Example Output
Console and Telegram (example):
ALERT: RELIANCE.NS EMA conditions met: Previous close (2810.00) > Current close (2800.50), Previous EMA (2760.00) > Current EMA (2750.30)!
ALERT: HDFCBANK.NS P/E ratio (19.50) is below threshold (20.0)!

P/E, P/B, and EMA Results:
         ticker current_price ttm_eps pe_ratio calculated_pe_ratio book_value pb_ratio calculated_pb_ratio     ema prev_day_close current_day_close prev_day_ema threshold_type threshold_number comparison
0  RELIANCE.NS       2800.50   95.20    29.42              29.42    1100.50     2.54                2.54  2750.30        2810.00          2800.50      2760.00            EMA           2800.0         lt
1  HDFCBANK.NS       1450.25   70.10    19.50              19.50     900.75     1.61                1.61  1420.75        1445.00          1450.25      1415.00             PE             20.0         lt
2      TCS.NS       3900.75  120.50    32.37              32.37    2167.10     1.80                1.80  3850.40        3890.00          3900.75      3840.00             PB              2.0         gt

CSV (pe_pb_ema_ratios_20250522_054412.csv):
ticker,current_price,ttm_eps,pe_ratio,calculated_pe_ratio,book_value,pb_ratio,calculated_pb_ratio,ema,prev_day_close,current_day_close,prev_day_ema,threshold_type,threshold_number,comparison
RELIANCE.NS,2800.50,95.20,29.42,29.42,1100.50,2.54,2.54,2750.30,2810.00,2800.50,2760.00,EMA,2800.0,lt
HDFCBANK.NS,1450.25,70.10,19.50,19.50,900.75,1.61,1.61,1420.75,1445.00,1450.25,1415.00,PE,20.0,lt
TCS.NS,3900.75,120.50,32.37,32.37,2167.10,1.80,1.80,3850.40,3890.00,3900.75,3840.00,PB,2.0,gt

Contributing
Contributions are welcome! To contribute:

Fork the repository (see step 1).
Clone your fork:git clone git@github.com:YOUR_USERNAME/set_alart_for_nse_shares.git


Create a branch:git checkout -b feature-name


Commit changes:git commit -m "Add feature"


Push to your fork:git push origin feature-name


Open a pull request to the original repository’s main branch.

Troubleshooting

Git Error: .github/workflows/ does not have a commit checked out:
Caused by an uninitialized or submodule .github/ directory.
Fix:rm -rf .github
git rm --cached .github
mkdir -p .github/workflows
touch .github/workflows/run_stock_analysis.yml
git add .github/workflows/run_stock_analysis.yml
git commit -m "Fix .github directory"
git push origin main




urllib3 Warning (macOS LibreSSL):
Local issue with Python 3.9. Use Python 3.10+:python3 -m venv venv
source venv/bin/activate
pip install yfinance pandas numpy python-telegram-bot


GitHub Actions (on ubuntu-latest) are unaffected.


No Telegram Alerts:
Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in GitHub Secrets or local environment.
Ensure bot is added to the chat and not blocked.
Test locally to isolate issues.


Action Fails:
Check Actions tab logs.
Confirm nse_stocks.json exists.
Verify secrets are set.


Push Errors:
For SSH: Ensure key is added (ssh -T git@github.com).
For HTTPS: Use a PAT with repo scope:git config --global credential.helper osxkeychain





Notes

Repository Name: The typo set_alart_for_nse_shares is intentional. To rename to set_alert_for_nse_shares:
On GitHub: Settings > Change repository name.
Locally:git remote set-url origin git@github.com:YOUR_USERNAME/set_alert_for_nse_shares.git




CSV Persistence: CSVs are temporary in Actions. To save:- name: Upload CSV artifact
  uses: actions/upload-artifact@v4
  with:
    name: stock-analysis-results
    path: pe_pb_ema_ratios_*.csv

Add to .github/workflows/run_stock_analysis.yml.
EMA Period: Fixed at 20 days. Customize in calculate_pe_ratios or add per-stock periods in nse_stocks.json.
Performance: yfinance may be slow for many stocks. Consider batching for large lists.

License
MIT License. See LICENSE for details (create a LICENSE file if needed).
Contact
Open a GitHub Issue for questions or issues.

