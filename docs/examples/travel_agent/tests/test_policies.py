"""Test Policy Configurations"""

import yaml
import os
import sys


def test_all_policies_exist():
    """Test that all policy files exist"""
    policy_dir = "docs/examples/travel_agent/config/policies"
    required_policies = [
        "employee_policy.yaml",
        "manager_policy.yaml",
        "executive_policy.yaml",
        "approving_manager_policy.yaml",
    ]

    for policy_file in required_policies:
        path = os.path.join(policy_dir, policy_file)
        assert os.path.exists(path), f"Policy file not found: {path}"

    print(f"✅ All {len(required_policies)} policy files exist")


def test_policy_structure():
    """Test that policies have required structure"""
    policy_files = [
        "docs/examples/travel_agent/config/policies/employee_policy.yaml",
        "docs/examples/travel_agent/config/policies/manager_policy.yaml",
        "docs/examples/travel_agent/config/policies/executive_policy.yaml",
        "docs/examples/travel_agent/config/policies/approving_manager_policy.yaml",
    ]

    required_sections = ["role", "flight_policy", "hotel_policy", "expense_policy", "approval_policy"]

    for policy_file in policy_files:
        with open(policy_file, 'r') as f:
            policy = yaml.safe_load(f)

        for section in required_sections:
            assert section in policy, f"Missing section '{section}' in {policy_file}"

    print("✅ All policies have required structure")


def test_flight_policy_fields():
    """Test that flight policies have required fields"""
    policy_files = [
        "docs/examples/travel_agent/config/policies/employee_policy.yaml",
        "docs/examples/travel_agent/config/policies/manager_policy.yaml",
        "docs/examples/travel_agent/config/policies/executive_policy.yaml",
        "docs/examples/travel_agent/config/policies/approving_manager_policy.yaml",
    ]

    required_fields = ["max_cost_per_person", "allowed_classes"]

    for policy_file in policy_files:
        with open(policy_file, 'r') as f:
            policy = yaml.safe_load(f)

        for field in required_fields:
            assert field in policy["flight_policy"], (
                f"Missing field '{field}' in flight_policy of {policy_file}"
            )

    print("✅ All flight policies have required fields")


def test_hotel_policy_fields():
    """Test that hotel policies have required fields"""
    policy_files = [
        "docs/examples/travel_agent/config/policies/employee_policy.yaml",
        "docs/examples/travel_agent/config/policies/manager_policy.yaml",
        "docs/examples/travel_agent/config/policies/executive_policy.yaml",
        "docs/examples/travel_agent/config/policies/approving_manager_policy.yaml",
    ]

    required_fields = ["max_rate_per_night", "min_rating"]

    for policy_file in policy_files:
        with open(policy_file, 'r') as f:
            policy = yaml.safe_load(f)

        for field in required_fields:
            assert field in policy["hotel_policy"], (
                f"Missing field '{field}' in hotel_policy of {policy_file}"
            )

    print("✅ All hotel policies have required fields")


def test_budget_hierarchy():
    """Test that budget limits follow hierarchy: employee < manager < executive"""
    with open("docs/examples/travel_agent/config/policies/employee_policy.yaml", 'r') as f:
        employee = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/manager_policy.yaml", 'r') as f:
        manager = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/executive_policy.yaml", 'r') as f:
        executive = yaml.safe_load(f)

    # Check flight costs
    emp_flight = employee["flight_policy"]["max_cost_per_person"]
    mgr_flight = manager["flight_policy"]["max_cost_per_person"]
    exec_flight = executive["flight_policy"]["max_cost_per_person"]

    assert emp_flight < mgr_flight, f"Employee flight cost ({emp_flight}) should be < Manager ({mgr_flight})"
    assert mgr_flight < exec_flight, (
        f"Manager flight cost ({mgr_flight}) should be < Executive ({exec_flight})"
    )

    # Check hotel rates
    emp_hotel = employee["hotel_policy"]["max_rate_per_night"]
    mgr_hotel = manager["hotel_policy"]["max_rate_per_night"]
    exec_hotel = executive["hotel_policy"]["max_rate_per_night"]

    assert emp_hotel < mgr_hotel, f"Employee hotel rate ({emp_hotel}) should be < Manager ({mgr_hotel})"
    assert mgr_hotel < exec_hotel, f"Manager hotel rate ({mgr_hotel}) should be < Executive ({exec_hotel})"

    # Check total budgets
    emp_budget = employee["expense_policy"]["max_total_budget"]
    mgr_budget = manager["expense_policy"]["max_total_budget"]
    exec_budget = executive["expense_policy"]["max_total_budget"]

    assert emp_budget < mgr_budget, f"Employee budget ({emp_budget}) should be < Manager ({mgr_budget})"
    assert mgr_budget < exec_budget, f"Manager budget ({mgr_budget}) should be < Executive ({exec_budget})"

    print("✅ Budget hierarchy is correct (employee < manager < executive)")
    print(f"   Flight costs: ${emp_flight} < ${mgr_flight} < ${exec_flight}")
    print(f"   Hotel rates: ${emp_hotel} < ${mgr_hotel} < ${exec_hotel}")
    print(f"   Total budgets: ${emp_budget} < ${mgr_budget} < ${exec_budget}")


