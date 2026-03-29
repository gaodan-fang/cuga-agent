"""
Approval Agent - Handles the manager approval workflow

This agent is responsible for:
1. Saving itineraries to the database
2. Sending approval requests to managers via Slack
3. Waiting for manager decisions
4. Reporting approval status back to the supervisor
"""

from cuga.sdk import CugaAgent
from docs.examples.travel_agent.agents.database_tools import (
    save_itinerary,
    check_approval_status,
)
from docs.examples.travel_agent.agents.slack_tools import send_approval_request

# Create the approval agent
approval_agent = CugaAgent(
    tools=[save_itinerary, send_approval_request, check_approval_status],
    special_instructions="""
    You handle travel approvals. Extract trip details from supervisor's message and save them.
    
    DEFAULT VALUES (use if not provided in message):
    - user_name: "John Doe"
    - user_email: "john.doe@company.com"
    
    REQUIRED: Use this EXACT code pattern:
    
    ```python
    import json
    
    # Extract details from supervisor's message, use defaults for user info
    save_result = await save_itinerary(
        user_name="John Doe",  # Default value
        user_email="john.doe@company.com",  # Default value
        origin="<extract from message>",
        destination="<extract from message>",
        departure_date="<extract from message>",
        return_date="<extract from message>",
        flight_details="<extract from message>",
        hotel_details="<extract from message>",
        total_cost=<extract number from message>
    )
    
    # Parse the JSON string result
    parsed = json.loads(save_result)
    itinerary_id = parsed["itinerary_id"]
    
    # Send approval request with same details
    approval_result = await send_approval_request(
        employee_name="John Doe",  # Default value
        employee_email="john.doe@company.com",  # Default value
        itinerary_id=itinerary_id,
        origin="<same as above>",
        destination="<same as above>",
        departure_date="<same as above>",
        return_date="<same as above>",
        total_cost=<same as above>,
        flight_summary="<same as flight_details>",
        hotel_summary="<same as hotel_details>"
    )
    
    print(f"Sent for approval, ID: {itinerary_id}")
    ```
    
    CRITICAL: ALWAYS use "John Doe" and "john.doe@company.com" for user info. Extract all other details from the message.
    """,
)
