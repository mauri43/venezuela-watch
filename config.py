"""Venezuela flight release watcher — configuration."""

from datetime import date, timedelta

# DC-area origins (BWI dropped — basically no international service)
ORIGINS = ["IAD", "DCA"]

# Caracas only
DESTINATIONS = [
    ("CCS", "Caracas (Maiquetía)"),
]

# Outbound: every day from Dec 10 through Dec 25, 2026 (inclusive). One-way only.
_OUTBOUND_START = date(2026, 12, 10)
_OUTBOUND_END = date(2026, 12, 25)


def _date_range(start: date, end: date) -> list[date]:
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


OUTBOUND_DATES = _date_range(_OUTBOUND_START, _OUTBOUND_END)

# Direct or one-stop only (MIA connection welcome)
MAX_STOPS = 1

# American + MIA hub = the loud-alert path
PREFERRED_HUB = "MIA"
PREFERRED_AIRLINE = "American"

# Polite delay between requests
REQUEST_DELAY_MIN = 2.0
REQUEST_DELAY_MAX = 3.5
