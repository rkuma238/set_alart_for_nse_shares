Set Alert for NSE Shares
This project analyzes National Stock Exchange (NSE) stocks by calculating Price-to-Earnings (P/E), Price-to-Book (P/B), and Exponential Moving Average (EMA) metrics, sending Telegram alerts when user-defined thresholds are breached. A GitHub Action runs the analysis daily at 6:00 PM IST (12:30 PM UTC), using Yahoo Finance (yfinance) data and python-telegram-bot for notifications.
Features

Financial Metrics:
P/E Ratio: Trailing 12-month EPS-based (from yfinance trailingPE and calculated as Price / TTM EPS).
P/B Ratio: Book value-based (from yfinance priceToBook and calculated as Price / Book Value).
EMA: 20-day Exponential Moving Average for trend analysis.


Threshold Alerts: Sends Telegram messages when P/E, P/B, or EMA falls below specified thresholds.
Automation: GitHub Action executes the script daily at 6:00 PM IST.
Output: Saves results to a CSV file and displays metrics in the console.
Configurable Input: Define stocks and thresholds via nse_stocks.json.

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
Create a bot via @BotFather in Telegram to get a bot token (e.g., 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11).
Get a chat ID (e.g., 123456789) using @userinfobot or by messaging the bot and checking with @GetIDsBot.


SSH Key: For Git operations (optional but recommended over HTTPS).

Setup Instructions
1. Fork the Repository
To use or contribute to this project, fork the repository to your GitHub account:

Go to the repository on GitHub.
Click the Fork button (top-right) to create a copy under your GitHub account.
Clone your forked repository:git clone git@github.com:YOUR_USERNAME/set_alart_for_nse_shares.git
cd set_alart_for_nse_shares


Replace YOUR_USERNAME with your GitHub username.
If using HTTPS:git clone https://github.com:YOUR_USERNAME/set_alart_for_nse_shares.git





2. Install Dependencies
Set up a virtual environment and install required libraries:
python3 -m venv venv
source venv/bin/activate
pip install yfinance pandas numpy python-telegram-bot

3. Configure nse_stocks.json
Edit nse_stocks.json to specify NSE stocks and thresholds. Two formats are supported:
Format 1: Stocks with Thresholds (Recommended)
[
    {
        "name": "RELIANCE.NS",
        "threshold_type": "EMA",
        "threshold_number": 10
    },
    {
        "name": "HDFCBANK.NS",
        "threshold_type": "PE",
        "threshold_number": 20
    },
    {
        "name": "TCS.NS",
        "threshold_type": "PB",
        "threshold_number": 2
    }
]


Fields:
name: NSE stock ticker (e.g., RELIANCE.NS, must end with .NS).
threshold_type: "PE", "EMA", or "PB".
threshold_number: Numeric threshold (e.g., 20 for P/E, 2 for P/B, 10 for EMA).


Behavior: Alerts are sent if the metric falls below the threshold.

Format 2: Simple Stock List
{
    "stocks": ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]
}


Behavior: Analyzes stocks without threshold checks (no alerts).

4. Set Up Telegram Notifications
The script sends alerts to a Telegram chat. Configure the bot and chat ID:
Create a Telegram Bot

Open Telegram and start a chat with @BotFather.
Send /newbot, name your bot, and receive a bot token (e.g., 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11).
Copy the token securely.

Get Chat ID

Start a chat with your bot or add it to a group.
Send a message, then use @userinfobot or @GetIDsBot to get the chat ID (e.g., 123456789).
Alternatively, message the bot and check the ID via a service like https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates.

Local Testing
Test Telegram alerts locally:
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
python3 calculate_pe_ema_pb_ratios.py


Verify alerts appear in your Telegram chat.

GitHub Secrets for Actions
For the GitHub Action to send Telegram alerts, store credentials in GitHub Secrets:

Go to your forked repository on GitHub.
Navigate to Settings > Secrets and variables > Actions > New repository secret.
Add two secrets:
Name: TELEGRAM_BOT_TOKEN
Value: Your Telegram bot token.


Name: TELEGRAM_CHAT_ID
Value: Your Telegram chat ID.




Verify secrets are listed under Repository secrets.

5. Test Locally
Run the script to ensure it works:
python3 calculate_pe_ema_pb_ratios.py


