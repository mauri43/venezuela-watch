"""Venezuela flight release watcher — configuration."""

from datetime import date, timedelta

# DC-area origins
ORIGINS = ["IAD", "DCA", "BWI"]

# Caracas only
DESTINATIONS = [
    ("CCS", "Caracas (Maiquetía)"),
]

# Outbound: every day strictly AFTER Dec 10, 2026 through end of December.
_OUTBOUND_START = date(2026, 12, 11)
_OUTBOUND_END = date(2026, 12, 31)

# Returns: dates strictly AFTER Jan 5, 2027.
RETURN_DATES = [
    date(2027, 1, 10),
    date(2027, 1, 24),
]


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