def test_per_diem_hierarchy():
    """Test that per diem follows hierarchy"""
    with open("docs/examples/travel_agent/config/policies/employee_policy.yaml", 'r') as f:
        employee = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/manager_policy.yaml", 'r') as f:
        manager = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/executive_policy.yaml", 'r') as f:
        executive = yaml.safe_load(f)

    # Check meal per diem
    emp_meal = employee["expense_policy"]["meal_per_diem"]
    mgr_meal = manager["expense_policy"]["meal_per_diem"]
    exec_meal = executive["expense_policy"]["meal_per_diem"]

    assert emp_meal < mgr_meal < exec_meal, "Meal per diem should follow hierarchy"

    print(f"✅ Per diem hierarchy is correct: ${emp_meal} < ${mgr_meal} < ${exec_meal}")


def test_role_names():
    """Test that role names are correct"""
    policies = {
        "employee": "docs/examples/travel_agent/config/policies/employee_policy.yaml",
        "manager": "docs/examples/travel_agent/config/policies/manager_policy.yaml",
        "executive": "docs/examples/travel_agent/config/policies/executive_policy.yaml",
        "approving_manager": "docs/examples/travel_agent/config/policies/approving_manager_policy.yaml",
    }

    for expected_role, policy_file in policies.items():
        with open(policy_file, 'r') as f:
            policy = yaml.safe_load(f)

        assert policy["role"] == expected_role, (
            f"Role mismatch in {policy_file}: expected '{expected_role}', got '{policy['role']}'"
        )

    print("✅ All role names are correct")


def test_approval_hierarchy():
    """Test that approval hierarchy is correct"""
    with open("docs/examples/travel_agent/config/policies/employee_policy.yaml", 'r') as f:
        employee = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/manager_policy.yaml", 'r') as f:
        manager = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/executive_policy.yaml", 'r') as f:
        executive = yaml.safe_load(f)
    with open("docs/examples/travel_agent/config/policies/approving_manager_policy.yaml", 'r') as f:
        approving_manager = yaml.safe_load(f)

    # Check that employee, manager, and executive require approving_manager approval
    assert employee["approval_policy"]["approval_required"]
    assert employee["approval_policy"]["approver_role"] == "approving_manager"

    assert manager["approval_policy"]["approval_required"]
    assert manager["approval_policy"]["approver_role"] == "approving_manager"

    assert executive["approval_policy"]["approval_required"]
    assert executive["approval_policy"]["approver_role"] == "approving_manager"

    # Check that approving_manager doesn't require approval
    assert not approving_manager["approval_policy"]["requires_approval"]
    assert approving_manager["approval_policy"]["approver_role"] == "none"

    print("✅ Approval hierarchy is correct:")
    print("   - Employee → Approving Manager")
    print("   - Manager → Approving Manager")
    print("   - Executive → Approving Manager")
    print("   - Approving Manager → Auto-approved")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Policy Configurations")
    print("=" * 60 + "\n")

    try:
        test_all_policies_exist()
        test_policy_structure()
        test_flight_policy_fields()
        test_hotel_policy_fields()
        test_budget_hierarchy()
        test_per_diem_hierarchy()
        test_role_names()
        test_approval_hierarchy()

        print("\n" + "=" * 60)
        print("✅ All policy configuration tests passed!")
        print("=" * 60 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)

# Made with Bob
