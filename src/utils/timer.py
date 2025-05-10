"""
Timer utilities for The Elidoras Codex.
This module provides timer functionality, particularly for Pomodoro technique.
"""
import os
import time
import threading
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger("TEC.Utils.Timer")

class PomodoroTimer:
    """
    Implementation of the Pomodoro Technique timer.
    
    The Pomodoro Technique is a time management method that uses a timer to break
    work into intervals, traditionally 25 minutes in length, separated by short breaks.
    """
    
    def __init__(self, 
                 work_minutes: int = 25, 
                 short_break_minutes: int = 5,
                 long_break_minutes: int = 15,
                 long_break_interval: int = 4,
                 user_id: str = "default",
                 use_aws: bool = False,
                 aws_region: str = "us-east-1"):
        """
        Initialize a new Pomodoro timer.
        
        Args:
            work_minutes: Length of a work session in minutes (default: 25)
            short_break_minutes: Length of a short break in minutes (default: 5)
            long_break_minutes: Length of a long break in minutes (default: 15)
            long_break_interval: Number of work sessions before a long break (default: 4)
            user_id: Identifier for the user (for storing timer state)
            use_aws: Whether to use AWS for state persistence
            aws_region: AWS region for storing timer state
        """
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.long_break_interval = long_break_interval
        self.user_id = user_id
        self.use_aws = use_aws
        self.aws_region = aws_region
        
        # State variables
        self.active = False
        self.timer_thread = None
        self.completed_pomodoros = 0
        self.current_phase = "idle"  # idle, work, short_break, long_break
        self.end_time = None
        self.callbacks = {
            "on_complete": [],
            "on_start": [],
            "on_pause": [],
            "on_resume": [],
            "on_cancel": []
        }
        
        # AWS resources
        self.dynamodb = None
        self.table = None
        if self.use_aws:
            self._initialize_aws()
            
        # Load any existing state
        self._load_state()
        
    def _initialize_aws(self):
        """Initialize AWS resources for timer persistence."""
        try:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.aws_region)
            self.table = self.dynamodb.Table('TEC_PomodoroTimers')
            logger.info("Connected to AWS DynamoDB for timer persistence")
        except ClientError as e:
            logger.error(f"Failed to initialize AWS DynamoDB: {e}")
            self.use_aws = False
            
    def _save_state(self):
        """Save the current timer state."""
        state = {
            "work_minutes": self.work_minutes,
            "short_break_minutes": self.short_break_minutes,
            "long_break_minutes": self.long_break_minutes,
            "long_break_interval": self.long_break_interval,
            "completed_pomodoros": self.completed_pomodoros,
            "current_phase": self.current_phase,
            "active": self.active,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        if self.use_aws and self.table:
            try:
                self.table.put_item(Item={
                    "user_id": self.user_id,
                    "timer_state": json.dumps(state)
                })
                logger.debug(f"Saved timer state to AWS DynamoDB for user {self.user_id}")
            except ClientError as e:
                logger.error(f"Failed to save timer state to AWS: {e}")
                self._save_state_local(state)
        else:
            self._save_state_local(state)
    
    def _save_state_local(self, state):
        """Save the timer state locally."""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'storage')
            os.makedirs(data_dir, exist_ok=True)
            
            file_path = os.path.join(data_dir, f'pomodoro_{self.user_id}.json')
            with open(file_path, 'w') as f:
                json.dump(state, f)
                
            logger.debug(f"Saved timer state locally to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save timer state locally: {e}")
    
    def _load_state(self):
        """Load the timer state."""
        state = None
        
        # Try loading from AWS first
        if self.use_aws and self.table:
            try:
                response = self.table.get_item(Key={"user_id": self.user_id})
                if "Item" in response:
                    state = json.loads(response["Item"]["timer_state"])
                    logger.debug(f"Loaded timer state from AWS for user {self.user_id}")
            except ClientError as e:
                logger.error(f"Failed to load timer state from AWS: {e}")
        
        # Fall back to local if AWS failed or not enabled
        if not state:
            try:
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'storage')
                file_path = os.path.join(data_dir, f'pomodoro_{self.user_id}.json')
                
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        state = json.load(f)
                    logger.debug(f"Loaded timer state from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load timer state locally: {e}")
        
        # Apply loaded state if available
        if state:
            self.work_minutes = state.get("work_minutes", self.work_minutes)
            self.short_break_minutes = state.get("short_break_minutes", self.short_break_minutes)
            self.long_break_minutes = state.get("long_break_minutes", self.long_break_minutes)
            self.long_break_interval = state.get("long_break_interval", self.long_break_interval)
            self.completed_pomodoros = state.get("completed_pomodoros", 0)
            self.current_phase = state.get("current_phase", "idle")
            
            # Only restore active timer if it hasn't expired
            if state.get("active", False) and state.get("end_time"):
                end_time = datetime.fromisoformat(state["end_time"])
                if end_time > datetime.utcnow():
                    self.active = True
                    self.end_time = end_time
                    self._start_timer_thread()
                    logger.info(f"Restored active timer with {(end_time - datetime.utcnow()).total_seconds():.1f} seconds remaining")
    
    def add_callback(self, event: str, callback: Callable):
        """
        Add a callback function for timer events.
        
        Args:
            event: Event type ("on_complete", "on_start", "on_pause", "on_resume", "on_cancel")
            callback: Function to call when the event occurs
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            
    def _trigger_callbacks(self, event: str):
        """
        Trigger all registered callbacks for an event.
        
        Args:
            event: Event type to trigger callbacks for
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(self)
                except Exception as e:
                    logger.error(f"Error in timer callback: {e}")
    
    def start(self, phase: str = None):
        """
        Start the timer.
        
        Args:
            phase: Optional phase to start ("work", "short_break", "long_break")
                  If not provided, will use appropriate next phase based on completed pomodoros
        """
        if self.active:
            logger.warning("Timer is already running")
            return
        
        # Determine which phase to start if not specified
        if not phase:
            if self.current_phase == "idle" or self.current_phase == "work":
                phase = "work"
            elif self.current_phase == "short_break":
                phase = "work"
            elif self.current_phase == "long_break":
                phase = "work"
        
        # Set the current phase and duration
        self.current_phase = phase
        if phase == "work":
            duration_minutes = self.work_minutes
        elif phase == "short_break":
            duration_minutes = self.short_break_minutes
        elif phase == "long_break":
            duration_minutes = self.long_break_minutes
        else:
            logger.error(f"Unknown timer phase: {phase}")
            return
            
        # Calculate end time
        self.end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.active = True
        
        # Start the timer thread
        self._start_timer_thread()
        
        # Save the state
        self._save_state()
        
        # Trigger callbacks
        self._trigger_callbacks("on_start")
        
        logger.info(f"Started {phase} timer for {duration_minutes} minutes")
        
    def _start_timer_thread(self):
        """Start the timer thread to track completion."""
        if self.timer_thread is not None:
            self.timer_thread.cancel()
              time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
        self.timer_thread = threading.Timer(time_remaining, self._timer_complete)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def _timer_complete(self):
        """Handle timer completion."""
        if not self.active:
            return
            
        logger.info(f"Timer complete: {self.current_phase}")
        
        # Update state based on completed phase
        if self.current_phase == "work":
            self.completed_pomodoros += 1
            
            # Determine next break type
            if self.completed_pomodoros % self.long_break_interval == 0:
                self.current_phase = "long_break"
            else:
                self.current_phase = "short_break"
        elif self.current_phase == "short_break" or self.current_phase == "long_break":
            # After any break, the next phase is work
            self.current_phase = "work"
        
        self.active = False
        self.timer_thread = None
        
        # Save the state
        self._save_state()
        
        # Trigger callbacks
        self._trigger_callbacks("on_complete")
    
    def pause(self):
        """Pause the active timer."""
        if not self.active:
            logger.warning("No active timer to pause")
            return
            
        # Calculate remaining time
        time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
        
        # Stop the timer thread
        if self.timer_thread:
            self.timer_thread.cancel()
            self.timer_thread = None
            
        # Update state
        self.active = False
        self.end_time = datetime.utcnow() + timedelta(seconds=time_remaining)
        
        # Save the state
        self._save_state()
        
        # Trigger callbacks
        self._trigger_callbacks("on_pause")
        
        logger.info(f"Paused {self.current_phase} timer with {time_remaining:.1f} seconds remaining")
    
    def resume(self):
        """Resume a paused timer."""
        if self.active:
            logger.warning("Timer is already running")
            return
            
        if self.current_phase == "idle":
            logger.warning("No paused timer to resume")
            return
            
        # Start the timer thread
        self.active = True
        self._start_timer_thread()
        
        # Save the state
        self._save_state()
        
        # Trigger callbacks
        self._trigger_callbacks("on_resume")
        
        time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
        logger.info(f"Resumed {self.current_phase} timer with {time_remaining:.1f} seconds remaining")
    
    def cancel(self):
        """Cancel the active timer."""
        if not self.active and self.current_phase == "idle":
            logger.warning("No timer to cancel")
            return
            
        # Stop the timer thread
        if self.timer_thread:
            self.timer_thread.cancel()
            self.timer_thread = None
            
        # Update state
        self.active = False
        self.current_phase = "idle"
        self.end_time = None
        
        # Save the state
        self._save_state()
        
        # Trigger callbacks
        self._trigger_callbacks("on_cancel")
        
        logger.info("Timer cancelled")
    
    def skip(self):
        """Skip to the next phase of the Pomodoro cycle."""
        # Cancel current timer
        if self.active and self.timer_thread:
            self.timer_thread.cancel()
            self.timer_thread = None
            
        # Force completion of current phase
        self._timer_complete()
        
        logger.info(f"Skipped to next phase: {self.current_phase}")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the timer.
        
        Returns:
            Dictionary with the current timer status
        """
        status = {
            "active": self.active,
            "phase": self.current_phase,
            "completed_pomodoros": self.completed_pomodoros
        }
        
        if self.active and self.end_time:
            time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
            status["time_remaining_seconds"] = time_remaining
            status["time_remaining_formatted"] = self._format_time(time_remaining)
            
        return status
    
    def _format_time(self, seconds: float) -> str:
        """
        Format time in seconds as MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


