"""
Slack Tools - Send notifications and handle approvals via Slack

This module provides tools for:
- Sending interactive approval requests to managers
- Checking approval status
- Notifying users of decisions
- Sending booking confirmations
- Sending trip reminders

Uses Slack SDK for real Slack integration.
"""

import os
import json
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_MANAGER_USER_ID = os.getenv("SLACK_MANAGER_USER_ID")

# Try to import Slack SDK
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False
    print("⚠️  Warning: slack_sdk not installed. Install with: pip install slack-sdk")


@tool
def send_approval_request(
    employee_name: str = "Travel User",
    employee_email: str = "user@company.com",
    itinerary_id: int = 0,
    origin: str = "Unknown",
    destination: str = "Unknown",
    departure_date: str = "TBD",
    return_date: str = "TBD",
    total_cost: float = 0.0,
    compliance_status: str = "pending review",
    flight_summary: str = "Selected flight",
    hotel_summary: str = "Selected hotel",
) -> str:
    """
    Send interactive approval request to manager via Slack.
    ALL PARAMETERS ARE OPTIONAL - defaults will be used if not provided.

    Args:
        employee_name: Name of employee requesting approval (default: "Travel User")
        employee_email: Employee's email address (default: "user@company.com")
        itinerary_id: Database itinerary ID (default: 0)
        origin: Trip origin (default: "Unknown")
        destination: Trip destination (default: "Unknown")
        departure_date: Departure date (default: "TBD")
        return_date: Return date (default: "TBD")
        total_cost: Total trip cost (default: 0.0)
        compliance_status: Policy compliance status (default: "pending review")
        flight_summary: Brief flight details (default: "Selected flight")
        hotel_summary: Brief hotel details (default: "Selected hotel")

    Returns:
        JSON string with message status and timestamp

    Example:
        # Can be called with minimal info:
        send_approval_request(itinerary_id=1, origin="NYC", destination="LAX")
        # Or with full details:
        send_approval_request('John Doe', 'john@example.com', 1, 'JFK', 'LAX', ...)
    """
    try:
        # Check if Slack SDK is available
        if not SLACK_SDK_AVAILABLE:
            return json.dumps(
                {
                    "success": False,
                    "error": "Slack SDK not installed",
                    "message": "Install slack-sdk: pip install slack-sdk",
                },
                indent=2,
            )

        # Check if Slack is configured
        if not SLACK_BOT_TOKEN or SLACK_BOT_TOKEN == "xoxb-your-slack-bot-token-here":
            return json.dumps(
                {
                    "success": False,
                    "error": "Slack not configured",
                    "message": "Set SLACK_BOT_TOKEN and SLACK_MANAGER_USER_ID in .env file",
                },
                indent=2,
            )

        if not SLACK_MANAGER_USER_ID:
            return json.dumps(
                {
                    "success": False,
                    "error": "Manager user ID not configured",
                    "message": "Set SLACK_MANAGER_USER_ID in .env file",
                },
                indent=2,
            )

        # Build Slack message blocks
        message_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🧳 Travel Request from {employee_name}"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Employee:*\n{employee_name}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{employee_email}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Route:*\n{origin} → {destination}"},
                    {"type": "mrkdwn", "text": f"*Dates:*\n{departure_date} to {return_date}"},
                ],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Flight:*\n{flight_summary}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Hotel:*\n{hotel_summary}"}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Cost:*\n${total_cost:.2f}"},
                    {"type": "mrkdwn", "text": f"*Policy Status:*\n{compliance_status}"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve"},
                        "style": "primary",
                        "value": f"approve_{itinerary_id}",
                        "action_id": "approve_trip",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "value": f"reject_{itinerary_id}",
                        "action_id": "reject_trip",
                    },
                ],
            },
        ]

        # Send message via Slack SDK
        try:
            client = WebClient(token=SLACK_BOT_TOKEN)

            response = client.chat_postMessage(
                channel=SLACK_MANAGER_USER_ID,
                text=f"Travel approval request from {employee_name}",
                blocks=message_blocks,
            )

            return json.dumps(
                {
                    "success": True,
                    "message": "Approval request sent to manager via Slack",
                    "manager_id": SLACK_MANAGER_USER_ID,
                    "itinerary_id": itinerary_id,
                    "timestamp": response.get("ts"),
                    "channel": response.get("channel"),
                    "slack_response": {"ok": response.get("ok"), "message_ts": response.get("ts")},
                },
                indent=2,
            )

        except SlackApiError as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Slack API error: {e.response['error']}",
                    "message": "Failed to send Slack message",
                    "details": str(e),
                },
                indent=2,
            )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to send approval request"}, indent=2
        )


