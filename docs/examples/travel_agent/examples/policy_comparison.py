"""
Policy Comparison Example

Compare travel options across different role policies.
"""

import sys

sys.path.append('.')

import json
from docs.examples.travel_agent.agents.compliance_agent_tools import load_user_policy


def compare_policies():
    """Compare policies for different roles"""

    roles = ["employee", "manager", "executive", "approving_manager"]

    print("\n" + "=" * 70)
    print("Corporate Travel Policy Comparison")
    print("=" * 70 + "\n")

    policies = {}
    for role in roles:
        policy_json = load_user_policy.invoke({"user_role": role})
        policies[role] = json.loads(policy_json)

    # Compare flight policies
    print("✈️  FLIGHT POLICIES")
    print("-" * 70)
    print(f"{'Role':<12} {'Max Cost':<12} {'Classes':<30}")
    print("-" * 70)

    for role in roles:
        max_cost = policies[role]["flight_policy"]["max_cost_per_person"]
        classes = ", ".join(policies[role]["flight_policy"]["allowed_classes"])
        print(f"{role.capitalize():<12} ${max_cost:<11} {classes:<30}")

    # Compare hotel policies
    print("\n🏨 HOTEL POLICIES")
    print("-" * 70)
    print(f"{'Role':<12} {'Max/Night':<12} {'Min Rating':<12}")
    print("-" * 70)

    for role in roles:
        max_rate = policies[role]["hotel_policy"]["max_rate_per_night"]
        min_rating = policies[role]["hotel_policy"]["min_rating"]
        print(f"{role.capitalize():<12} ${max_rate:<11} {min_rating:<12}")

    # Compare total budgets
    print("\n💰 BUDGET LIMITS")
    print("-" * 70)
    print(f"{'Role':<12} {'Total Budget':<15} {'Per Diem':<12}")
    print("-" * 70)

    for role in roles:
        total = policies[role]["expense_policy"]["max_total_budget"]
        per_diem = policies[role]["expense_policy"]["meal_per_diem"]
        print(f"{role.capitalize():<12} ${total:<14} ${per_diem}/day")

    # Compare approval requirements
    print("\n✅ APPROVAL REQUIREMENTS")
    print("-" * 70)
    print(f"{'Role':<12} {'Requires Approval':<20} {'Approver':<20}")
    print("-" * 70)

    for role in roles:
        requires = policies[role]["approval_policy"]["requires_approval"]
        approver = policies[role]["approval_policy"].get("approver_role", "N/A")
        print(f"{role.capitalize():<12} {'Yes' if requires else 'No':<20} {approver:<20}")

    print("\n" + "=" * 70)

    # Show example scenarios
    print("\n📋 EXAMPLE SCENARIOS")
    print("=" * 70 + "\n")

    print("Scenario 1: NYC → LA (5 days)")
    print("-" * 70)
    example_flight = 450
    example_hotel = 140
    example_days = 5

    for role in roles:
        policy = policies[role]
        flight_ok = example_flight <= policy["flight_policy"]["max_cost_per_person"]
        hotel_ok = example_hotel <= policy["hotel_policy"]["max_rate_per_night"]

        total = (
            example_flight
            + (example_hotel * example_days)
            + (policy["expense_policy"]["meal_per_diem"] * example_days)
        )
        budget_ok = total <= policy["expense_policy"]["max_total_budget"]

        status = "✅ Compliant" if (flight_ok and hotel_ok and budget_ok) else "❌ Violation"
        print(
            f"{role.capitalize():<12} Flight: ${example_flight} {'✅' if flight_ok else '❌'} | "
            f"Hotel: ${example_hotel}/night {'✅' if hotel_ok else '❌'} | "
            f"Total: ${total:.0f} {'✅' if budget_ok else '❌'} | {status}"
        )

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    compare_policies()

# Made with Bob
