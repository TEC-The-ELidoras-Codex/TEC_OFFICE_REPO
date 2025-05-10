"""
Tests for the Airth agent timer functionality.
"""
import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.airth_agent import AirthAgent
from src.utils.timer import PomodoroTimer, CountdownTimer

class TestAirthTimerFunctionality(unittest.TestCase):
    """Test cases for the timer functionality in AirthAgent."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary config path for testing
        self.test_config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        
        # Make sure the config directory exists
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # Mock the agent initialization to avoid loading unnecessary resources
        with patch('src.agents.airth_agent.AirthAgent._load_prompts', return_value={}), \
             patch('src.agents.airth_agent.AirthAgent._load_memories', return_value={}), \
             patch('src.agents.airth_agent.WordPressAgent', MagicMock()), \
             patch('src.agents.airth_agent.LocalStorageAgent', MagicMock()):
            
            self.agent = AirthAgent(self.test_config_dir)
            
        # Mock the AWS settings
        self.agent.use_aws_timers = False
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up any active timers
        if self.agent.pomodoro_timer:
            self.agent.pomodoro_timer.cancel()
        if self.agent.countdown_timer:
            self.agent.countdown_timer.cancel()
    
    def test_initialize_timers(self):
        """Test initializing the timers."""
        # Initially, timers should be None
        self.assertIsNone(self.agent.pomodoro_timer)
        self.assertIsNone(self.agent.countdown_timer)
        
        # Initialize pomodoro timer
        self.agent._initialize_pomodoro_timer("test_user")
        self.assertIsNotNone(self.agent.pomodoro_timer)
        self.assertIsInstance(self.agent.pomodoro_timer, PomodoroTimer)
        
        # Initialize countdown timer
        self.agent._initialize_countdown_timer("test_user")
        self.assertIsNotNone(self.agent.countdown_timer)
        self.assertIsInstance(self.agent.countdown_timer, CountdownTimer)
    
    def test_set_countdown_timer(self):
        """Test setting a countdown timer."""
        result = self.agent.set_timer(5, timer_type="countdown", timer_name="Test Timer")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["timer_type"], "countdown")
        self.assertIn("Test Timer", result["message"])
        
        # Check that the timer was initialized and started
        self.assertIsNotNone(self.agent.countdown_timer)
        self.assertTrue(self.agent.countdown_timer.active)
    
    def test_set_pomodoro_timer(self):
        """Test setting a pomodoro timer."""
        result = self.agent.set_timer(5, timer_type="pomodoro")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["timer_type"], "pomodoro")
        self.assertIn("work session", result["message"])
        
        # Check that the timer was initialized and started
        self.assertIsNotNone(self.agent.pomodoro_timer)
        self.assertTrue(self.agent.pomodoro_timer.active)
    
    def test_get_timer_status(self):
        """Test getting the timer status."""
        # Set both timers
        self.agent.set_timer(5, timer_type="countdown", timer_name="Test Countdown")
        self.agent.set_timer(5, timer_type="pomodoro")
        
        # Get status of both timers
        result = self.agent.get_timer_status()
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["active_timers"]), 2)
    
    def test_cancel_timer(self):
        """Test cancelling a timer."""
        # Set a timer
        self.agent.set_timer(5, timer_type="countdown", timer_name="Test Countdown")
        
        # Cancel the timer
        result = self.agent.cancel_timer("countdown")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["cancelled_timers"]), 1)
        self.assertEqual(result["cancelled_timers"][0]["timer_type"], "countdown")
        
        # Verify timer is no longer active
        self.assertFalse(self.agent.countdown_timer.active)
    
    def test_control_pomodoro(self):
        """Test controlling the pomodoro timer."""
        # Start a pomodoro timer
        self.agent.set_timer(5, timer_type="pomodoro")
        
        # Pause the timer
        result = self.agent.control_pomodoro("pause")
        self.assertTrue(result["success"])
        self.assertFalse(self.agent.pomodoro_timer.active)
        
        # Resume the timer
        result = self.agent.control_pomodoro("resume")
        self.assertTrue(result["success"])
        self.assertTrue(self.agent.pomodoro_timer.active)
        
        # Skip to the next phase
        result = self.agent.control_pomodoro("skip")
        self.assertTrue(result["success"])
        self.assertEqual(self.agent.pomodoro_timer.current_phase, "short_break")
    
    def test_process_timer_command(self):
        """Test processing natural language timer commands."""
        # Test setting a countdown timer
        result = self.agent.process_timer_command("set a timer for 10 minutes")
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.agent.countdown_timer)
        self.assertTrue(self.agent.countdown_timer.active)
        
        # Clean up
        self.agent.cancel_timer("countdown")
        
        # Test setting a timer with a name
        result = self.agent.process_timer_command("set a timer for 5 minutes called Meeting Timer")
        self.assertTrue(result["success"])
        self.assertEqual(self.agent.countdown_timer.timer_name, "Meeting Timer")
        
        # Clean up
        self.agent.cancel_timer("countdown")
        
        # Test setting a pomodoro timer
        result = self.agent.process_timer_command("start a pomodoro")
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.agent.pomodoro_timer)
        self.assertTrue(self.agent.pomodoro_timer.active)
        
        # Test getting timer status
        result = self.agent.process_timer_command("what's the status of my timer?")
        self.assertTrue(result["success"])
        self.assertIn("active_timers", result)
        
        # Test controlling pomodoro
        result = self.agent.process_timer_command("pause pomodoro")
        self.assertTrue(result["success"])
        self.assertFalse(self.agent.pomodoro_timer.active)
        
        result = self.agent.process_timer_command("resume pomodoro")
        self.assertTrue(result["success"])
        self.assertTrue(self.agent.pomodoro_timer.active)
        
        # Test cancelling timer
        result = self.agent.process_timer_command("cancel pomodoro timer")
        self.assertTrue(result["success"])
        self.assertFalse(self.agent.pomodoro_timer.active)
    
    def test_respond_to_timer_command(self):
        """Test getting personalized responses to timer commands."""
        # Test response for setting a timer
        result = self.agent.respond_to_timer_command("set a timer for 10 minutes")
        self.assertTrue(result["success"])
        self.assertIn("airth_response", result)
        
        # Clean up
        self.agent.cancel_timer("countdown")
        
        # Test response for pomodoro timer
        result = self.agent.respond_to_timer_command("start a pomodoro timer")
        self.assertTrue(result["success"])
        self.assertIn("airth_response", result)
        
        # Test response for error
        result = self.agent.respond_to_timer_command("do something with my timer")
        self.assertFalse(result["success"])
        self.assertIn("airth_response", result)

if __name__ == "__main__":
    unittest.main()
