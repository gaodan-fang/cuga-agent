"""
Flight Agent Tools - Search and filter flights using SerpAPI Google Flights

This module provides tools for:
- Searching flights between origin and destination
- Filtering flights by price range
- Filtering flights by airline
- Finding cheapest flight options
"""

import os
import json
from typing import Optional
from serpapi import GoogleSearch
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    travel_class: str = "economy",
) -> str:
    """
    Search for flights between origin and destination using SerpAPI Google Flights.

    Args:
        origin: Origin airport code (e.g., 'JFK', 'LAX', 'ORD')
        destination: Destination airport code (e.g., 'LAX', 'SFO', 'MIA')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional for one-way)
        passengers: Number of passengers (default: 1)
        travel_class: Flight class - 1=economy, 2=premium_economy, 3=business, 4=first (default: economy)

    Returns:
        JSON string with flight options including prices, airlines, times, and durations

    Example:
        search_flights('JFK', 'LAX', '2026-04-15', '2026-04-20', 1, 'economy')
    """
    try:
        # Validate inputs
        if not origin or not destination:
            return json.dumps({"success": False, "error": "Origin and destination are required"})

        if not departure_date:
            return json.dumps({"success": False, "error": "Departure date is required"})

        # Map travel class names to SerpAPI numeric values
        class_mapping = {"economy": "1", "premium_economy": "2", "business": "3", "first": "4"}
        travel_class_value = class_mapping.get(travel_class.lower(), "1")

        # Build SerpAPI parameters
        params = {
            "engine": "google_flights",
            "departure_id": origin.upper(),
            "arrival_id": destination.upper(),
            "outbound_date": departure_date,
            "currency": "USD",
            "hl": "en",
            "api_key": SERPAPI_KEY,
            "type": "1" if return_date else "2",  # 1=round-trip, 2=one-way
            "adults": passengers,
            "travel_class": travel_class_value,
        }

        if return_date:
            params["return_date"] = return_date

        # Execute search
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract and format flight options
        flights = []
        if "best_flights" in results:
            for flight in results["best_flights"][:10]:  # Top 10 flights
                flight_info = {
                    "airline": flight.get("flights", [{}])[0].get("airline", "Unknown"),
                    "flight_number": flight.get("flights", [{}])[0].get("flight_number", "N/A"),
                    "departure_airport": flight.get("flights", [{}])[0]
                    .get("departure_airport", {})
                    .get("id", origin),
                    "arrival_airport": flight.get("flights", [{}])[-1]
                    .get("arrival_airport", {})
                    .get("id", destination),
                    "departure_time": flight.get("flights", [{}])[0]
                    .get("departure_airport", {})
                    .get("time", "N/A"),
                    "arrival_time": flight.get("flights", [{}])[-1]
                    .get("arrival_airport", {})
                    .get("time", "N/A"),
                    "duration": flight.get("total_duration", "N/A"),
                    "stops": len(flight.get("flights", [])) - 1,
                    "price": flight.get("price", 0),
                    "carbon_emissions": flight.get("carbon_emissions", {}).get("this_flight", 0),
                    "layovers": [
                        f.get("layover", {}).get("duration", 0) for f in flight.get("flights", [])[:-1]
                    ],
                    "travel_class": travel_class,
                }
                flights.append(flight_info)

        # Also check other_flights if available
        if "other_flights" in results and len(flights) < 10:
            for flight in results["other_flights"][: 10 - len(flights)]:
                flight_info = {
                    "airline": flight.get("flights", [{}])[0].get("airline", "Unknown"),
                    "flight_number": flight.get("flights", [{}])[0].get("flight_number", "N/A"),
                    "departure_airport": flight.get("flights", [{}])[0]
                    .get("departure_airport", {})
                    .get("id", origin),
                    "arrival_airport": flight.get("flights", [{}])[-1]
                    .get("arrival_airport", {})
                    .get("id", destination),
                    "departure_time": flight.get("flights", [{}])[0]
                    .get("departure_airport", {})
                    .get("time", "N/A"),
                    "arrival_time": flight.get("flights", [{}])[-1]
                    .get("arrival_airport", {})
                    .get("time", "N/A"),
                    "duration": flight.get("total_duration", "N/A"),
                    "stops": len(flight.get("flights", [])) - 1,
                    "price": flight.get("price", 0),
                    "carbon_emissions": flight.get("carbon_emissions", {}).get("this_flight", 0),
                    "layovers": [
                        f.get("layover", {}).get("duration", 0) for f in flight.get("flights", [])[:-1]
                    ],
                    "travel_class": travel_class,
                }
                flights.append(flight_info)

        return json.dumps(
            {
                "success": True,
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "travel_class": travel_class,
                "flights_found": len(flights),
                "flights": flights,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "message": "Failed to search flights. Please check your API key and parameters.",
            },
            indent=2,
        )


