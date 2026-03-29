"""
Hotel Agent Tools - Search and filter hotels using SerpAPI Google Hotels

This module provides tools for:
- Searching hotels by location and dates
- Filtering hotels by price range
- Filtering hotels by star rating
- Filtering hotels by amenities
- Finding best value hotels
"""

import os
import json
from serpapi import GoogleSearch
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")


@tool
def search_hotels(
    location: str, check_in_date: str, check_out_date: str, guests: int = 1, rooms: int = 1
) -> str:
    """
    Search for hotels in a specific location using SerpAPI Google Hotels.

    Args:
        location: City or location name (e.g., 'Los Angeles', 'New York', 'San Francisco')
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 1)
        rooms: Number of rooms (default: 1)

    Returns:
        JSON string with hotel options including prices, ratings, and amenities

    Example:
        search_hotels('Los Angeles', '2026-04-15', '2026-04-20', 2, 1)
    """
    try:
        # Validate inputs
        if not location:
            return json.dumps({"success": False, "error": "Location is required"})

        if not check_in_date or not check_out_date:
            return json.dumps({"success": False, "error": "Check-in and check-out dates are required"})

        # Build SerpAPI parameters
        params = {
            "engine": "google_hotels",
            "q": f"Hotels in {location}",
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": guests,
            "currency": "USD",
            "gl": "us",
            "hl": "en",
            "api_key": SERPAPI_KEY,
        }

        # Execute search
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract and format hotel options
        hotels = []
        if "properties" in results:
            for hotel in results["properties"][:15]:  # Top 15 hotels
                hotel_info = {
                    "name": hotel.get("name", "Unknown Hotel"),
                    "type": hotel.get("type", "Hotel"),
                    "description": hotel.get("description", ""),
                    "rating": hotel.get("overall_rating", 0),
                    "reviews": hotel.get("reviews", 0),
                    "price_per_night": hotel.get("rate_per_night", {}).get("lowest", "N/A"),
                    "total_price": hotel.get("total_rate", {}).get("lowest", "N/A"),
                    "amenities": hotel.get("amenities", []),
                    "images": hotel.get("images", [])[:3],  # First 3 images
                    "link": hotel.get("link", ""),
                    "gps_coordinates": hotel.get("gps_coordinates", {}),
                    "check_in_time": hotel.get("check_in_time", "N/A"),
                    "check_out_time": hotel.get("check_out_time", "N/A"),
                    "nearby_places": hotel.get("nearby_places", [])[:5],  # Top 5 nearby places
                }
                hotels.append(hotel_info)

        return json.dumps(
            {
                "success": True,
                "location": location,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "guests": guests,
                "rooms": rooms,
                "hotels_found": len(hotels),
                "hotels": hotels,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "message": "Failed to search hotels. Please check your API key and parameters.",
            },
            indent=2,
        )


@tool
def filter_hotels_by_price(hotels_json: str, max_price_per_night: float) -> str:
    """
    Filter hotel options by maximum price per night.

    Args:
        hotels_json: JSON string from search_hotels result
        max_price_per_night: Maximum price per night in USD

    Returns:
        JSON string with filtered hotels within price range

    Example:
        filter_hotels_by_price(hotels_json, 150.00)
    """
    try:
        data = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        if not data.get("success"):
            return hotels_json

        filtered_hotels = []
        for hotel in data.get("hotels", []):
            price = hotel.get("price_per_night")
            # Handle both string and numeric prices
            if isinstance(price, str):
                try:
                    price = float(price.replace("$", "").replace(",", ""))
                except (ValueError, AttributeError):
                    continue
            elif price == "N/A":
                continue

            if price <= max_price_per_night:
                filtered_hotels.append(hotel)

        data["hotels"] = filtered_hotels
        data["hotels_found"] = len(filtered_hotels)
        data["filter_applied"] = f"max_price_per_night <= ${max_price_per_night}"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter hotels by price"}, indent=2
        )


@tool
def filter_hotels_by_rating(hotels_json: str, min_rating: float) -> str:
    """
    Filter hotel options by minimum star rating.

    Args:
        hotels_json: JSON string from search_hotels result
        min_rating: Minimum rating (e.g., 4.0 for 4+ stars)

    Returns:
        JSON string with filtered hotels meeting rating criteria

    Example:
        filter_hotels_by_rating(hotels_json, 4.0)
    """
    try:
        data = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        if not data.get("success"):
            return hotels_json

        filtered_hotels = [hotel for hotel in data.get("hotels", []) if hotel.get("rating", 0) >= min_rating]

        data["hotels"] = filtered_hotels
        data["hotels_found"] = len(filtered_hotels)
        data["filter_applied"] = f"rating >= {min_rating}"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter hotels by rating"}, indent=2
        )


