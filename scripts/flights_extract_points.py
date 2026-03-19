#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def get(obj, path, default=None):
    cur = obj
    for p in path:
        if isinstance(cur, list):
            try:
                cur = cur[p]
            except Exception:
                return default
        elif isinstance(cur, dict):
            if p not in cur:
                return default
            cur = cur[p]
        else:
            return default
    return cur


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: flights_extract_points.py <response.json>")
        print("Extracts booking/search keys from flights-sky response JSON.")
        sys.exit(0)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(path.read_text())
    except Exception as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    root = get(data, ["data"], {})
    itinerary = get(root, ["itinerary"], {})
    legs = get(itinerary, ["legs"], []) or []
    pricing = get(itinerary, ["pricingOptions"], []) or []

    booking_session_id = get(root, ["bookingSessionId"])
    polling_completed = get(root, ["pollingCompleted"])
    itinerary_id = get(itinerary, ["id"])
    pricing_option_id = get(pricing, [0, "id"])
    total_price = get(pricing, [0, "totalPrice"])
    agent_name = get(pricing, [0, "agents", 0, "name"])
    agent_url = get(pricing, [0, "agents", 0, "url"])

    print("Flight Search Points")
    print("====================")
    print(f"bookingSessionId: {booking_session_id}")
    print(f"pollingCompleted: {polling_completed}")
    print(f"itinerary.id: {itinerary_id}")
    print(f"pricingOptions[0].id: {pricing_option_id}")
    print(f"pricingOptions[0].totalPrice: {total_price}")
    print(f"pricingOptions[0].agents[0].name: {agent_name}")
    print(f"pricingOptions[0].agents[0].url: {agent_url}")
    print()

    print("Legs / Segments")
    print("===============")
    if not legs:
        print("No legs found")
    for i, leg in enumerate(legs, 1):
        o = get(leg, ["origin", "displayCode"])
        d = get(leg, ["destination", "displayCode"])
        dep = get(leg, ["departure"])
        arr = get(leg, ["arrival"])
        stops = get(leg, ["stopCount"])
        print(f"Leg {i}: {o} -> {d} | dep {dep} | arr {arr} | stops {stops}")

        for j, seg in enumerate(get(leg, ["segments"], []) or [], 1):
            so = get(seg, ["origin", "displayCode"])
            sd = get(seg, ["destination", "displayCode"])
            fn = get(seg, ["flightNumber"])
            carrier = get(seg, ["marketingCarrier", "displayCode"])
            sid = get(seg, ["id"])
            sdep = get(seg, ["departure"])
            sarr = get(seg, ["arrival"])

            # Avoid duplicate carrier prefix when flightNumber already includes it (e.g., "BF720").
            flight_label = str(fn or "")
            if carrier and flight_label and not flight_label.upper().startswith(str(carrier).upper()):
                flight_label = f"{carrier}{flight_label}"

            print(f"  Segment {j}: {so}->{sd} {flight_label} | {sdep} -> {sarr}")
            print(f"    segment.id: {sid}")


if __name__ == "__main__":
    main()
