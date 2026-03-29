"""Test API connections for Travel Agent MVP"""

import os
from dotenv import load_dotenv
import requests
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()


def test_serpapi():
    """Test SerpAPI connection"""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key or api_key == "your_serpapi_key_here":
        print("❌ SERPAPI_API_KEY not configured in .env")
        return False

    try:
        # Simple test search
        params = {"engine": "google", "q": "test", "api_key": api_key}
        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            print(f"❌ SerpAPI error: {results['error']}")
            return False

        print("✅ SerpAPI connection successful")
        return True
    except Exception as e:
        print(f"❌ SerpAPI connection failed: {e}")
        return False


def test_openweather():
    """Test OpenWeatherMap connection"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key or api_key == "your_openweather_key_here":
        print("❌ OPENWEATHER_API_KEY not configured in .env")
        return False

    try:
        # Test with Current Weather API 2.5 (Free tier)
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": "London,GB", "appid": api_key, "units": "metric"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 401:
            print("❌ OpenWeatherMap: Invalid API key")
            print("   Note: New keys may take 10-15 minutes to activate")
            return False
        elif response.status_code == 429:
            print("❌ OpenWeatherMap: Rate limit exceeded")
            print("   Free tier: 1000 calls/day")
            return False

        response.raise_for_status()
        data = response.json()

        if "main" in data and "temp" in data["main"]:
            print("✅ OpenWeatherMap connection successful")
            print(
                f"   Test location: {data.get('name', 'Unknown')}, {data.get('sys', {}).get('country', '')}"
            )
            print(f"   Temperature: {data['main']['temp']}°C")
            return True
        else:
            print("❌ OpenWeatherMap: Unexpected response format")
            return False

    except requests.exceptions.Timeout:
        print("❌ OpenWeatherMap connection timeout")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenWeatherMap connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ OpenWeatherMap error: {e}")
        return False


def test_llm_api_key():
    """Test LLM API key configuration (basic validation)"""
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if groq_key and groq_key != "gsk-your-groq-api-key":
        if groq_key.startswith("gsk-"):
            print("✅ Groq API key format valid")
            return True
        else:
            print("⚠️  Groq API key format may be invalid (should start with 'gsk-')")
            return False
    elif openai_key and openai_key != "sk-your-openai-api-key":
        if openai_key.startswith("sk-"):
            print("✅ OpenAI API key format valid")
            return True
        else:
            print("⚠️  OpenAI API key format may be invalid (should start with 'sk-')")
            return False
    else:
        print("⚠️  No LLM API key configured (Groq or OpenAI)")
        print("   Note: This is optional if you already have CUGA configured")
        return True  # Don't fail if LLM key is not set


def main():
    """Run all API connection tests"""
    print("\n" + "=" * 60)
    print("🔍 Testing API Connections for Travel Agent MVP")
    print("=" * 60 + "\n")

    results = {
        "SerpAPI": test_serpapi(),
        "OpenWeatherMap": test_openweather(),
        "LLM API Key": test_llm_api_key(),
    }

    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)

    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        status_text = "Connected" if status else "Failed"
        print(f"{status_icon} {service:20s}: {status_text}")

    all_passed = all(results.values())

    print("=" * 60)
    if all_passed:
        print("\n🎉 All API connections successful!")
        print("✅ Ready to proceed with Phase 2: Agent Tool Implementation\n")
    else:
        print("\n⚠️  Some API connections failed.")
        print("Please check your .env file and API keys.\n")
        print("Required API keys:")
        print("  - SERPAPI_API_KEY: https://serpapi.com/")
        print("  - OPENWEATHER_API_KEY: https://openweathermap.org/api")
        print("  - GROQ_API_KEY or OPENAI_API_KEY (optional if CUGA configured)\n")

    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

# Made with Bob
