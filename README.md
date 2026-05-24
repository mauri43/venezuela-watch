# Venezuela Watch 🇻🇪

Polls Google Flights for **DC airports → Venezuela** in December and sends a
Discord alert the moment availability shows up. Built because no one knows
*when* American (or anyone) will release the route — and you can't be awake 24/7.

## What it watches

- **Origins:** IAD, DCA, BWI
- **Destinations:** CCS, MAR, VLN, PMV
- **Dates:** Dec 5, 12, 19, 22, 26, 29 (2026) — round-trip, 7-night
- **Trigger:** any route+date that flips from "no flights" → "flights available"

State is persisted in `state.json`. Only newly-released combos trigger an alert,
so you don't get spammed every hour once flights are live.

## Setup

1. Push this directory to a new GitHub repo.
2. Add a repo secret: `DISCORD_WEBHOOK` = your Discord webhook URL.
3. Done. The Actions workflow runs hourly on its own.

Local testing:

```bash
cd venezuela-watch
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in DISCORD_WEBHOOK
python main.py
```

## Tuning

Edit `config.py` to add/remove airports, dates, or change the trip length and
allowed stop count.
