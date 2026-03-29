"""
Finance Agent Tools - Calculate expenses and generate reports

This module provides tools for:
- Calculating flight costs
- Calculating hotel costs
- Calculating per diem allowances
- Generating expense reports
- Validating budgets
"""

import json
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def calculate_flight_costs(
    flight_price: float, passengers: int = 1, baggage_fees: float = 0.0, seat_selection_fees: float = 0.0
) -> str:
    """
    Calculate total flight costs including additional fees.

    Args:
        flight_price: Base flight price per person
        passengers: Number of passengers
        baggage_fees: Additional baggage fees per person
        seat_selection_fees: Seat selection fees per person

    Returns:
        JSON string with detailed flight cost breakdown

    Example:
        calculate_flight_costs(350.00, 1, 30.00, 15.00)
    """
    try:
        base_cost = flight_price * passengers
        total_baggage = baggage_fees * passengers
        total_seat_fees = seat_selection_fees * passengers

        total_cost = base_cost + total_baggage + total_seat_fees

        return json.dumps(
            {
                "success": True,
                "category": "flights",
                "breakdown": {
                    "base_flight_cost": round(base_cost, 2),
                    "baggage_fees": round(total_baggage, 2),
                    "seat_selection_fees": round(total_seat_fees, 2),
                },
                "passengers": passengers,
                "cost_per_person": round(total_cost / passengers, 2),
                "total_cost": round(total_cost, 2),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def calculate_hotel_costs(
    price_per_night: float, num_nights: int, num_rooms: int = 1, taxes_and_fees_percent: float = 15.0
) -> str:
    """
    Calculate total hotel costs including taxes and fees.

    Args:
        price_per_night: Hotel price per night per room
        num_nights: Number of nights
        num_rooms: Number of rooms
        taxes_and_fees_percent: Taxes and fees as percentage (default: 15%)

    Returns:
        JSON string with detailed hotel cost breakdown

    Example:
        calculate_hotel_costs(150.00, 5, 1, 15.0)
    """
    try:
        base_cost = price_per_night * num_nights * num_rooms
        taxes_and_fees = base_cost * (taxes_and_fees_percent / 100)
        total_cost = base_cost + taxes_and_fees

        return json.dumps(
            {
                "success": True,
                "category": "accommodation",
                "breakdown": {
                    "base_hotel_cost": round(base_cost, 2),
                    "taxes_and_fees": round(taxes_and_fees, 2),
                    "taxes_and_fees_percent": taxes_and_fees_percent,
                },
                "price_per_night": price_per_night,
                "num_nights": num_nights,
                "num_rooms": num_rooms,
                "cost_per_night": round(total_cost / num_nights, 2),
                "total_cost": round(total_cost, 2),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def calculate_per_diem(
    num_days: int,
    daily_meal_allowance: float = 50.0,
    daily_transport_allowance: float = 25.0,
    daily_incidentals: float = 10.0,
) -> str:
    """
    Calculate per diem allowances for meals, transport, and incidentals.

    Args:
        num_days: Number of days
        daily_meal_allowance: Daily meal allowance (default: $50)
        daily_transport_allowance: Daily local transport allowance (default: $25)
        daily_incidentals: Daily incidental expenses (default: $10)

    Returns:
        JSON string with per diem breakdown

    Example:
        calculate_per_diem(5, 50.0, 25.0, 10.0)
    """
    try:
        total_meals = daily_meal_allowance * num_days
        total_transport = daily_transport_allowance * num_days
        total_incidentals = daily_incidentals * num_days

        total_per_diem = total_meals + total_transport + total_incidentals

        return json.dumps(
            {
                "success": True,
                "category": "per_diem",
                "breakdown": {
                    "meals": round(total_meals, 2),
                    "local_transport": round(total_transport, 2),
                    "incidentals": round(total_incidentals, 2),
                },
                "daily_rates": {
                    "meals": daily_meal_allowance,
                    "transport": daily_transport_allowance,
                    "incidentals": daily_incidentals,
                    "total_per_day": round(
                        daily_meal_allowance + daily_transport_allowance + daily_incidentals, 2
                    ),
                },
                "num_days": num_days,
                "total_per_diem": round(total_per_diem, 2),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def generate_expense_report(
    flight_costs_json: str,
    hotel_costs_json: str,
    per_diem_json: str,
    additional_expenses: Optional[str] = None,
) -> str:
    """
    Generate comprehensive expense report from all cost components.

    Args:
        flight_costs_json: JSON from calculate_flight_costs
        hotel_costs_json: JSON from calculate_hotel_costs
        per_diem_json: JSON from calculate_per_diem
        additional_expenses: Optional JSON string with additional expenses

    Returns:
        JSON string with complete expense report

    Example:
        generate_expense_report(flight_json, hotel_json, per_diem_json)
    """
    try:
        # Parse input JSONs
        flight_data = (
            json.loads(flight_costs_json) if isinstance(flight_costs_json, str) else flight_costs_json
        )
        hotel_data = json.loads(hotel_costs_json) if isinstance(hotel_costs_json, str) else hotel_costs_json
        per_diem_data = json.loads(per_diem_json) if isinstance(per_diem_json, str) else per_diem_json

        # Extract totals
        flight_total = flight_data.get("total_cost", 0)
        hotel_total = hotel_data.get("total_cost", 0)
        per_diem_total = per_diem_data.get("total_per_diem", 0)

        # Handle additional expenses
        additional_total = 0
        additional_breakdown = {}
        if additional_expenses:
            try:
                additional_data = (
                    json.loads(additional_expenses)
                    if isinstance(additional_expenses, str)
                    else additional_expenses
                )
                additional_breakdown = additional_data
                additional_total = sum(additional_data.values()) if isinstance(additional_data, dict) else 0
            except Exception:
                pass

        # Calculate grand total
        grand_total = flight_total + hotel_total + per_diem_total + additional_total

        # Build expense report
        report = {
            "success": True,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expense_summary": {
                "flights": round(flight_total, 2),
                "accommodation": round(hotel_total, 2),
                "per_diem": round(per_diem_total, 2),
                "additional_expenses": round(additional_total, 2),
                "grand_total": round(grand_total, 2),
            },
            "detailed_breakdown": {
                "flights": flight_data.get("breakdown", {}),
                "accommodation": hotel_data.get("breakdown", {}),
                "per_diem": per_diem_data.get("breakdown", {}),
                "additional": additional_breakdown,
            },
            "trip_details": {
                "passengers": flight_data.get("passengers", 1),
                "nights": hotel_data.get("num_nights", 0),
                "days": per_diem_data.get("num_days", 0),
            },
        }

        return json.dumps(report, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to generate expense report"}, indent=2
        )


@tool
def validate_budget(expense_report_json: str, budget_limit: float, role: str = "employee") -> str:
    """
    Validate if expenses are within budget limits for the user's role.

    Args:
        expense_report_json: JSON from generate_expense_report
        budget_limit: Maximum budget allowed
        role: User role (employee, manager, executive)

    Returns:
        JSON string with budget validation results

    Example:
        validate_budget(expense_report_json, 2000.00, 'employee')
    """
    try:
        # Parse expense report
        report_data = (
            json.loads(expense_report_json) if isinstance(expense_report_json, str) else expense_report_json
        )

        if not report_data.get("success"):
            return expense_report_json

        grand_total = report_data.get("expense_summary", {}).get("grand_total", 0)

        # Calculate budget status
        remaining_budget = budget_limit - grand_total
        budget_utilization = (grand_total / budget_limit * 100) if budget_limit > 0 else 0
        is_within_budget = grand_total <= budget_limit

        # Determine status
        if budget_utilization <= 80:
            status = "approved"
            status_message = "Expenses are well within budget"
        elif budget_utilization <= 100:
            status = "warning"
            status_message = "Expenses are close to budget limit"
        else:
            status = "over_budget"
            status_message = "Expenses exceed budget limit"

        # Category-wise analysis
        expense_summary = report_data.get("expense_summary", {})
        category_analysis = []

        for category, amount in expense_summary.items():
            if category != "grand_total" and amount > 0:
                percentage = (amount / grand_total * 100) if grand_total > 0 else 0
                category_analysis.append(
                    {
                        "category": category,
                        "amount": round(amount, 2),
                        "percentage_of_total": round(percentage, 1),
                    }
                )

        return json.dumps(
            {
                "success": True,
                "validation_result": {
                    "is_within_budget": is_within_budget,
                    "status": status,
                    "status_message": status_message,
                },
                "budget_details": {
                    "budget_limit": round(budget_limit, 2),
                    "total_expenses": round(grand_total, 2),
                    "remaining_budget": round(remaining_budget, 2),
                    "budget_utilization_percent": round(budget_utilization, 1),
                },
                "role": role,
                "category_analysis": category_analysis,
                "recommendations": [
                    "Review expenses before finalizing booking"
                    if not is_within_budget
                    else "Budget allocation is appropriate",
                    "Consider lower-cost alternatives"
                    if budget_utilization > 90
                    else "Good budget management",
                ],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to validate budget"}, indent=2
        )


@tool
def calculate_total_trip_cost(
    flight_price: float,
    hotel_price_per_night: float,
    num_nights: int,
    num_days: int,
    passengers: int = 1,
    daily_per_diem: float = 85.0,
) -> str:
    """
    Quick calculation of total trip cost (convenience function).

    Args:
        flight_price: Flight price per person
        hotel_price_per_night: Hotel price per night
        num_nights: Number of nights
        num_days: Number of days (for per diem)
        passengers: Number of passengers
        daily_per_diem: Daily per diem allowance

    Returns:
        JSON string with total trip cost

    Example:
        calculate_total_trip_cost(350.00, 150.00, 5, 6, 1, 85.00)
    """
    try:
        # Calculate components
        flight_total = flight_price * passengers
        hotel_total = hotel_price_per_night * num_nights * 1.15  # Include 15% taxes
        per_diem_total = daily_per_diem * num_days

        grand_total = flight_total + hotel_total + per_diem_total

        return json.dumps(
            {
                "success": True,
                "quick_estimate": {
                    "flights": round(flight_total, 2),
                    "accommodation": round(hotel_total, 2),
                    "per_diem": round(per_diem_total, 2),
                    "total": round(grand_total, 2),
                },
                "trip_details": {"passengers": passengers, "nights": num_nights, "days": num_days},
                "note": "This is a quick estimate. Use detailed calculation tools for accurate reporting.",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# Made with Bob
