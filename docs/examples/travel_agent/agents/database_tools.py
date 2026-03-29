"""
Database Tools - Store and retrieve travel itineraries using SQLite

This module provides tools for:
- Initializing database schema
- Saving travel itineraries
- Retrieving itineraries
- Updating approval status
- Querying itineraries
- Getting pending approvals
"""

import os
import json
import sqlite3
import time
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Use absolute path to ensure consistency across different execution contexts
# __file__ is docs/examples/travel_agent/agents/database_tools.py
# We need to go up to TravelAgent/ root, then down to data/
_this_file = os.path.abspath(
    __file__
)  # /path/to/TravelAgent/docs/examples/travel_agent/agents/database_tools.py
_agents_dir = os.path.dirname(_this_file)  # /path/to/TravelAgent/docs/examples/travel_agent/agents/
_travel_agent_dir = os.path.dirname(_agents_dir)  # /path/to/TravelAgent/docs/examples/travel_agent/
_examples_dir = os.path.dirname(_travel_agent_dir)  # /path/to/TravelAgent/docs/examples/
_docs_dir = os.path.dirname(_examples_dir)  # /path/to/TravelAgent/docs/
_project_root = os.path.dirname(_docs_dir)  # /path/to/TravelAgent/
_default_db_path = os.path.join(
    _project_root, "data", "itineraries.db"
)  # /path/to/TravelAgent/data/itineraries.db
DATABASE_PATH = os.getenv("DATABASE_PATH", _default_db_path)

# Debug: Print database path on module load
print(f"🗄️  DATABASE_PATH: {DATABASE_PATH}")
print(f"🗄️  Absolute: {os.path.abspath(DATABASE_PATH)}")
print(f"🗄️  Path exists: {os.path.exists(DATABASE_PATH)}")
if os.path.exists(DATABASE_PATH):
    import sqlite3

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM itineraries")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"🗄️  Itineraries in database: {count}")


