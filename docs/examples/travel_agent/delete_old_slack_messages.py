"""
Delete old Slack approval messages

This script deletes messages sent by the bot in a specific channel.
Useful for cleaning up test messages.
"""

import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_MANAGER_USER_ID = os.getenv("SLACK_MANAGER_USER_ID")


def delete_bot_messages(channel_id, limit=100):
    """
    Delete bot messages from a channel.

    Args:
        channel_id: Channel or DM ID
        limit: Maximum number of messages to check (default 100)
    """
    if not SLACK_BOT_TOKEN:
        print("❌ Error: SLACK_BOT_TOKEN not set in .env file")
        return

    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        # Get bot's own user ID
        auth_response = client.auth_test()
        bot_user_id = auth_response["user_id"]
        print(f"🤖 Bot User ID: {bot_user_id}")
        print(f"📍 Channel ID: {channel_id}")
        print("🔍 Fetching messages...\n")

        # Fetch conversation history
        result = client.conversations_history(channel=channel_id, limit=limit)

        messages = result["messages"]
        bot_messages = [msg for msg in messages if msg.get("user") == bot_user_id or msg.get("bot_id")]

        print(f"Found {len(bot_messages)} bot messages out of {len(messages)} total messages\n")

        if not bot_messages:
            print("✅ No bot messages to delete!")
            return

        # Ask for confirmation
        print("Messages to delete:")
        for i, msg in enumerate(bot_messages[:10], 1):  # Show first 10
            text = msg.get("text", "")[:50]
            ts = msg.get("ts")
            print(f"  {i}. [{ts}] {text}...")

        if len(bot_messages) > 10:
            print(f"  ... and {len(bot_messages) - 10} more")

        print(f"\n⚠️  This will delete {len(bot_messages)} messages!")
        confirm = input("Type 'yes' to confirm: ")

        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return

        # Delete messages
        deleted = 0
        failed = 0

        for msg in bot_messages:
            try:
                client.chat_delete(channel=channel_id, ts=msg["ts"])
                deleted += 1
                print(f"✅ Deleted message {deleted}/{len(bot_messages)}")
            except SlackApiError as e:
                failed += 1
                print(f"❌ Failed to delete message: {e.response['error']}")

        print(f"\n🎉 Done! Deleted {deleted} messages, {failed} failed")

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        if e.response['error'] == 'channel_not_found':
            print("   Make sure the channel ID is correct and the bot has access")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("  Delete Old Slack Approval Messages")
    print("=" * 70 + "\n")

    # Use the manager's DM channel by default
    channel_id = SLACK_MANAGER_USER_ID

    if len(sys.argv) > 1:
        channel_id = sys.argv[1]
        print(f"Using channel ID from argument: {channel_id}\n")
    else:
        print(f"Using manager DM channel: {channel_id}")
        print("(To use a different channel, run: python delete_old_slack_messages.py CHANNEL_ID)\n")

    delete_bot_messages(channel_id)

# Made with Bob