@tool
def filter_hotels_by_amenities(hotels_json: str, required_amenities: str) -> str:
    """
    Filter hotel options by required amenities.

    Args:
        hotels_json: JSON string from search_hotels result
        required_amenities: Comma-separated amenities (e.g., 'Free Wi-Fi,Pool,Gym')

    Returns:
        JSON string with filtered hotels having all required amenities

    Example:
        filter_hotels_by_amenities(hotels_json, 'Free Wi-Fi,Pool')
    """
    try:
        data = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        if not data.get("success"):
            return hotels_json

        # Parse required amenities
        required = [a.strip().lower() for a in required_amenities.split(',')]

        filtered_hotels = []
        for hotel in data.get("hotels", []):
            hotel_amenities = [a.lower() for a in hotel.get("amenities", [])]
            # Check if all required amenities are present
            if all(any(req in amenity for amenity in hotel_amenities) for req in required):
                filtered_hotels.append(hotel)

        data["hotels"] = filtered_hotels
        data["hotels_found"] = len(filtered_hotels)
        data["filter_applied"] = f"required_amenities: {required_amenities}"

        return json.dumps(data, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to filter hotels by amenities"}, indent=2
        )


@tool
def get_best_value_hotel(hotels_json: str) -> str:
    """
    Get the best value hotel based on rating-to-price ratio.

    Args:
        hotels_json: JSON string from search_hotels result

    Returns:
        JSON string with the best value hotel details

    Example:
        get_best_value_hotel(hotels_json)
    """
    try:
        data = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        if not data.get("success") or not data.get("hotels"):
            return json.dumps({"success": False, "message": "No hotels available"}, indent=2)

        # Calculate value score for each hotel (rating / price)
        hotels_with_value = []
        for hotel in data["hotels"]:
            price = hotel.get("price_per_night")
            rating = hotel.get("rating", 0)

            # Handle price conversion
            if isinstance(price, str):
                try:
                    price = float(price.replace("$", "").replace(",", ""))
                except (ValueError, AttributeError):
                    continue
            elif price == "N/A" or price == 0:
                continue

            if rating > 0 and price > 0:
                value_score = rating / (price / 100)  # Normalize price
                hotels_with_value.append({"hotel": hotel, "value_score": round(value_score, 2)})

        if not hotels_with_value:
            return json.dumps(
                {"success": False, "message": "No hotels with valid pricing and ratings"}, indent=2
            )

        # Get hotel with highest value score
        best_value = max(hotels_with_value, key=lambda x: x["value_score"])

        return json.dumps(
            {
                "success": True,
                "best_value_hotel": best_value["hotel"],
                "value_score": best_value["value_score"],
                "explanation": "Value score = rating / (price/100). Higher is better.",
                "total_hotels_compared": len(hotels_with_value),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def get_cheapest_hotel(hotels_json: str) -> str:
    """
    Get the cheapest hotel option from search results.

    Args:
        hotels_json: JSON string from search_hotels result

    Returns:
        JSON string with the cheapest hotel details

    Example:
        get_cheapest_hotel(hotels_json)
    """
    try:
        data = json.loads(hotels_json) if isinstance(hotels_json, str) else hotels_json

        if not data.get("success") or not data.get("hotels"):
            return json.dumps({"success": False, "message": "No hotels available"}, indent=2)

        # Find cheapest hotel
        cheapest = None
        min_price = float('inf')

        for hotel in data["hotels"]:
            price = hotel.get("price_per_night")

            # Handle price conversion
            if isinstance(price, str):
                try:
                    price = float(price.replace("$", "").replace(",", ""))
                except (ValueError, AttributeError):
                    continue
            elif price == "N/A":
                continue

            if price < min_price:
                min_price = price
                cheapest = hotel

        if not cheapest:
            return json.dumps({"success": False, "message": "No hotels with valid pricing"}, indent=2)

        return json.dumps(
            {
                "success": True,
                "cheapest_hotel": cheapest,
                "price_per_night": min_price,
                "total_hotels_compared": len(data["hotels"]),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


# Made with Bob
