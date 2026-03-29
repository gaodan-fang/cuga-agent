"""Test Weather Agent Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.weather_agent_tools import (
    get_weather_forecast,
    get_current_weather,
    get_packing_suggestions,
)


def test_current_weather():
    """Test current weather"""
    print("\n🧪 Testing get_current_weather...")
    result = get_current_weather.invoke({"location": "Los Angeles"})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ get_current_weather test passed")


def test_weather_forecast():
    """Test weather forecast"""
    print("\n🧪 Testing get_weather_forecast...")
    result = get_weather_forecast.invoke(
        {"location": "Los Angeles", "start_date": "2026-04-15", "end_date": "2026-04-20"}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ get_weather_forecast test passed")
    return result


def test_packing_suggestions():
    """Test packing suggestions"""
    print("\n🧪 Testing get_packing_suggestions...")
    # First get forecast
    forecast = get_weather_forecast.invoke(
        {"location": "Los Angeles", "start_date": "2026-04-15", "end_date": "2026-04-20"}
    )
    # Then get packing suggestions
    result = get_packing_suggestions.invoke({"weather_forecast_json": forecast})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result or "packing_list" in result
    print("✅ get_packing_suggestions test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Weather Agent Tools")
    print("=" * 60)

    try:
        test_current_weather()
        test_weather_forecast()
        test_packing_suggestions()

        print("\n" + "=" * 60)
        print("✅ All Weather Agent tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
