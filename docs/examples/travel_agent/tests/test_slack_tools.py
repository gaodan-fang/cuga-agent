"""Test Slack Tools"""

import sys

sys.path.append('.')

from docs.examples.travel_agent.agents.slack_tools import (
    send_approval_request,
    check_approval_status,
    send_approval_notification,
    send_booking_confirmation,
    send_trip_reminder,
)


def test_send_approval_request():
    """Test sending approval request"""
    print("\n🧪 Testing send_approval_request...")
    result = send_approval_request.invoke(
        {
            "employee_name": "John Doe",
            "employee_email": "john@example.com",
            "itinerary_id": 1,
            "origin": "JFK",
            "destination": "LAX",
            "departure_date": "2026-04-15",
            "return_date": "2026-04-20",
            "total_cost": 1850.00,
            "compliance_status": "compliant",
            "flight_summary": "United Airlines, $350, Economy",
            "hotel_summary": "Hilton Downtown, $150/night",
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ send_approval_request test passed")


def test_check_approval_status():
    """Test checking approval status"""
    print("\n🧪 Testing check_approval_status...")
    result = check_approval_status.invoke({"itinerary_id": 1, "message_timestamp": "2026-03-22T10:00:00"})
    print(result)
    assert "status" in result
    print("✅ check_approval_status test passed")


def test_send_approval_notification():
    """Test sending approval notification"""
    print("\n🧪 Testing send_approval_notification...")
    result = send_approval_notification.invoke(
        {
            "employee_slack_id": "U123456",
            "employee_name": "John Doe",
            "itinerary_id": 1,
            "approval_status": "approved",
            "manager_name": "Jane Manager",
            "manager_comments": "Approved - have a great trip!",
            "trip_summary": "JFK to LAX, Apr 15-20, 2026",
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ send_approval_notification test passed")


def test_send_booking_confirmation():
    """Test sending booking confirmation"""
    print("\n🧪 Testing send_booking_confirmation...")
    result = send_booking_confirmation.invoke(
        {
            "employee_slack_id": "U123456",
            "employee_name": "John Doe",
            "itinerary_id": 1,
            "trip_details": "JFK to LAX, Apr 15-20, 2026\nUnited Airlines\nHilton Downtown",
            "booking_reference": "BK123456",
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ send_booking_confirmation test passed")


def test_send_trip_reminder():
    """Test sending trip reminder"""
    print("\n🧪 Testing send_trip_reminder...")
    result = send_trip_reminder.invoke(
        {
            "employee_slack_id": "U123456",
            "employee_name": "John Doe",
            "trip_details": "JFK to LAX, Apr 15-20, 2026",
            "days_until_trip": 3,
        }
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    assert "success" in result
    print("✅ send_trip_reminder test passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Slack Tools")
    print("=" * 60)
    print("\nNote: These tests use mock mode since Slack is not configured")
    print("In production, configure SLACK_BOT_TOKEN for real Slack integration\n")

    try:
        test_send_approval_request()
        test_check_approval_status()
        test_send_approval_notification()
        test_send_booking_confirmation()
        test_send_trip_reminder()

        print("\n" + "=" * 60)
        print("✅ All Slack Tools tests passed!")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback

        traceback.print_exc()

# Made with Bob
