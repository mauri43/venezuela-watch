"""Search Google Flights for one-way DC→Caracas availability via fast-flights."""

import random
import time
from dataclasses import dataclass, field

from fast_flights import FlightQuery, Passengers, create_query, get_flights

from config import (
    DESTINATIONS,
    MAX_STOPS,
    ORIGINS,
    OUTBOUND_DATES,
    PREFERRED_AIRLINE,
    PREFERRED_HUB,
    REQUEST_DELAY_MAX,
    REQUEST_DELAY_MIN,
)


@dataclass
class Leg:
    from_code: str
    to_code: str
    airline: str


@dataclass
class Finding:
    origin: str
    dest_code: str
    dest_name: str
    depart: str
    price: int
    airline: str
    stops: int
    flights_url: str
    legs: list[Leg] = field(default_factory=list)
    is_aa_via_mia: bool = False


def google_flights_url(origin: str, dest: str, depart: str) -> str:
    return (
        "https://www.google.com/travel/flights?"
        f"q=Flights+from+{origin}+to+{dest}+on+{depart}+oneway"
    )


def _legs_from(flight) -> list[Leg]:
    out = []
    for l in (flight.flights or []):
        out.append(Leg(
            from_code=l.from_airport.code if l.from_airport else "?",
            to_code=l.to_airport.code if l.to_airport else "?",
            airline=(l.name or "") if hasattr(l, "name") else "",
        ))
    return out


def _is_aa_via_mia(legs: list[Leg], airline_str: str) -> bool:
    if PREFERRED_AIRLINE.lower() not in airline_str.lower():
        return False
    if len(legs) < 2:
        return False
    return legs[0].to_code == PREFERRED_HUB and legs[1].from_code == PREFERRED_HUB


def search_pair(origin: str, dest: str, depart: str) -> Finding | None:
    try:
        query = create_query(
            flights=[FlightQuery(date=depart, from_airport=origin, to_airport=dest)],
            trip="one-way",
            seat="economy",
            passengers=Passengers(adults=1),
            currency="USD",
        )
        results = get_flights(query)
    except Exception as e:
        print(f"    error {origin}->{dest} {depart}: {e}")
        return None

    if not results:
        return None

    best: Finding | None = None
    for f in results:
        if not (f.price and f.price > 0):
            continue
        legs = _legs_from(f)
        stops = max(len(legs) - 1, 0)
        if stops > MAX_STOPS:
            continue
        airline_str = ", ".join(f.airlines) if f.airlines else "?"
        candidate = Finding(
            origin=origin,
            dest_code=dest,
            dest_name="",
            depart=depart,
            price=int(f.price),
            airline=airline_str,
            stops=stops,
            flights_url=google_flights_url(origin, dest, depart),
            legs=legs,
            is_aa_via_mia=_is_aa_via_mia(legs, airline_str),
        )
        if best is None:
            best = candidate
        elif candidate.is_aa_via_mia and not best.is_aa_via_mia:
            best = candidate
        elif candidate.is_aa_via_mia == best.is_aa_via_mia and candidate.price < best.price:
            best = candidate
    return best


def scan_all() -> list[Finding]:
    findings: list[Finding] = []
    total = 0
    hits = 0

    for dest_code, dest_name in DESTINATIONS:
        for origin in ORIGINS:
            for d in OUTBOUND_DATES:
                total += 1
                depart = d.strftime("%Y-%m-%d")
                print(f"  {origin}->{dest_code} {depart} (oneway)...", end=" ", flush=True)

                result = search_pair(origin, dest_code, depart)
                if result is None:
                    print("no flights")
                else:
                    result.dest_name = dest_name
                    stops_str = "nonstop" if result.stops == 0 else f"{result.stops} stop"
                    aa_tag = " 🦅 AA-via-MIA" if result.is_aa_via_mia else ""
                    print(f"${result.price} ({result.airline}, {stops_str}){aa_tag} ✈")
                    findings.append(result)
                    hits += 1

                time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

    print(f"\n=== Scan done: {total} queries, {hits} with availability ===")
    return findings
