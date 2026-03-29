"""
Weather Agent Tools - Get weather forecasts using OpenWeatherMap API

This module provides tools for:
- Getting weather forecasts for travel dates
- Getting current weather conditions
- Generating packing suggestions based on weather
"""

import os
import json
from datetime import datetime
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


@tool
def get_weather_forecast(location: str, start_date: str, end_date: str) -> str:
    """
    Get weather forecast for a location during travel dates.

    Args:
        location: City name (e.g., 'Los Angeles', 'New York', 'London')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        JSON string with weather forecast including temperature, conditions, and precipitation

    Example:
        get_weather_forecast('Los Angeles', '2026-04-15', '2026-04-20')
    """
    try:
        # Validate inputs
        if not location:
            return json.dumps({"success": False, "error": "Location is required"})

        if not start_date or not end_date:
            return json.dumps({"success": False, "error": "Start and end dates are required"})

        # First, get coordinates for the location
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {"q": location, "limit": 1, "appid": OPENWEATHER_API_KEY}

        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            return json.dumps({"success": False, "error": f"Location '{location}' not found"})

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        location_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")

        # Get 5-day forecast (free tier)
        forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "imperial",  # Fahrenheit
        }

        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Extract relevant forecast data
        daily_forecasts = {}
        for item in forecast_data.get("list", []):
            forecast_time = datetime.fromtimestamp(item["dt"])
            forecast_date = forecast_time.date()

            # Only include forecasts within travel dates
            if start.date() <= forecast_date <= end.date():
                date_str = forecast_date.strftime("%Y-%m-%d")

                if date_str not in daily_forecasts:
                    daily_forecasts[date_str] = {
                        "date": date_str,
                        "temps": [],
                        "conditions": [],
                        "descriptions": [],
                        "humidity": [],
                        "wind_speed": [],
                        "precipitation_prob": [],
                    }

                daily_forecasts[date_str]["temps"].append(item["main"]["temp"])
                daily_forecasts[date_str]["conditions"].append(item["weather"][0]["main"])
                daily_forecasts[date_str]["descriptions"].append(item["weather"][0]["description"])
                daily_forecasts[date_str]["humidity"].append(item["main"]["humidity"])
                daily_forecasts[date_str]["wind_speed"].append(item["wind"]["speed"])
                daily_forecasts[date_str]["precipitation_prob"].append(item.get("pop", 0) * 100)

        # Aggregate daily data
        daily_summary = []
        for date_str, data in sorted(daily_forecasts.items()):
            summary = {
                "date": date_str,
                "temp_high": round(max(data["temps"]), 1),
                "temp_low": round(min(data["temps"]), 1),
                "temp_avg": round(sum(data["temps"]) / len(data["temps"]), 1),
                "condition": max(set(data["conditions"]), key=data["conditions"].count),
                "description": max(set(data["descriptions"]), key=data["descriptions"].count),
                "humidity_avg": round(sum(data["humidity"]) / len(data["humidity"]), 1),
                "wind_speed_avg": round(sum(data["wind_speed"]) / len(data["wind_speed"]), 1),
                "precipitation_chance": round(max(data["precipitation_prob"]), 1),
            }
            daily_summary.append(summary)

        # Overall trip summary
        all_temps = [temp for day in daily_forecasts.values() for temp in day["temps"]]
        all_conditions = [cond for day in daily_forecasts.values() for cond in day["conditions"]]

        trip_summary = {
            "temp_range": f"{round(min(all_temps), 1)}°F - {round(max(all_temps), 1)}°F",
            "avg_temp": round(sum(all_temps) / len(all_temps), 1),
            "most_common_condition": max(set(all_conditions), key=all_conditions.count),
            "rainy_days": sum(1 for day in daily_summary if day["precipitation_chance"] > 50),
        }

        return json.dumps(
            {
                "success": True,
                "location": f"{location_name}, {country}",
                "coordinates": {"lat": lat, "lon": lon},
                "start_date": start_date,
                "end_date": end_date,
                "trip_summary": trip_summary,
                "daily_forecast": daily_summary,
                "forecast_days": len(daily_summary),
            },
            indent=2,
        )

    except requests.exceptions.RequestException as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "message": "Failed to fetch weather forecast. Please check your API key and connection.",
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to process weather forecast"}, indent=2
        )


