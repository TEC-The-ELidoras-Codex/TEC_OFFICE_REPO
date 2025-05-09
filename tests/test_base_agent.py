"""
Tests for the base agent
"""
import os
import tempfile
import pytest
from src.agents.base_agent import BaseAgent

class TestBaseAgent:
    """Test the BaseAgent class."""
    
    def test_init_basic(self):
        """Test basic initialization of BaseAgent."""
        agent = BaseAgent("TestAgent")
        assert agent.name == "TestAgent"
        assert agent.config == {}
        
    def test_init_with_config(self):
        """Test initialization with config path."""
        # Create a temporary YAML config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.yaml")
            with open(config_path, 'w') as f:
                f.write("""
                test_key: test_value
                nested:
                    key1: value1
                    key2: value2
                """)
            
            # Initialize agent with the config path
            agent = BaseAgent("ConfigAgent", temp_dir)
            
            # Check that the config was loaded
            assert "test_key" in agent.config
            assert agent.config["test_key"] == "test_value"
            assert "nested" in agent.config
            assert agent.config["nested"]["key1"] == "value1"
            
    def test_run_method(self):
        """Test the run method of BaseAgent."""
        agent = BaseAgent("RunTestAgent")
        result = agent.run()
        
        # The base run method should return a specific response
        assert "status" in result
        assert result["status"] == "not_implemented"
        
    def test_agent_logger(self):
        """Test that the agent logger is properly configured."""
        agent = BaseAgent("LoggerTestAgent")
        assert agent.logger.name == "TEC.LoggerTestAgent"

class TestBaseAgentSubclass(BaseAgent):
    """A test subclass of BaseAgent with custom run implementation."""
    
    def __init__(self, name="TestSubclass", config_path=None):
        super().__init__(name, config_path)
        
    def run(self):
        """Custom run implementation."""
        return {"status": "success", "message": "Custom implementation"}
        
    def custom_method(self):
        """A custom method for testing."""
        return "custom method result"

class TestBaseAgentInheritance:
    """Test inheritance from BaseAgent."""
    
    def test_subclass_init(self):
        """Test initialization of a subclass."""
        agent = TestBaseAgentSubclass()
        assert agent.name == "TestSubclass"
        assert isinstance(agent, BaseAgent)
        
    def test_subclass_run(self):
        """Test that the subclass can override the run method."""
        agent = TestBaseAgentSubclass()
        result = agent.run()
        
        # The custom run method should return a different response
        assert result["status"] == "success"
        assert result["message"] == "Custom implementation"
        
    def test_subclass_custom_method(self):
        """Test a custom method on the subclass."""
        agent = TestBaseAgentSubclass()
        result = agent.custom_method()
        assert result == "custom method result"
