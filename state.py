"""Persist which (origin, dest, depart) combos currently show flights, so we
can alert on the false→true transition (i.e. flights newly released)."""

import json
import os
from dataclasses import asdict
from typing import Iterable

from search import Finding

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")


def _key(f: Finding) -> str:
    aa_tag = "AA" if f.is_aa_via_mia else "ANY"
    return f"{f.origin}|{f.dest_code}|{f.depart}|{aa_tag}"


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"seen": {}}
    try:
        with open(STATE_FILE) as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {"seen": {}}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)


def diff_new_releases(findings: Iterable[Finding], state: dict) -> list[Finding]:
    """Return findings that were NOT previously in state — the "newly released"."""
    seen: dict = state.get("seen", {})
    new = []
    for f in findings:
        if _key(f) not in seen:
            new.append(f)
    return new


def update_state(findings: Iterable[Finding], state: dict) -> dict:
    """Replace state with current snapshot — only keys currently available remain."""
    seen = {}
    for f in findings:
        seen[_key(f)] = {
            "price": f.price,
            "airline": f.airline,
            "stops": f.stops,
        }
    state["seen"] = seen
    return state
