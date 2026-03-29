"""Test Finance Agent Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.finance_agent_tools import (
    calculate_flight_costs,
    calculate_hotel_costs,
    calculate_per_diem,
    generate_expense_report,
    validate_budget,
    calculate_total_trip_cost,
)


def test_flight_costs():
    """Test flight cost calculation"""
    print("\n🧪 Testing calculate_flight_costs...")
    result = calculate_flight_costs.invoke(
        {"flight_price": 350.00, "passengers": 1, "baggage_fees": 30.00, "seat_selection_fees": 15.00}
    )
    print(result)
    assert "success" in result
    assert "total_cost" in result
    print("✅ calculate_flight_costs test passed")
    return result


def test_hotel_costs():
    """Test hotel cost calculation"""
    print("\n🧪 Testing calculate_hotel_costs...")
    result = calculate_hotel_costs.invoke(
        {"price_per_night": 150.00, "num_nights": 5, "num_rooms": 1, "taxes_and_fees_percent": 15.0}
    )
    print(result)
    assert "success" in result
    assert "total_cost" in result
    print("✅ calculate_hotel_costs test passed")
    return result


def test_per_diem():
    """Test per diem calculation"""
    print("\n🧪 Testing calculate_per_diem...")
    result = calculate_per_diem.invoke(
        {
            "num_days": 6,
            "daily_meal_allowance": 50.0,
            "daily_transport_allowance": 25.0,
            "daily_incidentals": 10.0,
        }
    )
    print(result)
    assert "success" in result
    assert "total_per_diem" in result
    print("✅ calculate_per_diem test passed")
    return result


def test_expense_report():
    """Test expense report generation"""
    print("\n🧪 Testing generate_expense_report...")

    # Get component costs
    flight_costs = calculate_flight_costs.invoke({"flight_price": 350.00, "passengers": 1})

    hotel_costs = calculate_hotel_costs.invoke({"price_per_night": 150.00, "num_nights": 5})

    per_diem = calculate_per_diem.invoke({"num_days": 6})

    # Generate report
    result = generate_expense_report.invoke(
        {"flight_costs_json": flight_costs, "hotel_costs_json": hotel_costs, "per_diem_json": per_diem}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    assert "grand_total" in result
    print("✅ generate_expense_report test passed")
    return result


def test_budget_validation():
    """Test budget validation"""
    print("\n🧪 Testing validate_budget...")

    # Generate expense report first
    flight_costs = calculate_flight_costs.invoke({"flight_price": 350.00, "passengers": 1})
    hotel_costs = calculate_hotel_costs.invoke({"price_per_night": 150.00, "num_nights": 5})
    per_diem = calculate_per_diem.invoke({"num_days": 6})

    expense_report = generate_expense_report.invoke(
        {"flight_costs_json": flight_costs, "hotel_costs_json": hotel_costs, "per_diem_json": per_diem}
    )

    # Validate against budget
    result = validate_budget.invoke(
        {"expense_report_json": expense_report, "budget_limit": 2000.00, "role": "employee"}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    assert "is_within_budget" in result
    print("✅ validate_budget test passed")


def test_quick_calculation():
    """Test quick trip cost calculation"""
    print("\n🧪 Testing calculate_total_trip_cost...")
    result = calculate_total_trip_cost.invoke(
        {
            "flight_price": 350.00,
            "hotel_price_per_night": 150.00,
            "num_nights": 5,
            "num_days": 6,
            "passengers": 1,
            "daily_per_diem": 85.0,
        }
    )
    print(result)
    assert "success" in result
    assert "total" in result
    print("✅ calculate_total_trip_cost test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Finance Agent Tools")
    print("=" * 60)

    try:
        test_flight_costs()
        test_hotel_costs()
        test_per_diem()
        test_expense_report()
        test_budget_validation()
        test_quick_calculation()

        print("\n" + "=" * 60)
        print("✅ All Finance Agent tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
