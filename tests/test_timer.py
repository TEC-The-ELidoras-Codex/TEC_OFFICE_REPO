"""
Tests for the timer utility.
"""
import unittest
import os
import sys
import time
from datetime import datetime, timedelta
import threading
from unittest.mock import MagicMock, patch

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.timer import PomodoroTimer, CountdownTimer

class TestPomodoroTimer(unittest.TestCase):
    """Test cases for the PomodoroTimer class."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a test user ID to avoid interfering with real data
        self.user_id = "test_user"
        self.timer = PomodoroTimer(
            work_minutes=0.05,  # 3 seconds for faster tests
            short_break_minutes=0.05,
            long_break_minutes=0.1,
            long_break_interval=2,
            user_id=self.user_id
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Cancel any active timers to avoid affecting other tests
        if self.timer.active:
            self.timer.cancel()
            
        # Clean up test data file if it exists
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'storage')
        test_file = os.path.join(data_dir, f'pomodoro_{self.user_id}.json')
        if os.path.exists(test_file):
            os.remove(test_file)
    
    def test_initialization(self):
        """Test timer initialization."""
        self.assertEqual(self.timer.work_minutes, 0.05)
        self.assertEqual(self.timer.short_break_minutes, 0.05)
        self.assertEqual(self.timer.long_break_minutes, 0.1)
        self.assertEqual(self.timer.long_break_interval, 2)
        self.assertEqual(self.timer.user_id, "test_user")
        self.assertEqual(self.timer.completed_pomodoros, 0)
        self.assertEqual(self.timer.current_phase, "idle")
        self.assertFalse(self.timer.active)
    
    def test_start_timer(self):
        """Test starting the timer."""
        self.timer.start()
        self.assertTrue(self.timer.active)
        self.assertEqual(self.timer.current_phase, "work")
        self.assertIsNotNone(self.timer.end_time)
        
    def test_pause_resume_timer(self):
        """Test pausing and resuming the timer."""
        self.timer.start()
        self.assertTrue(self.timer.active)
        
        self.timer.pause()
        self.assertFalse(self.timer.active)
        
        self.timer.resume()
        self.assertTrue(self.timer.active)
    
    def test_cancel_timer(self):
        """Test cancelling the timer."""
        self.timer.start()
        self.assertTrue(self.timer.active)
        
        self.timer.cancel()
        self.assertFalse(self.timer.active)
        self.assertEqual(self.timer.current_phase, "idle")
        self.assertIsNone(self.timer.end_time)
    
    def test_get_status(self):
        """Test getting the timer status."""
        status = self.timer.get_status()
        self.assertFalse(status["active"])
        self.assertEqual(status["phase"], "idle")
        
        self.timer.start()
        status = self.timer.get_status()
        self.assertTrue(status["active"])
        self.assertEqual(status["phase"], "work")
        self.assertIn("time_remaining_seconds", status)
        self.assertIn("time_remaining_formatted", status)
    
    def test_callback(self):
        """Test adding and triggering callbacks."""
        callback_triggered = threading.Event()
        
        def on_complete(_):
            callback_triggered.set()
        
        self.timer.add_callback("on_complete", on_complete)
        
        # Use a very short timer to ensure completion during the test
        self.timer.work_minutes = 0.01  # Less than a second
        self.timer.start()
        
        # Wait for the callback to be triggered (with timeout)
        self.assertTrue(callback_triggered.wait(2), "Callback was not triggered")
    
    def test_pomodoro_sequence(self):
        """Test the Pomodoro sequence flow."""
        # Mock the timer to complete instantly
        with patch.object(self.timer, '_start_timer_thread', lambda: self.timer._timer_complete()):
            # Start first work session
            self.timer.start()
            self.assertEqual(self.timer.current_phase, "short_break")
            self.assertEqual(self.timer.completed_pomodoros, 1)
            
            # Short break completes -> work
            self.timer._timer_complete()
            self.assertEqual(self.timer.current_phase, "work")
            
            # Work completes -> long break (after 2 pomodoros)
            self.timer._timer_complete()
            self.assertEqual(self.timer.current_phase, "long_break")
            self.assertEqual(self.timer.completed_pomodoros, 2)
            
            # Long break completes -> work
            self.timer._timer_complete()
            self.assertEqual(self.timer.current_phase, "work")

class TestCountdownTimer(unittest.TestCase):
    """Test cases for the CountdownTimer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.timer = CountdownTimer(user_id="test_user")
    
    def tearDown(self):
        """Clean up after tests."""
        if self.timer.active:
            self.timer.cancel()
    
    def test_initialization(self):
        """Test timer initialization."""
        self.assertEqual(self.timer.user_id, "test_user")
        self.assertFalse(self.timer.active)
        self.assertIsNone(self.timer.timer_name)
    
    def test_start_timer(self):
        """Test starting the timer."""
        self.timer.start(0.1, "Test Timer")
        self.assertTrue(self.timer.active)
        self.assertEqual(self.timer.timer_name, "Test Timer")
        self.assertIsNotNone(self.timer.end_time)
    
    def test_cancel_timer(self):
        """Test cancelling the timer."""
        self.timer.start(0.1, "Test Timer")
        self.assertTrue(self.timer.active)
        
        self.timer.cancel()
        self.assertFalse(self.timer.active)
    
    def test_get_status(self):
        """Test getting the timer status."""
        status = self.timer.get_status()
        self.assertFalse(status["active"])
        
        self.timer.start(0.1, "Test Timer")
        status = self.timer.get_status()
        self.assertTrue(status["active"])
        self.assertEqual(status["name"], "Test Timer")
        self.assertIn("time_remaining_seconds", status)
        self.assertIn("time_remaining_formatted", status)
    
    def test_callback(self):
        """Test adding and triggering callbacks."""
        callback_triggered = threading.Event()
        
        def on_complete(_):
            callback_triggered.set()
        
        self.timer.add_callback("on_complete", on_complete)
        
        # Use a very short timer to ensure completion during the test
        self.timer.start(0.01, "Quick Test")
        
        # Wait for the callback to be triggered (with timeout)
        self.assertTrue(callback_triggered.wait(2), "Callback was not triggered")

if __name__ == "__main__":
    unittest.main()