@tool
def get_current_weather(location: str) -> str:
    """
    Get current weather conditions for a location.

    Args:
        location: City name (e.g., 'Los Angeles', 'New York', 'London')

    Returns:
        JSON string with current weather conditions

    Example:
        get_current_weather('Los Angeles')
    """
    try:
        # Validate input
        if not location:
            return json.dumps({"success": False, "error": "Location is required"})

        # Get current weather
        weather_url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "imperial",  # Fahrenheit
        }

        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current_weather = {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "temp_min": round(data["main"]["temp_min"], 1),
            "temp_max": round(data["main"]["temp_max"], 1),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "wind_direction": data["wind"].get("deg", 0),
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility", 0),
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
            "timestamp": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
        }

        return json.dumps({"success": True, "current_weather": current_weather}, indent=2)

    except requests.exceptions.RequestException as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to fetch current weather"}, indent=2
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


@tool
def get_packing_suggestions(weather_forecast_json: str) -> str:
    """
    Generate packing suggestions based on weather forecast.

    Args:
        weather_forecast_json: JSON string from get_weather_forecast result

    Returns:
        JSON string with packing suggestions categorized by type

    Example:
        get_packing_suggestions(forecast_json)
    """
    try:
        data = (
            json.loads(weather_forecast_json)
            if isinstance(weather_forecast_json, str)
            else weather_forecast_json
        )

        if not data.get("success"):
            return weather_forecast_json

        trip_summary = data.get("trip_summary", {})
        daily_forecast = data.get("daily_forecast", [])

        # Extract weather patterns
        avg_temp = trip_summary.get("avg_temp", 70)
        rainy_days = trip_summary.get("rainy_days", 0)
        most_common_condition = trip_summary.get("most_common_condition", "Clear")

        # Temperature-based suggestions
        clothing = []
        if avg_temp < 40:
            clothing.extend(["Heavy winter coat", "Thermal underwear", "Warm gloves", "Winter hat", "Scarf"])
        elif avg_temp < 60:
            clothing.extend(["Light jacket or sweater", "Long pants", "Closed-toe shoes", "Light scarf"])
        elif avg_temp < 75:
            clothing.extend(["Light layers", "Mix of short and long sleeves", "Comfortable walking shoes"])
        else:
            clothing.extend(
                ["Light, breathable clothing", "Shorts and t-shirts", "Sandals", "Sun hat", "Sunglasses"]
            )

        # Weather condition-based suggestions
        accessories = ["Phone charger", "Travel adapter", "Reusable water bottle"]

        if rainy_days > 0:
            accessories.extend(["Umbrella", "Rain jacket or poncho", "Waterproof bag"])

        if most_common_condition in ["Clear", "Clouds"] and avg_temp > 65:
            accessories.extend(["Sunscreen (SPF 30+)", "Sunglasses", "Sun hat"])

        if any(day.get("wind_speed_avg", 0) > 15 for day in daily_forecast):
            accessories.append("Windbreaker")

        # General travel essentials
        essentials = [
            "Passport/ID",
            "Travel documents",
            "Medications",
            "Toiletries",
            "First aid kit",
            "Snacks for travel",
        ]

        # Activity-based suggestions
        activities = []
        if avg_temp > 70 and rainy_days == 0:
            activities.append("Great weather for outdoor activities!")
        elif rainy_days > len(daily_forecast) / 2:
            activities.append("Consider indoor activities - frequent rain expected")

        return json.dumps(
            {
                "success": True,
                "location": data.get("location"),
                "travel_dates": f"{data.get('start_date')} to {data.get('end_date')}",
                "weather_summary": {
                    "avg_temperature": f"{avg_temp}°F",
                    "rainy_days": rainy_days,
                    "primary_condition": most_common_condition,
                },
                "packing_list": {"clothing": clothing, "accessories": accessories, "essentials": essentials},
                "activity_suggestions": activities,
                "tips": [
                    "Check weather updates closer to departure date",
                    "Pack layers for temperature changes",
                    "Bring a small day bag for excursions",
                ],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to generate packing suggestions"}, indent=2
        )


# Made with Bob
