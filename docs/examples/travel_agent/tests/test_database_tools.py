"""Test Database Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.database_tools import (
    initialize_database,
    save_itinerary,
    get_itinerary,
    update_approval_status,
    query_itineraries,
    get_pending_approvals,
)


def test_initialize_database():
    """Test database initialization"""
    print("\n🧪 Testing initialize_database...")
    result = initialize_database.invoke({})
    print(result)
    assert "success" in result
    print("✅ initialize_database test passed")


def test_save_and_retrieve():
    """Test saving and retrieving itinerary"""
    print("\n🧪 Testing save_itinerary and get_itinerary...")

    # Save itinerary
    save_result = save_itinerary.invoke(
        {
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "user_role": "employee",
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "flight_details": '{"airline": "United", "price": 350}',
            "hotel_details": '{"name": "Hilton", "price": 150}',
            "weather_info": '{"temp": 75}',
            "expense_report": '{"total": 1850}',
            "compliance_status": "compliant",
            "total_cost": 1850.00,
            "manager_id": "manager@example.com",
        }
    )
    print(save_result[:300] + "..." if len(save_result) > 300 else save_result)
    assert "itinerary_id" in save_result

    # Extract itinerary ID
    import json

    save_data = json.loads(save_result)
    itinerary_id = save_data["itinerary_id"]

    # Retrieve itinerary
    get_result = get_itinerary.invoke({"itinerary_id": itinerary_id})
    print(get_result[:300] + "..." if len(get_result) > 300 else get_result)
    assert "itinerary" in get_result
    print("✅ save_itinerary and get_itinerary tests passed")

    return itinerary_id


def test_update_approval():
    """Test updating approval status"""
    print("\n🧪 Testing update_approval_status...")

    # First save an itinerary
    itinerary_id = test_save_and_retrieve()

    # Update approval
    result = update_approval_status.invoke(
        {
            "itinerary_id": itinerary_id,
            "approval_status": "approved",
            "manager_id": "manager@example.com",
            "manager_comments": "Approved - looks good",
        }
    )
    print(result)
    assert "success" in result
    print("✅ update_approval_status test passed")


def test_query_itineraries():
    """Test querying itineraries"""
    print("\n🧪 Testing query_itineraries...")

    result = query_itineraries.invoke({"user_email": "john@example.com", "limit": 5})
    print(result[:300] + "..." if len(result) > 300 else result)
    assert "itineraries" in result
    print("✅ query_itineraries test passed")


def test_pending_approvals():
    """Test getting pending approvals"""
    print("\n🧪 Testing get_pending_approvals...")

    result = get_pending_approvals.invoke({})
    print(result[:300] + "..." if len(result) > 300 else result)
    assert "pending_count" in result
    print("✅ get_pending_approvals test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Database Tools")
    print("=" * 60)

    try:
        test_initialize_database()
        test_save_and_retrieve()
        test_update_approval()
        test_query_itineraries()
        test_pending_approvals()

        print("\n" + "=" * 60)
        print("✅ All Database tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
