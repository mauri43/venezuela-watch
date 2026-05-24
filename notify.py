"""Discord webhook alert for newly-released Caracas flights."""

import os
import httpx

from search import Finding

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")


def _route_str(f: Finding) -> str:
    if not f.legs:
        return f"{f.origin} → {f.dest_code}"
    chain = [f.legs[0].from_code] + [l.to_code for l in f.legs]
    return " → ".join(chain)


def _embed(f: Finding) -> dict:
    stops = "Nonstop" if f.stops == 0 else f"{f.stops} stop{'s' if f.stops > 1 else ''}"
    title_prefix = "🦅 AA via MIA " if f.is_aa_via_mia else "🇻🇪 "
    color = 0x0078D2 if f.is_aa_via_mia else 0xCE1126  # AA blue vs Venezuelan red
    return {
        "title": f"{title_prefix}{_route_str(f)} — live!",
        "url": f.flights_url,
        "color": color,
        "fields": [
            {"name": "📅 Depart (one-way)", "value": f.depart, "inline": True},
            {"name": "💵 Lowest seen", "value": f"${f.price}", "inline": True},
            {"name": "✈️ Airline", "value": f.airline or "?", "inline": True},
            {"name": "🛬 Stops", "value": stops, "inline": True},
        ],
        "footer": {"text": "Tap title to open Google Flights and book"},
    }


def send_release_alert(new_findings: list[Finding]) -> bool:
    if not new_findings:
        return False
    if not DISCORD_WEBHOOK:
        print("[discord] DISCORD_WEBHOOK not set — skipping alert")
        return False

    aa_hits = [f for f in new_findings if f.is_aa_via_mia]
    other_hits = [f for f in new_findings if not f.is_aa_via_mia]

    # Send the AA-via-MIA alert FIRST as a separate, louder message
    if aa_hits:
        aa_lines = [
            f"• **{f.origin}→MIA→CCS** {f.depart} — ${f.price} ({f.airline}, "
            f"{'nonstop legs' if f.stops == 1 else f'{f.stops} stops'})"
            for f in sorted(aa_hits, key=lambda x: x.depart)
        ]
        aa_header = {
            "title": "🦅🚨 AMERICAN VIA MIAMI — Caracas flights LIVE",
            "description": (
                f"**{len(aa_hits)} AA itinerary(ies) just opened DC→MIA→CCS.**\n"
                "Book NOW.\n\n" + "\n".join(aa_lines)
            ),
            "color": 0x0078D2,
        }
        payload = {
            "username": "Venezuela Watch",
            "content": "🦅🚨 **@here** American Caracas service is LIVE!",
            "embeds": [aa_header] + [_embed(f) for f in aa_hits[:9]],
        }
        try:
            r = httpx.post(DISCORD_WEBHOOK, json=payload, timeout=15)
            r.raise_for_status()
            print(f"[discord] sent AA-via-MIA alert ({len(aa_hits)} findings)")
        except Exception as e:
            print(f"[discord] AA alert error: {e}")

    # Send the general release alert for everything else
    if other_hits:
        lines = [
            f"• **{f.origin}→{f.dest_code}** {f.depart} — ${f.price} ({f.airline}, "
            f"{'nonstop' if f.stops == 0 else f'{f.stops} stop'})"
            for f in sorted(other_hits, key=lambda x: x.depart)
        ]
        header = {
            "title": "🇻🇪🚨 Caracas flights just released",
            "description": (
                f"**{len(other_hits)} new route/date combo(s) now show availability.**\n\n"
                + "\n".join(lines)
            ),
            "color": 0xFCDD09,
        }
        payload = {
            "username": "Venezuela Watch",
            "content": "🚨 **@here** Caracas flights just opened up!",
            "embeds": [header] + [_embed(f) for f in other_hits[:9]],
        }
        try:
            r = httpx.post(DISCORD_WEBHOOK, json=payload, timeout=15)
            r.raise_for_status()
            print(f"[discord] sent general alert ({len(other_hits)} findings)")
        except Exception as e:
            print(f"[discord] general alert error: {e}")

    return True


def send_heartbeat_if_quiet(findings_count: int) -> None:
    print(f"[heartbeat] scan complete, {findings_count} total availabilities, no NEW releases")
