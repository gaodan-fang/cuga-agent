"""
Compliance Agent Tools - Enforce role-based travel policies

This module provides tools for:
- Loading user policies from YAML files
- Validating flights against policy
- Validating hotels against policy
- Validating total budget
- Checking overall compliance
- Suggesting compliant alternatives
"""

import os
import json
import yaml
from langchain_core.tools import tool
from langchain_core.tools import tool as langchain_tool
from dotenv import load_dotenv

load_dotenv()

# Policy file paths
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "config", "policies")


@tool
def load_user_policy(role: str = "employee") -> str:
    """
    Load role-based travel policy from YAML configuration.

    Args:
        role: User role - 'employee', 'manager', 'executive', or 'approving_manager'

    Returns:
        JSON string with policy details

    Example:
        load_user_policy('employee')
    """
    try:
        # Normalize role
        role = role.lower().strip()

        # Map role to policy file
        policy_files = {
            "employee": "employee_policy.yaml",
            "manager": "manager_policy.yaml",
            "executive": "executive_policy.yaml",
            "approving_manager": "approving_manager_policy.yaml",
        }

        if role not in policy_files:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Invalid role: {role}. Must be 'employee', 'manager', 'executive', or 'approving_manager'",
                }
            )

        policy_file = os.path.join(POLICY_DIR, policy_files[role])

        # Check if policy file exists
        if not os.path.exists(policy_file):
            # Return default policy if file doesn't exist yet
            default_policies = {
                "employee": {
                    "role": "employee",
                    "flight_class_allowed": ["economy"],
                    "max_flight_cost": 500,
                    "max_hotel_per_night": 150,
                    "total_budget_limit": 2000,
                    "per_diem": {"meals": 50, "transport": 25, "incidentals": 10},
                },
                "manager": {
                    "role": "manager",
                    "flight_class_allowed": ["economy", "premium_economy"],
                    "max_flight_cost": 800,
                    "max_hotel_per_night": 250,
                    "total_budget_limit": 4000,
                    "per_diem": {"meals": 75, "transport": 35, "incidentals": 15},
                },
                "executive": {
                    "role": "executive",
                    "flight_class_allowed": ["economy", "premium_economy", "business"],
                    "max_flight_cost": 1500,
                    "max_hotel_per_night": 400,
                    "total_budget_limit": 8000,
                    "per_diem": {"meals": 100, "transport": 50, "incidentals": 20},
                },
                "approving_manager": {
                    "role": "approving_manager",
                    "flight_class_allowed": ["economy", "premium_economy", "business"],
                    "max_flight_cost": 1500,
                    "max_hotel_per_night": 400,
                    "total_budget_limit": 8000,
                    "per_diem": {"meals": 100, "transport": 50, "incidentals": 20},
                },
            }

            policy = default_policies.get(role, default_policies["employee"])

            return json.dumps(
                {
                    "success": True,
                    "policy": policy,
                    "source": "default",
                    "note": "Using default policy. Policy file not found.",
                },
                indent=2,
            )

        # Load policy from file
        with open(policy_file, 'r') as f:
            policy = yaml.safe_load(f)

        return json.dumps(
            {"success": True, "policy": policy, "source": "file", "file_path": policy_file}, indent=2
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "message": "Failed to load policy"}, indent=2)


