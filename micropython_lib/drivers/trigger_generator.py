"""
Trigger Generator Library for ESP32-C6 Sequencer Project

This module provides a trigger generator that manages up to 7 gate outputs with
high-priority threading. The trigger system responds to clock events and manages
trigger timing, neopixel feedback, and automatic reset functionality.

Algorithm Overview:
- Initialize trigger outputs and neopixel display reference
- Create high-priority thread for trigger processing
- Handle clock events with trigger scheduling and execution
- Manage 50ms trigger duration with single timer
- Update neopixel colors based on trigger states
- Support up to 7 trigger outputs with individual control
- Thread-safe operation with proper synchronization
"""

import machine
import time
import _thread
from neopixel_display import NeopixelDisplay, RED, GREEN

class TriggerGenerator:
    def __init__(self, neopixel_display, trigger_pins=None, reset_timer_id=0):
        """
        Initialize trigger generator
        
        Args:
            neopixel_display: NeopixelDisplay object for visual feedback
            trigger_pins: List of GPIO pins for trigger outputs (default: pins 3-9)
            reset_timer_id: Timer ID for trigger reset (default: 0)
        """
        self.neopixel_display = neopixel_display
        self.reset_timer_id = reset_timer_id
        
        # Default trigger pins if not provided
        if trigger_pins is None:
            self.trigger_pins = [3, 4, 5, 6, 7, 8, 9]  # GPIO pins for triggers 1-7
        else:
            self.trigger_pins = trigger_pins[:7]  # Limit to 7 triggers
        
        self.num_triggers = len(self.trigger_pins)
        
        # Initialize trigger output pins
        self.trigger_outputs = []
        for pin in self.trigger_pins:
            trigger_pin = machine.Pin(pin, machine.Pin.OUT)
            trigger_pin.off()  # Start with triggers off
            self.trigger_outputs.append(trigger_pin)
        
        # Initialize reset timer
        self.reset_timer = machine.Timer(reset_timer_id)
        
        # Trigger state management
        self.current_triggers = [False] * self.num_triggers
        self.scheduled_triggers = [False] * self.num_triggers
        self.trigger_states = [False] * self.num_triggers  # Previous states for neopixel updates
        
        # Thread management
        self.trigger_thread = None
        self.thread_lock = _thread.allocate_lock()
        self.is_running = False
        self.clock_event = False
        
        # Statistics
        self.trigger_count = [0] * self.num_triggers
        self.last_trigger_time = [0] * self.num_triggers
        
    def _trigger_thread_function(self):
        """Main trigger thread function - runs at high priority"""
        while self.is_running:
            with self.thread_lock:
                if self.clock_event:
                    # Process current clock event
                    self._process_clock_event()
                    self.clock_event = False
                else:
                    # No clock event, sleep briefly
                    time.sleep_us(100)
    
    def _process_clock_event(self):
        """Process a clock event - generate triggers and schedule next"""
        # 1. Generate positive going signals for scheduled triggers
        for i in range(self.num_triggers):
            if self.scheduled_triggers[i]:
                self.trigger_outputs[i].on()
                self.current_triggers[i] = True
                self.trigger_count[i] += 1
                self.last_trigger_time[i] = time.ticks_ms()
        
        # 2. Update neopixel colors based on trigger state changes
        self._update_neopixel_colors()
        
        # 3. Schedule triggers for next clock (this would be set by sequencer logic)
        # For now, we'll clear the scheduled triggers
        self.scheduled_triggers = [False] * self.num_triggers
        
        # 4. Start 50ms timer to clear triggers
        self._start_reset_timer()
    
    def _update_neopixel_colors(self):
        """Update neopixel colors based on trigger state changes"""
        for i in range(self.num_triggers):
            current_state = self.current_triggers[i]
            previous_state = self.trigger_states[i]
            
            if current_state != previous_state:
                # State changed, update neopixel
                if current_state:
                    # Trigger went high - set to green
                    self.neopixel_display.set_gate(i + 1, 1)  # Gates are 1-6, triggers are 0-6
                else:
                    # Trigger went low - set to red
                    self.neopixel_display.set_gate(i + 1, 0)
                
                self.trigger_states[i] = current_state
    
    def _start_reset_timer(self):
        """Start the 50ms timer to reset triggers"""
        self.reset_timer.init(period=50, mode=machine.Timer.ONE_SHOT, 
                             callback=self._reset_triggers_callback)
    
    def _reset_triggers_callback(self, timer):
        """Timer callback to reset all active triggers"""
        with self.thread_lock:
            for i in range(self.num_triggers):
                if self.current_triggers[i]:
                    self.trigger_outputs[i].off()
                    self.current_triggers[i] = False
            
            # Update neopixel colors after reset
            self._update_neopixel_colors()
    
    def start(self):
        """Start the trigger generator thread"""
        if not self.is_running:
            self.is_running = True
            self.trigger_thread = _thread.start_new_thread(self._trigger_thread_function, ())
            print(f"Trigger generator started with {self.num_triggers} outputs")
    
    def stop(self):
        """Stop the trigger generator thread"""
        if self.is_running:
            self.is_running = False
            self.reset_timer.deinit()
            
            # Clear all triggers
            for i in range(self.num_triggers):
                self.trigger_outputs[i].off()
                self.current_triggers[i] = False
            
            # Wait for thread to finish
            time.sleep_ms(100)
            print("Trigger generator stopped")
    
    def clock_tick(self):
        """Called by clock generator on each clock tick"""
        with self.thread_lock:
            self.clock_event = True
    
    def schedule_trigger(self, trigger_num, state=True):
        """
        Schedule a trigger for the next clock event
        
        Args:
            trigger_num: Trigger number (0-6)
            state: True to trigger, False to not trigger
        """
        if 0 <= trigger_num < self.num_triggers:
            self.scheduled_triggers[trigger_num] = state
    
    def schedule_triggers(self, trigger_states):
        """
        Schedule multiple triggers for the next clock event
        
        Args:
            trigger_states: List of trigger states (True/False for each trigger)
        """
        for i, state in enumerate(trigger_states[:self.num_triggers]):
            self.scheduled_triggers[i] = state
    
    def get_trigger_state(self, trigger_num):
        """
        Get current state of a trigger
        
        Args:
            trigger_num: Trigger number (0-6)
            
        Returns:
            Current trigger state (True/False)
        """
        if 0 <= trigger_num < self.num_triggers:
            return self.current_triggers[trigger_num]
        return False
    
    def get_all_trigger_states(self):
        """
        Get all current trigger states
        
        Returns:
            List of current trigger states
        """
        return self.current_triggers.copy()
    
    def get_trigger_statistics(self):
        """
        Get trigger statistics
        
        Returns:
            Dictionary with trigger statistics
        """
        return {
            'trigger_count': self.trigger_count.copy(),
            'last_trigger_time': self.last_trigger_time.copy(),
            'current_states': self.current_triggers.copy(),
            'scheduled_states': self.scheduled_triggers.copy()
        }
    
    def reset_statistics(self):
        """Reset trigger statistics"""
        self.trigger_count = [0] * self.num_triggers
        self.last_trigger_time = [0] * self.num_triggers
    
    def set_trigger_pin(self, trigger_num, pin):
        """
        Change the GPIO pin for a trigger output
        
        Args:
            trigger_num: Trigger number (0-6)
            pin: New GPIO pin number
        """
        if 0 <= trigger_num < self.num_triggers:
            # Turn off old pin
            self.trigger_outputs[trigger_num].off()
            
            # Create new pin
            self.trigger_outputs[trigger_num] = machine.Pin(pin, machine.Pin.OUT)
            self.trigger_pins[trigger_num] = pin
    
    def get_configuration(self):
        """
        Get trigger generator configuration
        
        Returns:
            Dictionary with configuration information
        """
        return {
            'num_triggers': self.num_triggers,
            'trigger_pins': self.trigger_pins.copy(),
            'reset_timer_id': self.reset_timer_id,
            'is_running': self.is_running,
            'reset_period_ms': 50
        }
    
    def test_trigger(self, trigger_num, duration_ms=100):
        """
        Test a specific trigger output
        
        Args:
            trigger_num: Trigger number (0-6)
            duration_ms: Test duration in milliseconds
        """
        if 0 <= trigger_num < self.num_triggers:
            print(f"Testing trigger {trigger_num} for {duration_ms}ms")
            self.trigger_outputs[trigger_num].on()
            time.sleep_ms(duration_ms)
            self.trigger_outputs[trigger_num].off()
            print(f"Trigger {trigger_num} test completed")
    
    def test_all_triggers(self, duration_ms=100):
        """
        Test all trigger outputs sequentially
        
        Args:
            duration_ms: Test duration for each trigger
        """
        print(f"Testing all {self.num_triggers} triggers")
        for i in range(self.num_triggers):
            self.test_trigger(i, duration_ms)
            time.sleep_ms(50)  # Small delay between tests
        print("All trigger tests completed")