@tool
def filter_flights_by_price(flights_json: str, max_price: float) -> str:
    """
    Filter flight options by maximum price per person.

    Args:
        flights_json: JSON string from search_flights result
        max_price: Maximum price per person in USD

    Returns:
        JSON string with filtered flights within price range

    Example:
        filter_flights_by_price(flights_json, 500.00)
    """
    try:
        data = json.loads(flights_json) if isinstance(flights_json, str) else flights_json

        if not data.get("success"):
            return flights_json

        filtered_flights = [
            flight for flight in data.get("flights", []) if flight.get("price", float('inf')) <= max_price
        ]

        data["flights"] = filtered_flights
        data["flights_found"] = len(filtered_flights)
        data["filter_applied"] = f"max_price <= ${max_price}"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter flights by price"}, indent=2
        )


@tool
def filter_flights_by_airline(flights_json: str, airlines: str) -> str:
    """
    Filter flight options by specific airlines.

    Args:
        flights_json: JSON string from search_flights result
        airlines: Comma-separated airline names (e.g., 'United,Delta,American')

    Returns:
        JSON string with filtered flights from specified airlines

    Example:
        filter_flights_by_airline(flights_json, 'United,Delta')
    """
    try:
        data = json.loads(flights_json) if isinstance(flights_json, str) else flights_json

        if not data.get("success"):
            return flights_json

        # Parse airlines list
        airline_list = [a.strip() for a in airlines.split(',')]
        airlines_lower = [a.lower() for a in airline_list]

        filtered_flights = [
            flight
            for flight in data.get("flights", [])
            if any(airline in flight.get("airline", "").lower() for airline in airlines_lower)
        ]

        data["flights"] = filtered_flights
        data["flights_found"] = len(filtered_flights)
        data["filter_applied"] = f"airlines in {airline_list}"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter flights by airline"}, indent=2
        )


@tool
def get_cheapest_flight(flights_json: str) -> str:
    """
    Get the cheapest flight option from search results.

    Args:
        flights_json: JSON string from search_flights result

    Returns:
        JSON string with the cheapest flight details

    Example:
        get_cheapest_flight(flights_json)
    """
    try:
        data = json.loads(flights_json) if isinstance(flights_json, str) else flights_json

        if not data.get("success") or not data.get("flights"):
            return json.dumps({"success": False, "message": "No flights available"}, indent=2)

        cheapest = min(data["flights"], key=lambda x: x.get("price", float('inf')))

        # Calculate savings compared to most expensive
        most_expensive = max(data["flights"], key=lambda x: x.get("price", 0))
        savings = most_expensive.get("price", 0) - cheapest.get("price", 0)

        return json.dumps(
            {
                "success": True,
                "cheapest_flight": cheapest,
                "savings_vs_most_expensive": round(savings, 2),
                "total_flights_compared": len(data["flights"]),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def filter_direct_flights_only(flights_json: str) -> str:
    """
    Filter to show only direct (non-stop) flights.

    Args:
        flights_json: JSON string from search_flights result

    Returns:
        JSON string with only direct flights

    Example:
        filter_direct_flights_only(flights_json)
    """
    try:
        data = json.loads(flights_json) if isinstance(flights_json, str) else flights_json

        if not data.get("success"):
            return flights_json

        direct_flights = [flight for flight in data.get("flights", []) if flight.get("stops", 1) == 0]

        data["flights"] = direct_flights
        data["flights_found"] = len(direct_flights)
        data["filter_applied"] = "direct flights only (0 stops)"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter direct flights"}, indent=2
        )


# Made with Bob
