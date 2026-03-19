#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def get(obj, path, default=None):
    cur = obj
    for p in path:
        if isinstance(cur, dict):
            if p not in cur:
                return default
            cur = cur[p]
        elif isinstance(cur, list):
            try:
                cur = cur[p]
            except Exception:
                return default
        else:
            return default
    return cur


def summary_details(payload):
    root = get(payload, ["data"], {})
    itinerary = get(root, ["itinerary"], {})
    pricing = get(itinerary, ["pricingOptions"], []) or []

    print("Flight Details Summary")
    print("======================")
    print(f"status: {get(payload, ['status'])}")
    print(f"message: {get(payload, ['message'])}")
    print(f"bookingSessionId: {get(root, ['bookingSessionId'])}")
    print(f"pollingCompleted: {get(root, ['pollingCompleted'])}")
    print(f"itinerary.id: {get(itinerary, ['id'])}")
    print(f"pricingOptions[0].id: {get(pricing, [0, 'id'])}")
    print(f"pricingOptions[0].totalPrice: {get(pricing, [0, 'totalPrice'])}")
    print(f"agent: {get(pricing, [0, 'agents', 0, 'name'])}")

    legs = get(itinerary, ["legs"], []) or []
    print()
    print("Legs")
    print("----")
    if not legs:
        print("No legs found")
        return

    for i, leg in enumerate(legs, 1):
        print(
            f"Leg {i}: {get(leg,['origin','displayCode'])} -> {get(leg,['destination','displayCode'])} "
            f"| dep {get(leg,['departure'])} | arr {get(leg,['arrival'])} | stops {get(leg,['stopCount'])}"
        )
        for j, seg in enumerate(get(leg, ["segments"], []) or [], 1):
            carrier = str(get(seg, ["marketingCarrier", "displayCode"]) or "")
            flight_no = str(get(seg, ["flightNumber"]) or "")
            label = flight_no if flight_no.upper().startswith(carrier.upper()) else f"{carrier}{flight_no}"
            print(
                f"  Segment {j}: {get(seg,['origin','displayCode'])}->{get(seg,['destination','displayCode'])} {label} "
                f"| {get(seg,['departure'])} -> {get(seg,['arrival'])}"
            )


def summary_min_price(payload):
    data = get(payload, ["data"], payload)
    print("One-way Min Price Summary")
    print("=========================")
    print(f"status: {get(payload, ['status'], 'n/a')}")
    print(f"message: {get(payload, ['message'], 'n/a')}")

    # Heuristic extraction (schema may vary by provider version)
    min_price_candidates = [
        get(data, ["minPrice"]),
        get(data, ["price"]),
        get(data, ["totalPrice"]),
        get(data, ["lowestPrice"]),
    ]
    min_price = next((x for x in min_price_candidates if x is not None), None)
    print(f"minPrice (best guess): {min_price}")

    # Common list containers
    for key in ["itineraries", "flights", "results", "options"]:
        val = get(data, [key])
        if isinstance(val, list):
            print(f"{key} count: {len(val)}")
            if val:
                sample = val[0]
                origin = get(sample, ["origin", "displayCode"]) or get(sample, ["origin"]) or get(sample, ["departId"])
                destination = get(sample, ["destination", "displayCode"]) or get(sample, ["destination"]) or get(sample, ["arrivalId"])
                dep = get(sample, ["departure"]) or get(sample, ["departTime"]) or get(sample, ["departDate"])
                print(f"first result (best guess): {origin} -> {destination} | dep {dep}")
            break


def main():
    if len(sys.argv) < 3 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: travel_summarize.py <details|min-price> <response.json>")
        sys.exit(0)

    mode = sys.argv[1]
    path = Path(sys.argv[2])

    try:
        payload = json.loads(path.read_text())
    except Exception as e:
        print(f"Error reading JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if mode == "details":
        summary_details(payload)
    elif mode == "min-price":
        summary_min_price(payload)
    else:
        print("Mode must be one of: details, min-price", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
