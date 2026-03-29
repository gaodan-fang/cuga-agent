"""Test Hotel Agent Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.hotel_agent_tools import (
    search_hotels,
    filter_hotels_by_price,
    filter_hotels_by_rating,
    get_best_value_hotel,
)


def test_search_hotels():
    """Test hotel search"""
    print("\n🧪 Testing search_hotels...")
    result = search_hotels.invoke(
        {
            "location": "Los Angeles",
            "check_in_date": "2026-04-15",
            "check_out_date": "2026-04-20",
            "guests": 2,
            "rooms": 1,
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ search_hotels test passed")
    return result


def test_filter_by_price():
    """Test price filtering"""
    print("\n🧪 Testing filter_hotels_by_price...")
    # First search
    hotels = search_hotels.invoke(
        {"location": "Los Angeles", "check_in_date": "2026-04-15", "check_out_date": "2026-04-20"}
    )
    # Then filter
    result = filter_hotels_by_price.invoke({"hotels_json": hotels, "max_price_per_night": 150.0})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "filter_applied" in result or "success" in result
    print("✅ filter_hotels_by_price test passed")


def test_filter_by_rating():
    """Test rating filtering"""
    print("\n🧪 Testing filter_hotels_by_rating...")
    # First search
    hotels = search_hotels.invoke(
        {"location": "Los Angeles", "check_in_date": "2026-04-15", "check_out_date": "2026-04-20"}
    )
    # Then filter
    result = filter_hotels_by_rating.invoke({"hotels_json": hotels, "min_rating": 4.0})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "filter_applied" in result or "success" in result
    print("✅ filter_hotels_by_rating test passed")


def test_get_best_value():
    """Test getting best value hotel"""
    print("\n🧪 Testing get_best_value_hotel...")
    # First search
    hotels = search_hotels.invoke(
        {"location": "Los Angeles", "check_in_date": "2026-04-15", "check_out_date": "2026-04-20"}
    )
    # Get best value
    result = get_best_value_hotel.invoke({"hotels_json": hotels})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result or "best_value_hotel" in result
    print("✅ get_best_value_hotel test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Hotel Agent Tools")
    print("=" * 60)

    try:
        test_search_hotels()
        test_filter_by_price()
        test_filter_by_rating()
        test_get_best_value()

        print("\n" + "=" * 60)
        print("✅ All Hotel Agent tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