class CountdownTimer:
    """Simple countdown timer for setting arbitrary countdowns."""
    
    def __init__(self, user_id: str = "default", use_aws: bool = False):
        """
        Initialize a countdown timer.
        
        Args:
            user_id: Identifier for the user
            use_aws: Whether to use AWS for state persistence
        """
        self.user_id = user_id
        self.use_aws = use_aws
        
        # State variables
        self.active = False
        self.timer_thread = None
        self.end_time = None
        self.timer_name = None
        self.callbacks = {
            "on_complete": [],
            "on_start": [],
            "on_cancel": []
        }
        
        # AWS resources - reuse the PomodoroTimer AWS connection logic if needed
        
    def start(self, minutes: float, timer_name: str = None):
        """
        Start a countdown timer.
        
        Args:
            minutes: Duration in minutes
            timer_name: Optional name for the timer
        """
        if self.active:
            self.cancel()
            
        self.timer_name = timer_name or f"Timer for {minutes} minutes"
        self.end_time = datetime.utcnow() + timedelta(minutes=minutes)
        self.active = True
        
        # Start the timer thread
        time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
        self.timer_thread = threading.Timer(time_remaining, self._timer_complete)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        # Trigger callbacks
        for callback in self.callbacks["on_start"]:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in timer callback: {e}")
                
        logger.info(f"Started countdown timer '{self.timer_name}' for {minutes} minutes")
    
    def _timer_complete(self):
        """Handle timer completion."""
        if not self.active:
            return
            
        logger.info(f"Countdown timer complete: {self.timer_name}")
        
        self.active = False
        self.timer_thread = None
        
        # Trigger callbacks
        for callback in self.callbacks["on_complete"]:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in timer callback: {e}")
    
    def cancel(self):
        """Cancel the active timer."""
        if not self.active:
            return
            
        # Stop the timer thread
        if self.timer_thread:
            self.timer_thread.cancel()
            self.timer_thread = None
            
        # Update state
        self.active = False
        
        # Trigger callbacks
        for callback in self.callbacks["on_cancel"]:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in timer callback: {e}")
                
        logger.info(f"Cancelled countdown timer: {self.timer_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the timer.
        
        Returns:
            Dictionary with the current timer status
        """
        status = {
            "active": self.active,
            "name": self.timer_name
        }
        
        if self.active and self.end_time:
            time_remaining = max(0, (self.end_time - datetime.utcnow()).total_seconds())
            minutes = int(time_remaining // 60)
            seconds = int(time_remaining % 60)
            
            status["time_remaining_seconds"] = time_remaining
            status["time_remaining_formatted"] = f"{minutes:02d}:{seconds:02d}"
            
        return status
    
    def add_callback(self, event: str, callback: Callable):
        """
        Add a callback function for timer events.
        
        Args:
            event: Event type ("on_complete", "on_start", "on_cancel")
            callback: Function to call when the event occurs
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
