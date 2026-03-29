"""
Slack Interactive Components Handler

This module handles Slack interactive component events (button clicks)
for the travel approval workflow.

To use:
1. Set up a Slack app with Interactive Components enabled
2. Set the Request URL to point to this handler endpoint
3. Run this as a Flask/FastAPI server to receive Slack events
"""

import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Import database tools
try:
    from docs.examples.travel_agent.agents.database_tools import update_approval_status, initialize_database
except ImportError:
    # Fallback for direct execution
    from database_tools import update_approval_status, initialize_database

load_dotenv()

# Initialize database on startup
print("🔧 Initializing database...")
init_result = initialize_database.invoke({})
print(f"   {init_result}")

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

# Initialize Slack client
slack_client = WebClient(token=SLACK_BOT_TOKEN)


@app.route("/", methods=["GET", "POST"])
def health_check():
    """Health check endpoint - also handles Slack interactive events at root"""
    # If it's a POST request with Slack payload, handle it
    if request.method == "POST":
        print("\n🔔 Received POST to root endpoint - forwarding to interactive handler")
        return handle_interactive()

    # GET request - return health check
    return jsonify(
        {
            "status": "ok",
            "service": "Travel Agent Slack Handler",
            "endpoints": {"interactive": "/slack/interactive (POST) or / (POST)", "health": "/ (GET)"},
        }
    )


@app.route("/slack/interactive", methods=["GET", "POST"])
def handle_interactive():
    """
    Handle Slack interactive component events (button clicks).

    This endpoint receives events when managers click Approve/Reject buttons.
    Also handles GET requests for Slack URL verification.
    """
    print(f"\n🔔 Received {request.method} request to /slack/interactive")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Content-Type: {request.content_type}")

    # Handle GET request (Slack URL verification)
    if request.method == "GET":
        print("   ✅ Responding to GET request (URL verification)")
        return jsonify(
            {
                "status": "ok",
                "message": "Slack interactive endpoint is ready",
                "note": "This endpoint accepts POST requests with Slack interactive payloads",
            }
        )

    # Handle POST request (actual button clicks)
    print("   📨 Processing POST request (button click)")
    try:
        # Parse the payload
        payload_str = request.form.get("payload")
        if not payload_str:
            print("   ❌ No payload found in request")
            return jsonify({"text": "❌ No payload found"}), 400

        print(f"   📦 Payload received (length: {len(payload_str)})")
        payload = json.loads(payload_str)
        print("   ✅ Payload parsed successfully")

        # Verify it's from Slack (in production, verify signature)
        # For now, we'll skip signature verification for simplicity

        # Extract action information
        print("   📋 Extracting action information...")
        action = payload.get("actions", [{}])[0]
        action_id = action.get("action_id")
        action_value = action.get("value")
        print(f"   Action ID: {action_id}, Value: {action_value}")

        user = payload.get("user", {})
        manager_id = user.get("id")
        manager_name = user.get("name", "Manager")
        print(f"   Manager: {manager_name} (ID: {manager_id})")

        # Extract message information for updating
        message = payload.get("message", {})
        message_ts = message.get("ts")
        channel_id = payload.get("channel", {}).get("id")
        print(f"   Message TS: {message_ts}, Channel: {channel_id}")

        # Parse the action value (format: "approve_123" or "reject_123")
        if "_" in action_value:
            action_type, itinerary_id_str = action_value.split("_", 1)

            # Handle case where itinerary_id_str might be JSON (from old messages)
            if itinerary_id_str.strip().startswith("{"):
                print("   ⚠️ Received JSON instead of ID, parsing...")
                try:
                    result_json = json.loads(itinerary_id_str)
                    itinerary_id = result_json.get("itinerary_id")
                    print(f"   ✅ Extracted ID from JSON: {itinerary_id}")
                except json.JSONDecodeError:
                    print(f"   ❌ Failed to parse JSON: {itinerary_id_str}")
                    return jsonify({"text": "❌ Invalid itinerary ID format"}), 400
            else:
                # Normal case: just a number
                itinerary_id = int(itinerary_id_str)

            print(f"   Itinerary ID: {itinerary_id}")
        else:
            print(f"   ❌ Invalid action format: {action_value}")
            return jsonify({"text": "❌ Invalid action format"}), 400

        # Determine approval status
        if action_id == "approve_trip":
            approval_status = "approved"
            message = f"✅ Trip approved by {manager_name}"
            emoji = "✅"
        elif action_id == "reject_trip":
            approval_status = "rejected"
            message = f"❌ Trip rejected by {manager_name}"
            emoji = "❌"
        else:
            print(f"   ❌ Unknown action ID: {action_id}")
            return jsonify({"text": "❌ Unknown action"}), 400

        print(f"   Decision: {approval_status}")

        # Update database
        print("   💾 Updating database...")
        # Use invoke with proper input dict
        result = update_approval_status.invoke(
            {
                "itinerary_id": itinerary_id,
                "approval_status": approval_status,
                "manager_id": manager_id,
                "manager_comments": f"Decision made via Slack by {manager_name}",
            }
        )

        print("   ✅ Database update result received")
        result_data = json.loads(result)
        print(f"   Result success: {result_data.get('success')}")

        if not result_data.get("success"):
            error_msg = result_data.get('error', 'Unknown error')
            print(f"   ❌ Database update failed: {error_msg}")
            return jsonify({"text": f"❌ Error updating approval: {error_msg}"}), 500

        print("   🎉 Approval processed successfully!")

        # TODO: Send notification back to user's chat
        # For now, we'll log it. In production, this would:
        # 1. Look up user's session/chat ID from database
        # 2. Send a message to their active chat session
        # 3. Or send them a Slack DM if they're on Slack
        print(f"   📢 User notification: Trip {itinerary_id} was {approval_status} by {manager_name}")
        print("   💡 In production: Send this to user's chat or Slack DM")

        # Update the Slack message using the Web API
        try:
            updated_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Travel Request {approval_status.title()}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Status:* {message}\n*Itinerary ID:* {itinerary_id}\n*Timestamp:* {result_data.get('updated_at', 'N/A')}",
                    },
                },
                {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Decided by <@{manager_id}>"}]},
            ]

            # Update the message in Slack
            print("   📝 Updating Slack message...")
            slack_client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=f"Travel request {approval_status}",
                blocks=updated_blocks,
            )
            print("   ✅ Slack message updated successfully!")

            # Return success response (Slack expects a 200 OK)
            return jsonify({"ok": True}), 200

        except SlackApiError as e:
            print(f"   ❌ Failed to update Slack message: {e.response['error']}")
            # Still return 200 to Slack to avoid retries
            return jsonify({"ok": True}), 200

    except Exception as e:
        print(f"\n❌ Error handling Slack interaction: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"text": f"❌ Error: {str(e)}"}), 500


if __name__ == "__main__":
    # Allow port to be configured via environment variable
    port = int(os.getenv("SLACK_HANDLER_PORT", "3001"))

    print("🚀 Starting Slack Interactive Components Handler")
    print(f"📍 Endpoint: http://localhost:{port}/slack/interactive")
    print("💡 Configure this URL in your Slack app's Interactive Components settings")
    print("\n⚠️  Note: For production, use a proper web server (gunicorn, uvicorn) and HTTPS")
    print("⚠️  You may need ngrok or similar to expose localhost to Slack\n")

    app.run(host="0.0.0.0", port=port, debug=True)

# Made with Bob
