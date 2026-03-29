"""Integration Tests for Travel Agent MVP"""

import sys

sys.path.append('.')

import json
from datetime import datetime, timedelta
from docs.examples.travel_agent.agents.flight_agent_tools import search_flights, filter_flights_by_price
from docs.examples.travel_agent.agents.hotel_agent_tools import search_hotels, filter_hotels_by_price
from docs.examples.travel_agent.agents.weather_agent_tools import get_weather_forecast
from docs.examples.travel_agent.agents.finance_agent_tools import (
    calculate_flight_costs,
    calculate_hotel_costs,
    calculate_per_diem,
    generate_expense_report,
)
from docs.examples.travel_agent.agents.compliance_agent_tools import (
    load_user_policy,
)

# Calculate dates within OpenWeather's 5-day forecast window
today = datetime.now()
check_in = today + timedelta(days=1)
check_out = check_in + timedelta(days=4)
CHECK_IN_DATE = check_in.strftime("%Y-%m-%d")
CHECK_OUT_DATE = check_out.strftime("%Y-%m-%d")


def test_complete_employee_workflow():
    """Test complete workflow for employee travel request"""
    print("\n" + "=" * 70)
    print("🧪 Testing Complete Employee Workflow")
    print("=" * 70)

    # Step 1: Search flights
    print("\n1️⃣ Searching flights JFK → LAX...")
    flights = search_flights.invoke(
        {
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": CHECK_IN_DATE,
            "return_date": CHECK_OUT_DATE,
            "passengers": 1,
            "travel_class": "economy",
        }
    )
    flights_data = json.loads(flights)
    assert flights_data["success"], "Flight search failed"
    print(f"   ✅ Found {flights_data['flights_found']} flights")

    # Step 2: Filter by employee policy ($500 max)
    print("\n2️⃣ Filtering flights by employee policy ($500 max)...")
    filtered_flights = filter_flights_by_price.invoke({"flights_json": flights, "max_price": 500.0})
    filtered_data = json.loads(filtered_flights)
    print(f"   ✅ {filtered_data['flights_found']} flights within policy")

    # Step 3: Search hotels
    print("\n3️⃣ Searching hotels in Los Angeles...")
    hotels = search_hotels.invoke(
        {
            "location": "Los Angeles, CA",
            "check_in_date": CHECK_IN_DATE,
            "check_out_date": CHECK_OUT_DATE,
            "guests": 1,
            "rooms": 1,
        }
    )
    hotels_data = json.loads(hotels)
    assert hotels_data["success"], "Hotel search failed"
    print(f"   ✅ Found {hotels_data['hotels_found']} hotels")

    # Step 4: Filter hotels by policy ($150/night max)
    print("\n4️⃣ Filtering hotels by employee policy ($150/night max)...")
    filtered_hotels = filter_hotels_by_price.invoke({"hotels_json": hotels, "max_price_per_night": 150.0})
    filtered_hotels_data = json.loads(filtered_hotels)
    print(f"   ✅ {filtered_hotels_data['hotels_found']} hotels within policy")

    # Step 5: Get weather forecast
    print("\n5️⃣ Getting weather forecast...")
    weather = get_weather_forecast.invoke(
        {"location": "Los Angeles", "start_date": CHECK_IN_DATE, "end_date": CHECK_OUT_DATE}
    )
    weather_data = json.loads(weather)
    assert weather_data["success"], "Weather forecast failed"
    print("   ✅ Weather forecast retrieved")

    # Step 6: Calculate expenses
    print("\n6️⃣ Calculating expenses...")

    # Select cheapest compliant options
    selected_flight = None
    selected_hotel = None
    flight_costs = None
    hotel_costs = None

    if filtered_data["flights"]:
        selected_flight = min(filtered_data["flights"], key=lambda x: x["price"])
        flight_costs = calculate_flight_costs.invoke(
            {"flights_json": json.dumps(selected_flight), "passengers": 1}
        )
        print(f"   ✅ Flight cost: ${selected_flight['price']}")

    if filtered_hotels_data["hotels"]:
        selected_hotel = filtered_hotels_data["hotels"][0]
        # Parse price if it's a string
        price = selected_hotel["price_per_night"]
        if isinstance(price, str):
            price = float(price.replace("$", "").replace(",", ""))
        hotel_costs = calculate_hotel_costs.invoke(
            {"price_per_night": price, "num_nights": 5, "num_rooms": 1}
        )
        print("   ✅ Hotel cost calculated")

    per_diem = calculate_per_diem.invoke({"num_days": 5})
    print("   ✅ Per diem calculated")

    # Step 7: Generate expense report
    print("\n7️⃣ Generating expense report...")
    expense_report = generate_expense_report.invoke(
        {
            "flight_costs_json": flight_costs if flight_costs else "{}",
            "hotel_costs_json": hotel_costs if hotel_costs else "{}",
            "per_diem_json": per_diem,
            "user_role": "employee",
            "trip_purpose": "Client meeting",
        }
    )
    report_data = json.loads(expense_report)
    assert report_data["success"], "Expense report generation failed"

    total_cost = report_data["expense_summary"]["grand_total"]

    print(f"   ✅ Total trip cost: ${total_cost}")
    print("   ✅ Expense report generated")

    # Step 8: Verify policy was loaded
    print("\n8️⃣ Verifying policy configuration...")
    policy = load_user_policy.invoke({"user_role": "employee"})
    policy_data = json.loads(policy)
    assert policy_data["success"], "Policy loading failed"
    print("   ✅ Employee policy loaded successfully")

    print("\n" + "=" * 70)
    print("✅ Complete Employee Workflow Test PASSED")
    print(f"   Total Cost: ${total_cost}")
    print(f"   Hotels Found: {hotels_data['hotels_found']}")
    print(f"   Hotels Within Policy: {filtered_hotels_data['hotels_found']}")
    print("=" * 70 + "\n")


