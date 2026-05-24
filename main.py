#!/usr/bin/env python3
"""Venezuela flight release watcher.

Polls DC airports → Venezuela for December dates. When a route+date that
previously had NO flights suddenly shows availability, fires a Discord alert.
"""

import sys
from dotenv import load_dotenv

load_dotenv()

from search import scan_all
from state import diff_new_releases, load_state, save_state, update_state
from notify import send_heartbeat_if_quiet, send_release_alert


def main() -> int:
    print("=" * 60)
    print("VENEZUELA WATCH — DC airports → CCS/MAR/VLN/PMV, December")
    print("=" * 60)

    findings = scan_all()
    state = load_state()
    new = diff_new_releases(findings, state)

    if new:
        print(f"\n🚨 {len(new)} NEW release(s) detected — alerting Discord")
        send_release_alert(new)
    else:
        send_heartbeat_if_quiet(len(findings))

    update_state(findings, state)
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
