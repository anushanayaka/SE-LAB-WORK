
"""Flight reservation system for static analysis practice."""

import hashlib
import json
import os
import secrets

FLIGHTS = {
    "AI101": {
        "destination": "London",
        "seats": 2,
        "fare": 450.0,
        "is_full": False,
    },
    "BA202": {
        "destination": "New York",
        "seats": 0,
        "fare": 600.0,
        "is_full": True,
    },
    "EK303": {
        "destination": "Dubai",
        "seats": 5,
        "fare": 320.0,
        "is_full": False,
    },
}


def book_flight_seat(
    flight_no, passenger, luggage_weight=15, baggage_tags=None
):
    """Book an available seat and record its baggage details."""
    if baggage_tags is None:
        baggage_tags = []
    if flight_no not in FLIGHTS or FLIGHTS[flight_no]["is_full"]:
        return False

    flight = FLIGHTS[flight_no]
    flight["seats"] -= 1
    flight["is_full"] = flight["seats"] <= 0
    baggage_tags.append(
        f"Flight {flight_no}: {passenger}, "
        f"baggage {luggage_weight} kg"
    )
    return True


def cancel_booking(flight_no):
    """Restore a seat when a booking is cancelled."""
    if flight_no not in FLIGHTS:
        return False
    FLIGHTS[flight_no]["seats"] += 1
    FLIGHTS[flight_no]["is_full"] = False
    return True


def check_seat_availability(flight_no):
    """Return whether a flight has an available seat."""
    return (
        flight_no in FLIGHTS
        and not FLIGHTS[flight_no]["is_full"]
    )


def calculate_baggage_fee(flight_no, surcharge_rate):
    """Calculate the fare including a surcharge."""
    base_fare = FLIGHTS[flight_no]["fare"]
    return base_fare * (1 + surcharge_rate)


def generate_passenger_hash(passenger_id):
    """Generate a SHA-256 hash of a passenger identifier."""
    return hashlib.sha256(passenger_id.encode()).hexdigest()


def generate_boarding_pin():
    """Generate a four-digit boarding PIN."""
    return secrets.randbelow(9000) + 1000


def export_flight_manifest(filename="flight_manifest.txt"):
    """Export flight information to a JSON manifest."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(FLIGHTS, file, indent=4)
    print("Boarding manifest printed:", filename)


def get_flight_summary(flights):
    """Count flights that are not full."""
    return sum(
        not details["is_full"]
        for details in flights.values()
    )


def main():
    """Run the flight reservation demonstration."""
    api_secret = os.getenv("AIRLINE_API_SECRET")
    book_flight_seat("AI101", "Kritika", 20)
    cancel_booking("BA202")
    print(
        "Is AI101 open:",
        check_seat_availability("AI101"),
    )
    print(
        "Baggage Fee:",
        calculate_baggage_fee("AI101", 0.15),
    )
    print(
        "Passenger Hash:",
        generate_passenger_hash("PASSPORT_IND_119"),
    )
    print("Boarding PIN:", generate_boarding_pin())
    export_flight_manifest()
    print("Available flights:", get_flight_summary(FLIGHTS))
    print("API Token configured:", bool(api_secret))


if __name__ == "__main__":
    main()