@tool
def check_approval_status(itinerary_id: int, message_timestamp: str) -> str:
    """
    Check if manager has responded to approval request.

    Args:
        itinerary_id: Itinerary ID
        message_timestamp: Timestamp of the approval request message

    Returns:
        JSON string with approval status

    Example:
        check_approval_status(1, '2026-03-22T10:00:00')
    """
    try:
        # Mock implementation
        # In production, check Slack message reactions or button clicks

        return json.dumps(
            {
                "success": True,
                "mock_mode": True,
                "itinerary_id": itinerary_id,
                "status": "pending",
                "message": "Awaiting manager response",
                "checked_at": datetime.now().isoformat(),
                "note": "In production, query Slack API for button clicks or reactions",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to check approval status"}, indent=2
        )


@tool
def send_approval_notification(
    employee_slack_id: str,
    employee_name: str,
    itinerary_id: int,
    approval_status: str,
    manager_name: str,
    manager_comments: Optional[str] = None,
    trip_summary: Optional[str] = None,
) -> str:
    """
    Notify employee of manager's approval decision via Slack.

    Args:
        employee_slack_id: Employee's Slack user ID
        employee_name: Employee's name
        itinerary_id: Itinerary ID
        approval_status: "approved" or "rejected"
        manager_name: Manager's name
        manager_comments: Optional comments from manager
        trip_summary: Optional trip summary

    Returns:
        JSON string with notification status

    Example:
        send_approval_notification('U123', 'John Doe', 1, 'approved', 'Jane Manager')
    """
    try:
        status_emoji = "✅" if approval_status == "approved" else "❌"
        status_text = "approved" if approval_status == "approved" else "rejected"

        # Build notification message
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} Travel Request {status_text.title()}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi {employee_name},\n\nYour travel request (ID: {itinerary_id}) has been *{status_text}* by {manager_name}.",
                },
            },
        ]

        if trip_summary:
            message_blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Trip Details:*\n{trip_summary}"}}
            )

        if manager_comments:
            message_blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Manager Comments:*\n_{manager_comments}_"},
                }
            )

        if approval_status == "approved":
            message_blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "✈️ You can now proceed with booking your trip!"},
                }
            )
        else:
            message_blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Please revise your travel plans and resubmit."},
                }
            )

        # Mock response
        return json.dumps(
            {
                "success": True,
                "mock_mode": True,
                "message": f"Notification sent: Trip {status_text}",
                "employee_id": employee_slack_id,
                "itinerary_id": itinerary_id,
                "approval_status": approval_status,
                "timestamp": datetime.now().isoformat(),
                "message_blocks": message_blocks,
                "note": "In production, use Slack SDK to send this message",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to send approval notification"}, indent=2
        )


@tool
def send_booking_confirmation(
    employee_slack_id: str,
    employee_name: str,
    itinerary_id: int,
    trip_details: str,
    booking_reference: Optional[str] = None,
) -> str:
    """
    Send booking confirmation to employee via Slack.

    Args:
        employee_slack_id: Employee's Slack user ID
        employee_name: Employee's name
        itinerary_id: Itinerary ID
        trip_details: Trip details summary
        booking_reference: Optional booking reference number

    Returns:
        JSON string with confirmation status

    Example:
        send_booking_confirmation('U123', 'John Doe', 1, 'JFK to LAX...', 'BK123456')
    """
    try:
        message_blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "✈️ Booking Confirmed!"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi {employee_name},\n\nYour travel booking has been confirmed!",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Trip Details:*\n{trip_details}"}},
        ]

        if booking_reference:
            message_blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Booking Reference:* `{booking_reference}`"},
                }
            )

        message_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📧 Confirmation details have been sent to your email.\n🎒 Don't forget to check the weather and pack accordingly!",
                },
            }
        )

        return json.dumps(
            {
                "success": True,
                "mock_mode": True,
                "message": "Booking confirmation sent",
                "employee_id": employee_slack_id,
                "itinerary_id": itinerary_id,
                "booking_reference": booking_reference,
                "timestamp": datetime.now().isoformat(),
                "message_blocks": message_blocks,
                "note": "In production, use Slack SDK to send this message",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to send booking confirmation"}, indent=2
        )


@tool
def send_trip_reminder(
    employee_slack_id: str, employee_name: str, trip_details: str, days_until_trip: int
) -> str:
    """
    Send trip reminder to employee via Slack.

    Args:
        employee_slack_id: Employee's Slack user ID
        employee_name: Employee's name
        trip_details: Trip details summary
        days_until_trip: Number of days until trip

    Returns:
        JSON string with reminder status

    Example:
        send_trip_reminder('U123', 'John Doe', 'JFK to LAX...', 3)
    """
    try:
        if days_until_trip == 1:
            reminder_text = "🚨 Your trip is *tomorrow*!"
        elif days_until_trip <= 3:
            reminder_text = f"⏰ Your trip is in *{days_until_trip} days*!"
        else:
            reminder_text = f"📅 Reminder: Your trip is in {days_until_trip} days"

        message_blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "✈️ Trip Reminder"}},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hi {employee_name},\n\n{reminder_text}"},
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Trip Details:*\n{trip_details}"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Pre-Trip Checklist:*\n✓ Check weather forecast\n✓ Pack essentials\n✓ Confirm booking details\n✓ Check-in online (24hrs before)\n✓ Arrange transportation to airport",
                },
            },
        ]

        return json.dumps(
            {
                "success": True,
                "mock_mode": True,
                "message": "Trip reminder sent",
                "employee_id": employee_slack_id,
                "days_until_trip": days_until_trip,
                "timestamp": datetime.now().isoformat(),
                "message_blocks": message_blocks,
                "note": "In production, use Slack SDK to send this message",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to send trip reminder"}, indent=2
        )


# Made with Bob
