"""Test Compliance Agent Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.compliance_agent_tools import (
    load_user_policy,
    validate_flight_policy,
    validate_hotel_policy,
    validate_total_budget,
    check_overall_compliance,
    suggest_compliant_alternatives,
)


def test_load_policy():
    """Test policy loading"""
    print("\n🧪 Testing load_user_policy...")

    # Test employee policy
    result = load_user_policy.invoke({"role": "employee"})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    assert "policy" in result
    print("✅ load_user_policy test passed")
    return result


def test_validate_flight():
    """Test flight validation"""
    print("\n🧪 Testing validate_flight_policy...")

    # Load policy first
    policy = load_user_policy.invoke({"role": "employee"})

    # Test compliant flight
    result = validate_flight_policy.invoke(
        {"flight_price": 450.00, "flight_class": "economy", "policy_json": policy}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "is_compliant" in result
    print("✅ validate_flight_policy test passed")
    return result


def test_validate_hotel():
    """Test hotel validation"""
    print("\n🧪 Testing validate_hotel_policy...")

    # Load policy first
    policy = load_user_policy.invoke({"role": "employee"})

    # Test compliant hotel
    result = validate_hotel_policy.invoke(
        {"hotel_price_per_night": 140.00, "num_nights": 5, "policy_json": policy}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "is_compliant" in result
    print("✅ validate_hotel_policy test passed")
    return result


def test_validate_budget():
    """Test budget validation"""
    print("\n🧪 Testing validate_total_budget...")

    # Load policy first
    policy = load_user_policy.invoke({"role": "employee"})

    # Test within budget
    result = validate_total_budget.invoke({"total_cost": 1850.00, "policy_json": policy})
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "is_within_budget" in result
    print("✅ validate_total_budget test passed")
    return result


def test_overall_compliance():
    """Test overall compliance check"""
    print("\n🧪 Testing check_overall_compliance...")

    # Load policy
    policy = load_user_policy.invoke({"role": "employee"})

    # Get individual validations
    flight_val = validate_flight_policy.invoke(
        {"flight_price": 450.00, "flight_class": "economy", "policy_json": policy}
    )

    hotel_val = validate_hotel_policy.invoke(
        {"hotel_price_per_night": 140.00, "num_nights": 5, "policy_json": policy}
    )

    budget_val = validate_total_budget.invoke({"total_cost": 1850.00, "policy_json": policy})

    # Check overall compliance
    result = check_overall_compliance.invoke(
        {
            "flight_validation_json": flight_val,
            "hotel_validation_json": hotel_val,
            "budget_validation_json": budget_val,
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "is_fully_compliant" in result
    print("✅ check_overall_compliance test passed")


def test_suggest_alternatives():
    """Test alternative suggestions"""
    print("\n🧪 Testing suggest_compliant_alternatives...")

    # Load policy
    policy = load_user_policy.invoke({"role": "employee"})

    # Test with non-compliant prices
    result = suggest_compliant_alternatives.invoke(
        {"current_flight_price": 600.00, "current_hotel_price": 200.00, "policy_json": policy}
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "suggestions" in result
    print("✅ suggest_compliant_alternatives test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Compliance Agent Tools")
    print("=" * 60)

    try:
        test_load_policy()
        test_validate_flight()
        test_validate_hotel()
        test_validate_budget()
        test_overall_compliance()
        test_suggest_alternatives()

        print("\n" + "=" * 60)
        print("✅ All Compliance Agent tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
