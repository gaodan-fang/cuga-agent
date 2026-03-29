"""
Basic Travel Request Example

This example shows how to use the Travel Agent to plan a simple trip.
"""

import sys

sys.path.append('.')

import json
from docs.examples.travel_agent.agents.flight_agent_tools import search_flights
from docs.examples.travel_agent.agents.hotel_agent_tools import search_hotels
from docs.examples.travel_agent.agents.weather_agent_tools import get_weather_forecast
from docs.examples.travel_agent.agents.finance_agent_tools import calculate_total_trip_cost
from docs.examples.travel_agent.agents.compliance_agent_tools import (
    load_user_policy,
    check_overall_compliance,
)


def plan_basic_trip():
    """Plan a basic trip from New York to Los Angeles"""

    print("\n" + "=" * 70)
    print("🛫 Planning trip: New York → Los Angeles")
    print("📅 Dates: April 15-20, 2026")
    print("👤 Role: Employee")
    print("=" * 70 + "\n")

    # Step 1: Search flights
    print("1️⃣ Searching flights...")
    flights = search_flights.invoke(
        {
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "passengers": 1,
            "travel_class": "economy",
        }
    )
    flights_data = json.loads(flights)

    if flights_data["success"]:
        print(f"   ✅ Found {flights_data['flights_found']} flights")
        if flights_data["flights"]:
            cheapest = min(flights_data["flights"], key=lambda x: x["price"])
            print(f"   💰 Cheapest: ${cheapest['price']} - {cheapest['airline']}")

    # Step 2: Search hotels
    print("\n2️⃣ Searching hotels...")
    hotels = search_hotels.invoke(
        {
            "location": "Los Angeles, CA",
            "check_in_date": "2026-04-15",
            "check_out_date": "2026-04-20",
            "guests": 1,
            "rooms": 1,
        }
    )
    hotels_data = json.loads(hotels)

    if hotels_data["success"]:
        print(f"   ✅ Found {hotels_data['hotels_found']} hotels")
        if hotels_data["hotels"]:
            cheapest_hotel = min(hotels_data["hotels"], key=lambda x: x["rate_per_night"])
            print(f"   💰 Cheapest: ${cheapest_hotel['rate_per_night']}/night - {cheapest_hotel['name']}")

    # Step 3: Get weather
    print("\n3️⃣ Getting weather forecast...")
    weather = get_weather_forecast.invoke(
        {"location": "Los Angeles", "start_date": "2026-04-15", "end_date": "2026-04-20"}
    )
    weather_data = json.loads(weather)

    if weather_data["success"]:
        print("   ✅ Weather forecast retrieved")
        if weather_data["forecast"]:
            avg_temp = sum(d["temperature"] for d in weather_data["forecast"]) / len(weather_data["forecast"])
            print(f"   🌡️  Average temperature: {avg_temp:.1f}°F")

    # Step 4: Calculate total cost
    print("\n4️⃣ Calculating total trip cost...")
    if flights_data["flights"] and hotels_data["hotels"]:
        total_cost_result = calculate_total_trip_cost.invoke(
            {
                "flight_json": json.dumps(cheapest),
                "hotel_json": json.dumps(cheapest_hotel),
                "nights": 5,
                "passengers": 1,
                "user_role": "employee",
            }
        )
        cost_data = json.loads(total_cost_result)

        if cost_data["success"]:
            print(f"   ✅ Total estimated cost: ${cost_data['total_cost']:.2f}")
            print("   📊 Breakdown:")
            print(f"      - Flights: ${cost_data['breakdown']['flights']:.2f}")
            print(f"      - Hotels: ${cost_data['breakdown']['hotels']:.2f}")
            print(f"      - Per Diem: ${cost_data['breakdown']['per_diem']:.2f}")

    # Step 5: Check policy compliance
    print("\n5️⃣ Checking policy compliance...")
    policy = load_user_policy.invoke({"user_role": "employee"})

    if flights_data["flights"] and hotels_data["hotels"]:
        compliance = check_overall_compliance.invoke(
            {
                "flight_json": json.dumps(cheapest),
                "hotel_json": json.dumps(cheapest_hotel),
                "total_cost": cost_data['total_cost'],
                "policy_json": policy,
            }
        )
        compliance_data = json.loads(compliance)

        if compliance_data.get("compliant"):
            print("   ✅ Trip is compliant with employee policy")
        else:
            print("   ⚠️  Policy violations detected:")
            for violation in compliance_data.get("violations", []):
                print(f"      - {violation}")

    print("\n" + "=" * 70)
    print("✅ Trip planning complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    plan_basic_trip()

# Made with Bob