@tool
def validate_flight_policy(flight_price: float, flight_class: str, policy_json: str) -> str:
    """
    Validate if flight meets policy requirements.

    Args:
        flight_price: Flight price per person
        flight_class: Flight class (economy, premium_economy, business, first)
        policy_json: JSON from load_user_policy

    Returns:
        JSON string with validation results

    Example:
        validate_flight_policy(450.00, 'economy', policy_json)
    """
    try:
        # Parse policy
        policy_data = json.loads(policy_json) if isinstance(policy_json, str) else policy_json

        if not policy_data.get("success"):
            return policy_json

        policy = policy_data.get("policy", {})

        # Extract policy limits
        max_flight_cost = policy.get("max_flight_cost", 500)
        allowed_classes = policy.get("flight_class_allowed", ["economy"])

        # Normalize flight class
        flight_class_normalized = flight_class.lower().replace(" ", "_")

        # Validate price
        price_compliant = flight_price <= max_flight_cost
        price_difference = flight_price - max_flight_cost

        # Validate class
        class_compliant = flight_class_normalized in [c.lower().replace(" ", "_") for c in allowed_classes]

        # Overall compliance
        is_compliant = price_compliant and class_compliant

        violations = []
        if not price_compliant:
            violations.append(f"Flight price ${flight_price} exceeds limit of ${max_flight_cost}")
        if not class_compliant:
            violations.append(
                f"Flight class '{flight_class}' not allowed. Permitted: {', '.join(allowed_classes)}"
            )

        return json.dumps(
            {
                "success": True,
                "is_compliant": is_compliant,
                "validation_details": {
                    "price_compliant": price_compliant,
                    "class_compliant": class_compliant,
                    "flight_price": flight_price,
                    "max_allowed": max_flight_cost,
                    "price_difference": round(price_difference, 2) if not price_compliant else 0,
                    "flight_class": flight_class,
                    "allowed_classes": allowed_classes,
                },
                "violations": violations,
                "role": policy.get("role", "unknown"),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to validate flight policy"}, indent=2
        )


@tool
def validate_hotel_policy(hotel_price_per_night: float, num_nights: int, policy_json: str) -> str:
    """
    Validate if hotel meets policy requirements.

    Args:
        hotel_price_per_night: Hotel price per night
        num_nights: Number of nights
        policy_json: JSON from load_user_policy

    Returns:
        JSON string with validation results

    Example:
        validate_hotel_policy(140.00, 5, policy_json)
    """
    try:
        # Parse policy
        policy_data = json.loads(policy_json) if isinstance(policy_json, str) else policy_json

        if not policy_data.get("success"):
            return policy_json

        policy = policy_data.get("policy", {})

        # Extract policy limits
        max_hotel_per_night = policy.get("max_hotel_per_night", 150)

        # Validate price per night
        price_compliant = hotel_price_per_night <= max_hotel_per_night
        price_difference = hotel_price_per_night - max_hotel_per_night

        # Calculate total hotel cost
        total_hotel_cost = hotel_price_per_night * num_nights
        max_total_hotel = max_hotel_per_night * num_nights

        violations = []
        if not price_compliant:
            violations.append(
                f"Hotel price ${hotel_price_per_night}/night exceeds limit of ${max_hotel_per_night}/night"
            )

        return json.dumps(
            {
                "success": True,
                "is_compliant": price_compliant,
                "validation_details": {
                    "price_per_night": hotel_price_per_night,
                    "max_allowed_per_night": max_hotel_per_night,
                    "price_difference_per_night": round(price_difference, 2) if not price_compliant else 0,
                    "num_nights": num_nights,
                    "total_hotel_cost": round(total_hotel_cost, 2),
                    "max_total_allowed": round(max_total_hotel, 2),
                },
                "violations": violations,
                "role": policy.get("role", "unknown"),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to validate hotel policy"}, indent=2
        )


@tool
def validate_total_budget(total_cost: float, policy_json: str) -> str:
    """
    Validate if total trip cost is within budget limit.

    Args:
        total_cost: Total trip cost
        policy_json: JSON from load_user_policy

    Returns:
        JSON string with budget validation results

    Example:
        validate_total_budget(1850.00, policy_json)
    """
    try:
        # Parse policy
        policy_data = json.loads(policy_json) if isinstance(policy_json, str) else policy_json

        if not policy_data.get("success"):
            return policy_json

        policy = policy_data.get("policy", {})

        # Extract budget limit
        budget_limit = policy.get("total_budget_limit", 2000)

        # Validate budget
        is_within_budget = total_cost <= budget_limit
        budget_utilization = (total_cost / budget_limit * 100) if budget_limit > 0 else 0

        # Determine status
        if budget_utilization <= 80:
            status = "excellent"
            message = "Well within budget"
        elif budget_utilization <= 95:
            status = "good"
            message = "Within budget with some room"
        elif budget_utilization <= 100:
            status = "warning"
            message = "Very close to budget limit"
        else:
            status = "over_budget"
            message = "Exceeds budget limit"

        violations = []
        if not is_within_budget:
            violations.append(f"Total cost ${total_cost} exceeds budget limit of ${budget_limit}")

        return json.dumps(
            {
                "success": True,
                "is_within_budget": is_within_budget,
                "validation_details": {
                    "total_cost": round(total_cost, 2),
                    "budget_limit": round(budget_limit, 2),
                    "remaining_budget": round(budget_limit - total_cost, 2),
                    "budget_utilization_percent": round(budget_utilization, 1),
                    "status": status,
                    "status_message": message,
                },
                "violations": violations,
                "role": policy.get("role", "unknown"),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to validate total budget"}, indent=2
        )


@tool
def check_overall_compliance(
    flight_validation_json: str, hotel_validation_json: str, budget_validation_json: str
) -> str:
    """
    Check overall compliance across all policy areas.

    Args:
        flight_validation_json: JSON from validate_flight_policy
        hotel_validation_json: JSON from validate_hotel_policy
        budget_validation_json: JSON from validate_total_budget

    Returns:
        JSON string with comprehensive compliance report

    Example:
        check_overall_compliance(flight_val, hotel_val, budget_val)
    """
    try:
        # Parse validation results
        flight_data = (
            json.loads(flight_validation_json)
            if isinstance(flight_validation_json, str)
            else flight_validation_json
        )
        hotel_data = (
            json.loads(hotel_validation_json)
            if isinstance(hotel_validation_json, str)
            else hotel_validation_json
        )
        budget_data = (
            json.loads(budget_validation_json)
            if isinstance(budget_validation_json, str)
            else budget_validation_json
        )

        # Extract compliance status
        flight_compliant = flight_data.get("is_compliant", False)
        hotel_compliant = hotel_data.get("is_compliant", False)
        budget_compliant = budget_data.get("is_within_budget", False)

        # Overall compliance
        is_fully_compliant = flight_compliant and hotel_compliant and budget_compliant

        # Collect all violations
        all_violations = []
        all_violations.extend(flight_data.get("violations", []))
        all_violations.extend(hotel_data.get("violations", []))
        all_violations.extend(budget_data.get("violations", []))

        # Determine approval status
        if is_fully_compliant:
            approval_status = "auto_approved"
            approval_message = "Trip meets all policy requirements"
        elif len(all_violations) <= 2:
            approval_status = "requires_manager_approval"
            approval_message = "Minor policy violations - manager approval required"
        else:
            approval_status = "rejected"
            approval_message = "Multiple policy violations - trip needs revision"

        # Generate recommendations
        recommendations = []
        if not flight_compliant:
            recommendations.append("Consider lower-cost flights or economy class")
        if not hotel_compliant:
            recommendations.append("Select hotels within nightly rate limit")
        if not budget_compliant:
            recommendations.append("Reduce overall trip costs to meet budget")

        if is_fully_compliant:
            recommendations.append("Trip is policy-compliant and ready for booking")

        return json.dumps(
            {
                "success": True,
                "is_fully_compliant": is_fully_compliant,
                "compliance_summary": {
                    "flight_compliant": flight_compliant,
                    "hotel_compliant": hotel_compliant,
                    "budget_compliant": budget_compliant,
                },
                "approval_status": approval_status,
                "approval_message": approval_message,
                "total_violations": len(all_violations),
                "violations": all_violations,
                "recommendations": recommendations,
                "next_steps": [
                    "Proceed with booking" if is_fully_compliant else "Revise trip to meet policy",
                    "Submit for manager approval" if approval_status == "requires_manager_approval" else "",
                ],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to check overall compliance"}, indent=2
        )


@tool
def suggest_compliant_alternatives(
    current_flight_price: float, current_hotel_price: float, policy_json: str
) -> str:
    """
    Suggest policy-compliant alternatives based on current selections.

    Args:
        current_flight_price: Current flight price
        current_hotel_price: Current hotel price per night
        policy_json: JSON from load_user_policy

    Returns:
        JSON string with compliant alternative suggestions

    Example:
        suggest_compliant_alternatives(600.00, 200.00, policy_json)
    """
    try:
        # Parse policy
        policy_data = json.loads(policy_json) if isinstance(policy_json, str) else policy_json

        if not policy_data.get("success"):
            return policy_json

        policy = policy_data.get("policy", {})

        # Extract limits
        max_flight = policy.get("max_flight_cost", 500)
        max_hotel = policy.get("max_hotel_per_night", 150)
        allowed_classes = policy.get("flight_class_allowed", ["economy"])

        suggestions = []

        # Flight suggestions
        if current_flight_price > max_flight:
            flight_reduction_needed = current_flight_price - max_flight
            suggestions.append(
                {
                    "category": "flight",
                    "issue": f"Current flight ${current_flight_price} exceeds limit",
                    "target": f"Find flights under ${max_flight}",
                    "reduction_needed": round(flight_reduction_needed, 2),
                    "tips": [
                        "Book in advance for better rates",
                        "Consider connecting flights instead of direct",
                        f"Ensure flight class is {' or '.join(allowed_classes)}",
                        "Check alternative airports nearby",
                        "Be flexible with travel dates",
                    ],
                }
            )

        # Hotel suggestions
        if current_hotel_price > max_hotel:
            hotel_reduction_needed = current_hotel_price - max_hotel
            suggestions.append(
                {
                    "category": "hotel",
                    "issue": f"Current hotel ${current_hotel_price}/night exceeds limit",
                    "target": f"Find hotels under ${max_hotel}/night",
                    "reduction_needed": round(hotel_reduction_needed, 2),
                    "tips": [
                        "Consider hotels slightly outside city center",
                        "Look for business-class hotels instead of luxury",
                        "Check for corporate rates or discounts",
                        "Consider hotel chains with loyalty programs",
                        "Book directly with hotel for better rates",
                    ],
                }
            )

        # General budget tips
        general_tips = [
            "Combine cost savings across flight and hotel",
            "Book both together for package deals",
            "Travel during off-peak times for lower rates",
            "Use company travel portal if available",
        ]

        return json.dumps(
            {
                "success": True,
                "policy_limits": {
                    "max_flight_cost": max_flight,
                    "max_hotel_per_night": max_hotel,
                    "allowed_flight_classes": allowed_classes,
                },
                "current_selections": {
                    "flight_price": current_flight_price,
                    "hotel_price_per_night": current_hotel_price,
                },
                "suggestions": suggestions,
                "general_tips": general_tips,
                "role": policy.get("role", "unknown"),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to generate suggestions"}, indent=2
        )


# Made with Bob


@tool
def filter_travel_options(
    flights_json: str, hotels_json: str, role: str = "employee", max_results: int = 5
) -> str:
    """
    Filter flights and hotels based on role policy. Returns at most max_results of each.
    This is a deterministic code-based filter - no LLM involved.

    Args:
        flights_json: JSON string with list of flights (each with 'price' field)
        hotels_json: JSON string with list of hotels (each with 'price_per_night' field)
        role: User role for policy lookup
        max_results: Maximum number of compliant results to return (default: 5)

    Returns:
        JSON string with filtered results, policy limits, and counts

    Example:
        filter_travel_options('[{"airline": "AA", "price": 450}, ...]', '[{"name": "Hotel", "price_per_night": 120}, ...]', 'employee', 5)
    """
    try:
        import json

        # Load policy
        policy_result = load_user_policy.invoke({"role": role})
        policy_data = json.loads(policy_result)

        if not policy_data.get("success"):
            return json.dumps({"success": False, "error": "Failed to load policy"})

        policy = policy_data["policy"]

        # Get limits from policy
        flight_policy = policy.get("flight_policy", {})
        hotel_policy = policy.get("hotel_policy", {})

        max_flight_cost = flight_policy.get("max_cost_per_person", 500)
        max_hotel_per_night = hotel_policy.get("max_rate_per_night", 150)

        # Parse input
        flights = json.loads(flights_json) if isinstance(flights_json, str) else flights_json
        hotels = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        # Filter flights
        compliant_flights = []
        for flight in flights:
            price = flight.get("price", 0)
            if isinstance(price, str):
                # Extract number from string like "$450" or "450"
                price = float(''.join(c for c in price if c.isdigit() or c == '.'))
            if price <= max_flight_cost:
                compliant_flights.append(flight)

        # Filter hotels
        compliant_hotels = []
        for hotel in hotels:
            price_per_night = hotel.get("price_per_night", 0)
            if isinstance(price_per_night, str):
                price_per_night = float(''.join(c for c in price_per_night if c.isdigit() or c == '.'))
            if price_per_night <= max_hotel_per_night:
                compliant_hotels.append(hotel)

        # Limit to max_results
        filtered_flights = compliant_flights[:max_results]
        filtered_hotels = compliant_hotels[:max_results]

        # Calculate counts
        total_flights = len(flights)
        total_hotels = len(hotels)
        flights_filtered = total_flights - len(filtered_flights)
        hotels_filtered = total_hotels - len(filtered_hotels)

        return json.dumps(
            {
                "success": True,
                "policy_limits": {
                    "role": role,
                    "max_flight_cost": max_flight_cost,
                    "max_hotel_per_night": max_hotel_per_night,
                },
                "compliant_flights": filtered_flights,
                "compliant_hotels": filtered_hotels,
                "counts": {
                    "total_flights": total_flights,
                    "compliant_flights": len(filtered_flights),
                    "flights_filtered": flights_filtered,
                    "total_hotels": total_hotels,
                    "compliant_hotels": len(filtered_hotels),
                    "hotels_filtered": hotels_filtered,
                },
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter travel options"}, indent=2
        )


"""
Compliance Agent Tools - LLM-based policy enforcement with Cuga Tool Guides

NEW: analyze_travel_compliance - Simple LLM-based tool that works with Tool Guides
OLD: Deterministic validation tools (kept as fallback)
"""


@langchain_tool
def analyze_travel_compliance(flights_json: str, hotels_json: str, role: str = "employee") -> str:
    """
    Analyze travel options for policy compliance using LLM reasoning.

    This tool receives flight and hotel options and applies role-based
    company travel policies to filter and validate them. The Tool Guide
    system injects detailed policy constraints into this tool's context.

    Args:
        flights_json: JSON string with list of flight options
        hotels_json: JSON string with list of hotel options
        role: User role (employee, manager, executive)

    Returns:
        Analysis of compliant options with explanations

    Example:
        analyze_travel_compliance(
            flights_json='[{"airline": "United", "price": 450, "class": "economy"}]',
            hotels_json='[{"name": "Budget Inn", "price_per_night": 120}]',
            role="employee"
        )

    Note:
        This tool uses LLM reasoning guided by Cuga's Tool Guide policy system.
        The Tool Guide injects role-specific policy constraints (max prices,
        allowed classes, budget limits) directly into the tool's context.
    """
    # This is a placeholder - the actual work is done by the LLM
    # with policy guidance from the Tool Guide system
    return f"""
    Analyzing travel options for {role} role...
    
    Please apply the role-based policy constraints to filter these options:
    - Flights: {flights_json}
    - Hotels: {hotels_json}
    
    Return compliant options with explanations.
    """


# ============================================================================
# ORIGINAL DETERMINISTIC TOOLS (kept as fallback)
# ============================================================================
