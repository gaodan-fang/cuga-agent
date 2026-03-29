"""Test Flight Agent Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.flight_agent_tools import (
    search_flights,
    filter_flights_by_price,
    get_cheapest_flight,
)


def test_search_flights():
    """Test flight search"""
    print("\n🧪 Testing search_flights...")
    result = search_flights.invoke(
        {
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "passengers": 1,
            "travel_class": "economy",
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ search_flights test passed")
    return result


def test_filter_by_price():
    """Test price filtering"""
    print("\n🧪 Testing filter_flights_by_price...")
    # First search
    flights = search_flights.invoke(
        {"origin": "JFK", "destination": "LAX", "departure_date": "2026-04-15", "return_date": "2026-04-20"}
    )
    # Then filter
    result = filter_flights_by_price.invoke({"flights_json": flights, "max_price": 300.0})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "filter_applied" in result or "success" in result
    print("✅ filter_flights_by_price test passed")


def test_get_cheapest():
    """Test getting cheapest flight"""
    print("\n🧪 Testing get_cheapest_flight...")
    # First search
    flights = search_flights.invoke(
        {"origin": "JFK", "destination": "LAX", "departure_date": "2026-04-15", "return_date": "2026-04-20"}
    )
    # Get cheapest
    result = get_cheapest_flight.invoke({"flights_json": flights})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result or "cheapest_flight" in result
    print("✅ get_cheapest_flight test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Flight Agent Tools")
    print("=" * 60)

    try:
        test_search_flights()
        test_filter_by_price()
        test_get_cheapest()

        print("\n" + "=" * 60)
        print("✅ All Flight Agent tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
