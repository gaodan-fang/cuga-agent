"""Test Supervisor Configuration"""

import yaml
import os
import sys


def test_supervisor_config_exists():
    """Test that supervisor config file exists"""
    config_path = "docs/examples/travel_agent/config/supervisor_travel_agent.yaml"
    assert os.path.exists(config_path), f"Config file not found: {config_path}"
    print("✅ Supervisor config file exists")


def test_supervisor_config_valid():
    """Test that supervisor config is valid YAML"""
    config_path = "docs/examples/travel_agent/config/supervisor_travel_agent.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Verify required sections
    assert "supervisor" in config, "Missing 'supervisor' section"
    assert "agents" in config, "Missing 'agents' section"

    # Verify supervisor has required fields
    assert "name" in config["supervisor"], "Missing supervisor name"
    assert "description" in config["supervisor"], "Missing supervisor description"

    print("✅ Supervisor configuration has required sections")


def test_all_agents_defined():
    """Test that all 5 agents are defined"""
    config_path = "docs/examples/travel_agent/config/supervisor_travel_agent.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Verify all 5 agents are defined
    agent_names = [agent["name"] for agent in config["agents"]]
    expected_agents = ["flight_agent", "hotel_agent", "weather_agent", "finance_agent", "compliance_agent"]

    for expected in expected_agents:
        assert expected in agent_names, f"Missing agent: {expected}"

    print(f"✅ All {len(expected_agents)} agents are defined")


def test_agents_have_tools():
    """Test that each agent has tools defined"""
    config_path = "docs/examples/travel_agent/config/supervisor_travel_agent.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    for agent in config["agents"]:
        assert "tools" in agent, f"Agent {agent['name']} missing tools"
        assert len(agent["tools"]) > 0, f"Agent {agent['name']} has no tools"

        # Verify each tool has name and module
        for tool in agent["tools"]:
            assert "name" in tool, f"Tool in {agent['name']} missing name"
            assert "module" in tool, f"Tool in {agent['name']} missing module"

    print("✅ All agents have tools properly defined")


def test_agent_descriptions():
    """Test that each agent has a description"""
    config_path = "docs/examples/travel_agent/config/supervisor_travel_agent.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    for agent in config["agents"]:
        assert "description" in agent, f"Agent {agent['name']} missing description"
        assert len(agent["description"]) > 0, f"Agent {agent['name']} has empty description"

    print("✅ All agents have descriptions")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Supervisor Configuration")
    print("=" * 60 + "\n")

    try:
        test_supervisor_config_exists()
        test_supervisor_config_valid()
        test_all_agents_defined()
        test_agents_have_tools()
        test_agent_descriptions()

        print("\n" + "=" * 60)
        print("✅ All supervisor configuration tests passed!")
        print("=" * 60 + "\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)

# Made with Bob
