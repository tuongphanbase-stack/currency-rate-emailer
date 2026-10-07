# Currency Rate Emailer

Emails a summary of exchange rates for a watchlist of currencies -> VND,
compared across five independent sources (market mid-rate, Vietcombank,
fawazahmed0/currency-api, fxratesapi.com, and CoinGecko via USDT).

The email includes a best-rate highlight, a cross-source discrepancy alert, a
side-by-side comparison table, quick VND conversions, and a weekly 7-day
trend. See the docstring at the top of `currency_rate_emailer.py` for the full
details.

`email_preview.html` shows what the email looks like.

## Status: partially restored

Only `currency_rate_emailer.py` and `email_preview.html` survived. Still
missing:

- `.github/workflows/send-currency-rate.yml` (the scheduled GitHub Actions run)
- `requirements.txt` (the script needs `requests`)

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