def get_db_connection():
    """Get database connection"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@tool
def initialize_database() -> str:
    """
    Initialize the database schema for storing travel itineraries.
    Creates tables if they don't exist.

    Returns:
        JSON string with initialization status

    Example:
        initialize_database()
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create itineraries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itineraries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_role TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                departure_date TEXT NOT NULL,
                return_date TEXT,
                flight_details TEXT,
                hotel_details TEXT,
                weather_info TEXT,
                expense_report TEXT,
                compliance_status TEXT,
                total_cost REAL,
                approval_status TEXT DEFAULT 'pending',
                manager_id TEXT,
                manager_comments TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                approved_at TEXT
            )
        ''')

        # Create approval_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS approval_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                itinerary_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                comments TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (itinerary_id) REFERENCES itineraries (id)
            )
        ''')

        conn.commit()
        conn.close()

        return json.dumps(
            {
                "success": True,
                "message": "Database initialized successfully",
                "database_path": DATABASE_PATH,
                "tables_created": ["itineraries", "approval_history"],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to initialize database"}, indent=2
        )


@tool
def save_itinerary(
    user_name: str = "Travel User",
    user_email: str = "user@company.com",
    user_role: str = "employee",
    origin: str = "Unknown",
    destination: str = "Unknown",
    departure_date: str = "TBD",
    return_date: Optional[str] = None,
    flight_details: str = '{"airline": "Selected Flight", "price": 0}',
    hotel_details: str = '{"hotel": "Selected Hotel", "price": 0}',
    weather_info: str = '{}',
    expense_report: str = '{"total": 0}',
    compliance_status: str = "pending review",
    total_cost: float = 0.0,
    manager_id: Optional[str] = "MGR-12345",
) -> str:
    """
    Save a travel itinerary to the database.
    ALL PARAMETERS ARE OPTIONAL - defaults will be used if not provided.

    Args:
        user_name: User's full name (default: "Travel User")
        user_email: User's email address (default: "user@company.com")
        user_role: User's role (default: "employee")
        origin: Origin airport/city (default: "Unknown")
        destination: Destination airport/city (default: "Unknown")
        departure_date: Departure date (default: "TBD")
        return_date: Return date (optional)
        flight_details: JSON string with flight information (default: basic JSON)
        hotel_details: JSON string with hotel information (default: basic JSON)
        weather_info: JSON string with weather forecast (default: empty JSON)
        expense_report: JSON string with expense breakdown (default: zero cost)
        compliance_status: Compliance check result (default: "pending review")
        total_cost: Total trip cost (default: 0.0)
        manager_id: Manager's ID for approval (default: "MGR-12345")

    Returns:
        JSON string with saved itinerary ID

    Example:
        # Can be called with minimal info:
        save_itinerary(origin="NYC", destination="LAX")
        # Or with full details:
        save_itinerary('John Doe', 'john@example.com', 'employee', ...)
    """
    try:
        # Initialize database if needed
        initialize_database.invoke({})

        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute(
            '''
            INSERT INTO itineraries (
                user_name, user_email, user_role, origin, destination,
                departure_date, return_date, flight_details, hotel_details,
                weather_info, expense_report, compliance_status, total_cost,
                approval_status, manager_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
            (
                user_name,
                user_email,
                user_role,
                origin,
                destination,
                departure_date,
                return_date,
                flight_details,
                hotel_details,
                weather_info,
                expense_report,
                compliance_status,
                total_cost,
                'pending',
                manager_id,
                now,
                now,
            ),
        )

        itinerary_id = cursor.lastrowid

        # Log creation in approval history
        cursor.execute(
            '''
            INSERT INTO approval_history (itinerary_id, action, actor, comments, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''',
            (itinerary_id, 'created', user_email, 'Itinerary created', now),
        )

        conn.commit()
        conn.close()

        return json.dumps(
            {
                "success": True,
                "itinerary_id": itinerary_id,
                "message": "Itinerary saved successfully",
                "approval_status": "pending",
                "created_at": now,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to save itinerary"}, indent=2
        )


@tool
def get_itinerary(itinerary_id: int) -> str:
    """
    Retrieve a travel itinerary by ID.

    Args:
        itinerary_id: Itinerary ID

    Returns:
        JSON string with itinerary details

    Example:
        get_itinerary(1)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM itineraries WHERE id = ?', (itinerary_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return json.dumps({"success": False, "error": f"Itinerary {itinerary_id} not found"})

        # Convert row to dict
        itinerary = dict(row)

        # Get approval history
        cursor.execute(
            '''
            SELECT * FROM approval_history 
            WHERE itinerary_id = ? 
            ORDER BY timestamp DESC
        ''',
            (itinerary_id,),
        )

        history = [dict(h) for h in cursor.fetchall()]

        conn.close()

        return json.dumps({"success": True, "itinerary": itinerary, "approval_history": history}, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to retrieve itinerary"}, indent=2
        )


@tool
def update_approval_status(
    itinerary_id: int, approval_status: str, manager_id: str, manager_comments: Optional[str] = None
) -> str:
    """
    Update the approval status of an itinerary.

    Args:
        itinerary_id: Itinerary ID
        approval_status: New status ('approved', 'rejected', 'pending')
        manager_id: Manager's ID who is approving/rejecting
        manager_comments: Optional comments from manager

    Returns:
        JSON string with update status

    Example:
        update_approval_status(1, 'approved', 'manager@example.com', 'Looks good')
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Update itinerary
        cursor.execute(
            '''
            UPDATE itineraries 
            SET approval_status = ?, 
                manager_id = ?,
                manager_comments = ?,
                approved_at = ?,
                updated_at = ?
            WHERE id = ?
        ''',
            (approval_status, manager_id, manager_comments, now, now, itinerary_id),
        )

        if cursor.rowcount == 0:
            conn.close()
            return json.dumps({"success": False, "error": f"Itinerary {itinerary_id} not found"})

        # Log approval action
        cursor.execute(
            '''
            INSERT INTO approval_history (itinerary_id, action, actor, comments, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''',
            (itinerary_id, approval_status, manager_id, manager_comments or '', now),
        )

        conn.commit()
        conn.close()

        return json.dumps(
            {
                "success": True,
                "itinerary_id": itinerary_id,
                "approval_status": approval_status,
                "manager_id": manager_id,
                "updated_at": now,
                "message": f"Itinerary {approval_status} by {manager_id}",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to update approval status"}, indent=2
        )


@tool
def query_itineraries(
    user_email: Optional[str] = None, approval_status: Optional[str] = None, limit: int = 10
) -> str:
    """
    Query itineraries with optional filters.

    Args:
        user_email: Filter by user email (optional)
        approval_status: Filter by approval status (optional)
        limit: Maximum number of results (default: 10)

    Returns:
        JSON string with matching itineraries

    Example:
        query_itineraries(user_email='john@example.com', approval_status='pending')
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query
        query = 'SELECT * FROM itineraries WHERE 1=1'
        params = []

        if user_email:
            query += ' AND user_email = ?'
            params.append(user_email)

        if approval_status:
            query += ' AND approval_status = ?'
            params.append(approval_status)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        itineraries = [dict(row) for row in rows]

        conn.close()

        return json.dumps(
            {
                "success": True,
                "count": len(itineraries),
                "itineraries": itineraries,
                "filters": {"user_email": user_email, "approval_status": approval_status, "limit": limit},
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to query itineraries"}, indent=2
        )


@tool
def get_pending_approvals(manager_id: Optional[str] = None) -> str:
    """
    Get all itineraries pending approval.

    Args:
        manager_id: Filter by specific manager (optional)

    Returns:
        JSON string with pending itineraries

    Example:
        get_pending_approvals('manager@example.com')
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM itineraries WHERE approval_status = 'pending'"
        params = []

        if manager_id:
            query += ' AND manager_id = ?'
            params.append(manager_id)

        query += ' ORDER BY created_at ASC'

        cursor.execute(query, params)
        rows = cursor.fetchall()

        pending = [dict(row) for row in rows]

        conn.close()

        return json.dumps(
            {
                "success": True,
                "pending_count": len(pending),
                "pending_itineraries": pending,
                "manager_id": manager_id,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to get pending approvals"}, indent=2
        )


@tool
def wait_for_approval(itinerary_id: int, timeout_seconds: int = 300, check_interval: int = 5) -> str:
    """
    Wait for manager approval of an itinerary. Polls the database until approval status changes.
    This allows the conversation to continue automatically when the manager approves via Slack.

    Args:
        itinerary_id: Itinerary ID to monitor
        timeout_seconds: Maximum time to wait in seconds (default: 300 = 5 minutes)
        check_interval: How often to check status in seconds (default: 5)

    Returns:
        JSON string with approval result

    Example:
        wait_for_approval(1, timeout_seconds=300)
    """
    try:
        start_time = time.time()
        elapsed = 0

        print(f"\n⏳ Waiting for manager approval (itinerary #{itinerary_id})...")
        print(f"   Will check every {check_interval} seconds for up to {timeout_seconds} seconds")

        while elapsed < timeout_seconds:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT approval_status, manager_id, manager_comments FROM itineraries WHERE id = ?',
                (itinerary_id,),
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return json.dumps({"success": False, "error": f"Itinerary {itinerary_id} not found"})

            status = row['approval_status']

            # Check if status has changed from pending
            if status == 'approved':
                print("\n✅ Approval received! Manager approved the itinerary.")
                return json.dumps(
                    {
                        "success": True,
                        "status": "approved",
                        "itinerary_id": itinerary_id,
                        "manager_id": row['manager_id'],
                        "manager_comments": row['manager_comments'],
                        "message": "Itinerary has been approved by manager. You can now proceed with booking.",
                    },
                    indent=2,
                )

            elif status == 'rejected':
                print("\n❌ Itinerary was rejected by manager.")
                return json.dumps(
                    {
                        "success": True,
                        "status": "rejected",
                        "itinerary_id": itinerary_id,
                        "manager_id": row['manager_id'],
                        "manager_comments": row['manager_comments'],
                        "message": "Itinerary was rejected. Please review manager's comments and create a new itinerary.",
                    },
                    indent=2,
                )

            # Still pending, wait and check again
            time.sleep(check_interval)
            elapsed = time.time() - start_time

            # Show progress every 30 seconds
            if int(elapsed) % 30 == 0 and elapsed > 0:
                print(f"   Still waiting... ({int(elapsed)}s elapsed)")

        # Timeout reached
        print(f"\n⏱️  Timeout reached after {timeout_seconds} seconds")
        return json.dumps(
            {
                "success": True,
                "status": "timeout",
                "itinerary_id": itinerary_id,
                "message": f"Approval request timed out after {timeout_seconds} seconds. The itinerary is still pending manager approval. You can check status later or contact your manager directly.",
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to wait for approval"}, indent=2
        )


@tool
def check_approval_status(itinerary_id: int) -> str:
    """
    Quick check of current approval status without waiting.
    Use this to check if an approval has been received.

    Args:
        itinerary_id: Itinerary ID to check

    Returns:
        JSON string with current status

    Example:
        check_approval_status(1)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT approval_status, manager_id, manager_comments, approved_at 
            FROM itineraries 
            WHERE id = ?
        ''',
            (itinerary_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return json.dumps({"success": False, "error": f"Itinerary {itinerary_id} not found"})

        return json.dumps(
            {
                "success": True,
                "itinerary_id": itinerary_id,
                "approval_status": row['approval_status'],
                "manager_id": row['manager_id'],
                "manager_comments": row['manager_comments'],
                "approved_at": row['approved_at'],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": str(e), "message": "Failed to check approval status"}, indent=2
        )


# Made with Bob
