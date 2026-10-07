# Currency Rate Emailer

Emails a summary of exchange rates for a watchlist of currencies -> VND,
compared across five independent sources (market mid-rate, Vietcombank,
fawazahmed0/currency-api, fxratesapi.com, and CoinGecko via USDT).

The email includes a best-rate highlight, a cross-source discrepancy alert, a
side-by-side comparison table, quick VND conversions, and a weekly 7-day
trend. See the docstring at the top of `currency_rate_emailer.py` for the full
details.

`email_preview.html` shows what the email looks like.

## Setup

1. Add these secrets under Settings -> Secrets and variables -> Actions:
   - `GMAIL_ADDRESS`: your Gmail address
   - `GMAIL_APP_PASSWORD`: a Gmail App Password (https://myaccount.google.com/apppasswords)
   - `CURRENCY_RECIPIENT`: where to send the email
2. Optional: add **Variables** (same page, Variables tab) to change the
   defaults: `WATCHLIST`, `ALERT_THRESHOLD_PERCENT` (only email when a rate
   moved at least this much; unset = every run), `DISCREPANCY_THRESHOLD_PERCENT`,
   `CONVERT_AMOUNTS_VND`.
3. Test it: Actions tab -> "Send Currency Rate Summary" -> Run workflow.

It runs every 30 minutes (`.github/workflows/send-currency-rate.yml`) and
commits `last_rates.json` and `rate_history.csv` back to the repo after each
run; the history feeds the weekly trend sent with the Monday 00:xx run
(Vietnam time).

The workflow and `requirements.txt` were rebuilt after the original repo was
lost; the script itself is the original.

## Running it locally

```
pip install requests
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="16-char-app-password"
export CURRENCY_RECIPIENT="where-to-send@example.com"
python currency_rate_emailer.py generate   # fetch rates, build the email
python currency_rate_emailer.py send       # send it via Gmail
```

Optional settings: `WATCHLIST`, `CONVERT_AMOUNTS_VND`,
`ALERT_THRESHOLD_PERCENT`, `DISCREPANCY_THRESHOLD_PERCENT`.