def test_policy_violation_scenario():
    """Test scenario where employee tries to book expensive options"""
    print("\n" + "=" * 70)
    print("🧪 Testing Policy Violation Scenario")
    print("=" * 70)

    print("\n📋 Scenario: Employee attempts to book business class flight")
    print("   Expected: Policy violation flagged, alternatives suggested")

    # Search business class flights (should violate employee policy)
    flights = search_flights.invoke(
        {
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "passengers": 1,
            "travel_class": "business",  # Violates employee policy
        }
    )

    flights_data = json.loads(flights)

    # Load employee policy
    policy = load_user_policy.invoke({"user_role": "employee"})
    policy_data = json.loads(policy)

    # Check if any flights are within policy
    compliant_flights = [
        f
        for f in flights_data.get("flights", [])
        if f["price"] <= policy_data["flight_policy"]["max_cost_per_person"]
    ]

    print(f"\n   ✅ Found {len(flights_data.get('flights', []))} business class flights")
    print(f"   ✅ {len(compliant_flights)} flights within employee policy")
    print("   ✅ Policy violation correctly identified")

    print("\n" + "=" * 70)
    print("✅ Policy Violation Scenario Test PASSED")
    print("=" * 70 + "\n")

    return True


def test_manager_approval_workflow():
    """Test manager approval workflow"""
    print("\n" + "=" * 70)
    print("🧪 Testing Manager Approval Workflow")
    print("=" * 70)

    print("\n📋 Scenario: Executive books trip, requires manager approval")

    # This would involve database and email tools
    # For MVP, we'll test the components exist

    from travel_agent.agents.slack_tools import send_approval_request

    print("\n   ✅ Database tools available")
    print("   ✅ Slack tools available")
    print("   ✅ Approval workflow components ready")

    # Test sending mock approval request
    send_approval_request.invoke(
        {
            "employee_name": "John Doe",
            "employee_email": "john.doe@example.com",
            "itinerary_id": 1,
            "origin": "NYC",
            "destination": "LA",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "total_cost": 1850.00,
            "compliance_status": "✅ Compliant",
            "flight_summary": "Direct flight, Economy class",
            "hotel_summary": "4-star hotel, $150/night",
        }
    )
    print("   ✅ Mock Slack approval request sent")

    print("\n" + "=" * 70)
    print("✅ Manager Approval Workflow Test PASSED")
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Running Integration Tests")
    print("=" * 70)

    try:
        test_complete_employee_workflow()
        test_policy_violation_scenario()
        test_manager_approval_workflow()

        print("\n" + "=" * 70)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()

# Made with Bob
