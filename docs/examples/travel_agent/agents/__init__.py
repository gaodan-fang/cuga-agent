"""
Travel Agent Tools - Specialized agents with their tools

This module provides pre-configured agent instances for the travel agent system.
Each agent is configured with its specific tools following the pattern:

    agent = CugaAgent(tools=[tool1, tool2, ...])
    agent.description = "Agent description"
"""

from src.cuga.sdk import CugaAgent

# Import approval agent (pre-configured in its own file)
from docs.examples.travel_agent.agents.approval_agent import approval_agent

# Import all tools
from docs.examples.travel_agent.agents.flight_agent_tools import (
    search_flights,
    filter_flights_by_price,
    filter_flights_by_airline,
    get_cheapest_flight,
    filter_direct_flights_only,
)

from docs.examples.travel_agent.agents.hotel_agent_tools import (
    search_hotels,
    filter_hotels_by_price,
    filter_hotels_by_rating,
    filter_hotels_by_amenities,
    get_best_value_hotel,
    get_cheapest_hotel,
)

from docs.examples.travel_agent.agents.weather_agent_tools import (
    get_weather_forecast,
    get_current_weather,
    get_packing_suggestions,
)

from docs.examples.travel_agent.agents.finance_agent_tools import (
    calculate_flight_costs,
    calculate_hotel_costs,
    calculate_per_diem,
    generate_expense_report,
    validate_budget,
    calculate_total_trip_cost,
)

from docs.examples.travel_agent.agents.compliance_agent_tools import (
    analyze_travel_compliance,
    # load_user_policy,
    # filter_travel_options,
    # validate_flight_policy,
    # validate_hotel_policy,
    # validate_total_budget,
    # check_overall_compliance,
    # suggest_compliant_alternatives
)

from docs.examples.travel_agent.agents.database_tools import (
    initialize_database,
    save_itinerary,
    get_itinerary,
    update_approval_status,
    query_itineraries,
    get_pending_approvals,
    wait_for_approval,
    check_approval_status,
)

from docs.examples.travel_agent.agents.slack_tools import (
    send_approval_request,
    check_approval_status as slack_check_approval_status,
    send_approval_notification,
    send_booking_confirmation,
    send_trip_reminder,
)

# Create Flight Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
flight_agent = CugaAgent(
    tools=[
        search_flights,
        filter_flights_by_price,
        filter_flights_by_airline,
        filter_direct_flights_only,
    ]
)

# Create Hotel Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
hotel_agent = CugaAgent(
    tools=[
        search_hotels,
        filter_hotels_by_price,
        filter_hotels_by_rating,
        filter_hotels_by_amenities,
    ]
)

# Create Weather Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
weather_agent = CugaAgent(tools=[get_weather_forecast, get_current_weather, get_packing_suggestions])

# Create Finance Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
finance_agent = CugaAgent(
    tools=[
        calculate_flight_costs,
        calculate_hotel_costs,
        calculate_per_diem,
        generate_expense_report,
        validate_budget,
        calculate_total_trip_cost,
    ]
)

# Create Compliance Agent with Cuga Policy System + Tool Guide
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
# This agent uses a simple LLM-based tool that receives policy guidance from Tool Guides
compliance_agent = CugaAgent(
    tools=[analyze_travel_compliance],  # Simple tool that leverages Tool Guide
    cuga_folder="docs/examples/travel_agent/cuga_policies",  # Load Tool Guides from cuga_policies folder
    auto_load_policies=True,  # Automatically load Tool Guides on initialization
    filesystem_sync=True,  # Enable policy filesystem sync
)

# Create Database Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
database_agent = CugaAgent(
    tools=[
        initialize_database,
        save_itinerary,
        get_itinerary,
        update_approval_status,
        query_itineraries,
        get_pending_approvals,
        wait_for_approval,
        check_approval_status,
    ]
)

# Create Slack Agent
# Description is defined in travel_agent/config/supervisor_travel_agent.yaml
slack_agent = CugaAgent(
    tools=[
        send_approval_request,
        slack_check_approval_status,
        send_approval_notification,
        send_booking_confirmation,
        send_trip_reminder,
    ]
)

# Export all agents and tools
__all__ = [
    # Agents
    'approval_agent',
    'flight_agent',
    'hotel_agent',
    'weather_agent',
    'finance_agent',
    'compliance_agent',
    'database_agent',
    'slack_agent',
    # Flight tools
    'search_flights',
    'filter_flights_by_price',
    'filter_flights_by_airline',
    'get_cheapest_flight',
    'filter_direct_flights_only',
    # Hotel tools
    'search_hotels',
    'filter_hotels_by_price',
    'filter_hotels_by_rating',
    'filter_hotels_by_amenities',
    'get_best_value_hotel',
    'get_cheapest_hotel',
    # Weather tools
    'get_weather_forecast',
    'get_current_weather',
    'get_packing_suggestions',
    # Finance tools
    'calculate_flight_costs',
    'calculate_hotel_costs',
    'calculate_per_diem',
    'generate_expense_report',
    'validate_budget',
    'calculate_total_trip_cost',
    # Compliance tools
    'load_user_policy',
    'validate_flight_policy',
    'validate_hotel_policy',
    'validate_total_budget',
    'check_overall_compliance',
    'suggest_compliant_alternatives',
    # Database tools
    'initialize_database',
    'save_itinerary',
    'get_itinerary',
    'update_approval_status',
    'query_itineraries',
    'get_pending_approvals',
    'wait_for_approval',
    'check_approval_status',
    # Slack tools
    'send_approval_request',
    'send_approval_notification',
    'send_booking_confirmation',
    'send_trip_reminder',
]

# Made with Bob