Output:
Console: Alerts (e.g., ALERT: HDFCBANK.NS P/E ratio (19.50) is below threshold (20.0)!) and a results table.
Telegram: Alerts sent to the specified chat.
CSV: Results saved to pe_pb_ema_ratios_YYYYMMDD_HHMMSS.csv with columns: ticker, current_price, ttm_eps, pe_ratio, calculated_pe_ratio, book_value, pb_ratio, calculated_pb_ratio, ema, threshold_type, threshold_number.



6. Configure GitHub Action
The GitHub Action (run_stock_analysis.yml) runs daily at 6:00 PM IST (12:30 PM UTC).
Workflow Details

Schedule: Cron 30 12 * * * (12:30 PM UTC).
Steps: Checks out the repository, sets up Python 3.9, installs dependencies, and runs the script.
Environment: Uses TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from secrets.

Verify Action

Visit your repository’s Actions tab.
The workflow runs daily or can be triggered manually (Run workflow).
Check logs for execution details and Telegram alerts.

Example Output
Console and Telegram:
ALERT: HDFCBANK.NS P/E ratio (19.50) is below threshold (20.0)!
ALERT: TCS.NS P/B ratio (1.80) is below threshold (2.0)!

P/E, P/B, and EMA Results:
         ticker current_price ttm_eps pe_ratio calculated_pe_ratio book_value pb_ratio calculated_pb_ratio     ema threshold_type threshold_number
0  RELIANCE.NS       2800.50   95.20    29.42              29.42    1100.50     2.54                2.54  2750.30           EMA             10.0
1  HDFCBANK.NS       1450.25   70.10    19.50              19.50     900.75     1.61                1.61  1420.75            PE             20.0
2      TCS.NS       3900.75  120.50    32.37              32.37    2167.10     1.80                1.80  3850.40            PB              2.0

CSV (pe_pb_ema_ratios_20250520_225123.csv):
ticker,current_price,ttm_eps,pe_ratio,calculated_pe_ratio,book_value,pb_ratio,calculated_pb_ratio,ema,threshold_type,threshold_number
RELIANCE.NS,2800.50,95.20,29.42,29.42,1100.50,2.54,2.54,2750.30,EMA,10.0
HDFCBANK.NS,1450.25,70.10,19.50,19.50,900.75,1.61,1.61,1420.75,PE,20.0
TCS.NS,3900.75,120.50,32.37,32.37,2167.10,1.80,1.80,3850.40,PB,2.0

Contributing
Contributions are welcome! To contribute:

Fork the repository (see step 1).
Clone your fork:git clone git@github.com:YOUR_USERNAME/set_alart_for_nse_shares.git


Create a branch:git checkout -b feature-name


Make changes and commit:git commit -m "Add feature"


Push to your fork:git push origin feature-name


Open a pull request from your fork’s branch to the original repository’s main branch.

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
Local issue with Python 3.9’s LibreSSL. Use Python 3.10+:python3 -m venv venv
source venv/bin/activate
pip install yfinance pandas numpy python-telegram-bot


GitHub Actions (on ubuntu-latest) are unaffected.


No Telegram Alerts:
Verify TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in GitHub Secrets or local environment variables.
Ensure the bot is added to the chat and not blocked.
Test locally to isolate issues.


Action Fails:
Check Actions tab logs.
Confirm nse_stocks.json exists in the repository.
Verify secrets are correctly named.


Push Errors:
For SSH: Ensure key is added (ssh -T git@github.com).
For HTTPS: Use a Personal Access Token (PAT) with repo scope:git config --global credential.helper osxkeychain





Notes

Repository Name: The typo set_alart_for_nse_shares (should be alert) is intentional. To rename:
On GitHub: Settings > Change repository name.
Locally:git remote set-url origin git@github.com:YOUR_USERNAME/set_alert_for_nse_shares.git




CSV Persistence: The CSV is temporary in Actions. To save:- name: Upload CSV artifact
  uses: actions/upload-artifact@v4
  with:
    name: stock-analysis-results
    path: pe_pb_ema_ratios_*.csv

Add to .github/workflows/run_stock_analysis.yml.
EMA Period: Fixed at 20 days. Customize by editing ema_period in calculate_pe_ratios or adding per-stock periods in nse_stocks.json.
Performance: yfinance may be slow for many stocks. Consider batching for large lists.

License
This project is licensed under the MIT License. See LICENSE for details (create a LICENSE file if needed).
Contact
For questions or issues, open a GitHub Issue in the repository.

