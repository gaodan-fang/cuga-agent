"""
Demo: Interactive Approval Workflow

This script demonstrates how the Travel Agent waits for manager approval
and continues the conversation automatically when approved.

For demo purposes, this script simulates a manager approval after a delay.
"""

import sys

sys.path.append('.')

import time
import json
import threading
from docs.examples.travel_agent.agents.database_tools import (
    initialize_database,
    save_itinerary,
    update_approval_status,
    wait_for_approval,
)


def simulate_manager_approval(itinerary_id: int, delay_seconds: int = 10):
    """
    Simulate a manager approving the itinerary after a delay.
    In production, this would happen via Slack when the manager clicks "Approve".
    """
    print(f"\n[DEMO] Manager will approve itinerary #{itinerary_id} in {delay_seconds} seconds...")
    time.sleep(delay_seconds)

    # Simulate manager approval
    result = update_approval_status.invoke(
        {
            "itinerary_id": itinerary_id,
            "approval_status": "approved",
            "manager_id": "demo_manager@company.com",
            "manager_comments": "Looks good! Approved for business travel.",
        }
    )

    print("\n[DEMO] ✅ Manager approved the itinerary!")
    return result


def demo_approval_workflow():
    """Demonstrate the interactive approval workflow"""

    print("\n" + "=" * 70)
    print("🎬 DEMO: Interactive Approval Workflow")
    print("=" * 70)

    # Step 1: Initialize database
    print("\n1️⃣ Initializing database...")
    initialize_database.invoke({})
    print("   ✅ Database ready")

    # Step 2: Create a sample itinerary
    print("\n2️⃣ Creating sample itinerary...")
    itinerary_data = {
        "user_id": "john.doe@company.com",
        "user_role": "employee",
        "origin": "New York",
        "destination": "Los Angeles",
        "departure_date": "2026-04-15",
        "return_date": "2026-04-20",
        "flight_details": json.dumps(
            {"airline": "United Airlines", "flight_number": "UA123", "price": 450.00}
        ),
        "hotel_details": json.dumps({"name": "Downtown Hotel", "rate_per_night": 140.00, "nights": 5}),
        "total_cost": 1150.00,
        "trip_purpose": "Client meeting",
    }

    result = save_itinerary.invoke(itinerary_data)
    result_data = json.loads(result)

    if not result_data["success"]:
        print(f"   ❌ Failed to save itinerary: {result_data.get('error')}")
        return

    itinerary_id = result_data["itinerary_id"]
    print(f"   ✅ Itinerary saved with ID: {itinerary_id}")
    print("   📧 Approval request sent to manager")

    # Step 3: Start background thread to simulate manager approval
    print("\n3️⃣ Starting approval workflow...")
    print("   💡 In production, manager would approve via Slack")
    print("   💡 For this demo, we'll simulate approval after 10 seconds")

    approval_thread = threading.Thread(target=simulate_manager_approval, args=(itinerary_id, 10))
    approval_thread.daemon = True
    approval_thread.start()

    # Step 4: Wait for approval (this is what the Travel Agent does)
    print("\n4️⃣ Travel Agent waiting for approval...")
    print("   ⏳ This simulates the agent waiting in the conversation...")
    print("   💬 User sees: 'Waiting for manager approval...'")

    approval_result = wait_for_approval.invoke(
        {"itinerary_id": itinerary_id, "timeout_seconds": 60, "check_interval": 2}
    )

    approval_data = json.loads(approval_result)

    # Step 5: Handle approval result
    print("\n5️⃣ Approval received!")
    print("=" * 70)

    if approval_data["status"] == "approved":
        print("\n🎉 SUCCESS! The conversation continues automatically:")
        print("\n   Travel Agent: 'Great news! Your manager has approved your trip!'")
        print("   Travel Agent: 'Manager's comment: " + approval_data.get("manager_comments", "") + "'")
        print("   Travel Agent: 'Would you like me to proceed with booking?'")
        print("\n   💬 The user can now continue the conversation naturally")

    elif approval_data["status"] == "rejected":
        print("\n❌ Trip was rejected:")
        print("\n   Travel Agent: 'I'm sorry, but your manager has rejected this itinerary.'")
        print(f"   Travel Agent: 'Reason: {approval_data.get('manager_comments', 'No reason provided')}'")
        print("   Travel Agent: 'Would you like me to help you create a new itinerary?'")

    elif approval_data["status"] == "timeout":
        print("\n⏱️  Approval timeout:")
        print("\n   Travel Agent: 'I haven't received a response from your manager yet.'")
        print("   Travel Agent: 'The request is still pending. I'll notify you when they respond.'")
        print("   Travel Agent: 'You can also check with them directly if needed.'")

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\n💡 Key Points:")
    print("   1. The Travel Agent WAITS for approval (doesn't end the conversation)")
    print("   2. When manager approves via Slack, the conversation CONTINUES automatically")
    print("   3. User experiences a seamless, interactive workflow")
    print("   4. No need to start a new conversation or check status manually")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        demo_approval_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

# Made with Bob
