"""
High-Performance Core Trigger Generator for ESP32-C6 Sequencer Project

This module provides trigger generation functionality optimized for the high-performance core
of the ESP32-C6. It manages trigger patterns, neopixel feedback, and communicates with the
low-power core for clock events and trigger execution.

Algorithm Overview:
- Run on high-performance core for UI and pattern management
- Receive clock events from low-power core via inter-core communication
- Manage trigger patterns and scheduling
- Update neopixel display for visual feedback
- Coordinate with low-power core for trigger execution
- Handle trigger statistics and configuration
"""

import machine
import time
import _thread
from neopixel_display import NeopixelDisplay, RED, GREEN
from intercore_communication import InterCoreCommunication, CMD_TRIGGER_PATTERN, RESP_CLOCK_TICK

class HighPerformanceTriggerGenerator:
    def __init__(self, intercore_comm, neopixel_display, trigger_pins=None):
        """
        Initialize high-performance trigger generator
        
        Args:
            intercore_comm: InterCoreCommunication object
            neopixel_display: NeopixelDisplay object for visual feedback
            trigger_pins: List of GPIO pins for trigger outputs (default: pins 3-9)
        """
        self.intercore_comm = intercore_comm
        self.neopixel_display = neopixel_display
        
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
        
        # Trigger state management
        self.current_triggers = [False] * self.num_triggers
        self.scheduled_triggers = [False] * self.num_triggers
        self.trigger_states = [False] * self.num_triggers  # Previous states for neopixel updates
        
        # Pattern management
        self.trigger_patterns = []
        self.current_pattern_index = 0
        self.pattern_length = 16  # Default pattern length
        self.pattern_enabled = False
        
        # Thread management
        self.trigger_thread = None
        self.thread_lock = _thread.allocate_lock()
        self.is_running = False
        
        # Statistics
        self.trigger_count = [0] * self.num_triggers
        self.last_trigger_time = [0] * self.num_triggers
        self.clock_tick_count = 0
        
        # Setup inter-core communication callbacks
        self.intercore_comm.set_clock_tick_callback(self._on_clock_tick)
        
    def _on_clock_tick(self, timestamp):
        """Handle clock tick from low-power core"""
        self.clock_tick_count += 1
        
        # Process current trigger pattern
        if self.pattern_enabled and self.trigger_patterns:
            self._process_pattern_step()
        
        # Generate triggers for scheduled triggers
        self._generate_triggers()
        
        # Update neopixel colors
        self._update_neopixel_colors()
        
        # Schedule next pattern step
        self._advance_pattern()
    
    def _process_pattern_step(self):
        """Process current step in trigger pattern"""
        if self.current_pattern_index < len(self.trigger_patterns):
            pattern_step = self.trigger_patterns[self.current_pattern_index]
            
            # Schedule triggers based on pattern
            for i, trigger_state in enumerate(pattern_step[:self.num_triggers]):
                self.scheduled_triggers[i] = trigger_state
    
    def _generate_triggers(self):
        """Generate triggers for scheduled triggers"""
        for i in range(self.num_triggers):
            if self.scheduled_triggers[i]:
                self.trigger_outputs[i].on()
                self.current_triggers[i] = True
                self.trigger_count[i] += 1
                self.last_trigger_time[i] = time.ticks_ms()
    
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
    
    def _advance_pattern(self):
        """Advance to next step in pattern"""
        if self.pattern_enabled and self.trigger_patterns:
            self.current_pattern_index = (self.current_pattern_index + 1) % len(self.trigger_patterns)
    
    def _trigger_thread_function(self):
        """Main trigger thread function for high-performance core"""
        while self.is_running:
            with self.thread_lock:
                # Process inter-core messages
                self.intercore_comm.process_messages()
                
                # Small delay to prevent excessive CPU usage
                time.sleep_ms(10)
    
    def start(self):
        """Start the high-performance trigger generator"""
        if not self.is_running:
            self.is_running = True
            
            # Start thread
            self.trigger_thread = _thread.start_new_thread(self._trigger_thread_function, ())
            
            print(f"High-performance trigger generator started with {self.num_triggers} outputs")
    
    def stop(self):
        """Stop the high-performance trigger generator"""
        if self.is_running:
            self.is_running = False
            
            # Clear all triggers
            for i in range(self.num_triggers):
                self.trigger_outputs[i].off()
                self.current_triggers[i] = False
            
            # Wait for thread to finish
            time.sleep_ms(100)
            
            print("High-performance trigger generator stopped")
    
    def set_trigger_pattern(self, pattern):
        """
        Set trigger pattern
        
        Args:
            pattern: List of pattern steps, each step is a list of trigger states
        """
        self.trigger_patterns = pattern
        self.current_pattern_index = 0
        self.pattern_length = len(pattern)
        print(f"Trigger pattern set: {self.pattern_length} steps")
    
    def enable_pattern(self, enabled=True):
        """
        Enable or disable pattern playback
        
        Args:
            enabled: True to enable pattern, False to disable
        """
        self.pattern_enabled = enabled
        if enabled:
            print("Trigger pattern enabled")
        else:
            print("Trigger pattern disabled")
    
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
            'scheduled_states': self.scheduled_triggers.copy(),
            'clock_tick_count': self.clock_tick_count,
            'pattern_enabled': self.pattern_enabled,
            'current_pattern_index': self.current_pattern_index,
            'pattern_length': self.pattern_length
        }
    
    def reset_statistics(self):
        """Reset trigger statistics"""
        self.trigger_count = [0] * self.num_triggers
        self.last_trigger_time = [0] * self.num_triggers
        self.clock_tick_count = 0
    
    def create_simple_pattern(self, pattern_string):
        """
        Create a simple trigger pattern from a string
        
        Args:
            pattern_string: String representation of pattern (e.g., "1001001001001001")
        """
        pattern = []
        for char in pattern_string:
            if char == '1':
                pattern.append([True] * self.num_triggers)
            else:
                pattern.append([False] * self.num_triggers)
        
        self.set_trigger_pattern(pattern)
        print(f"Simple pattern created: {pattern_string}")
    
    def create_alternating_pattern(self, trigger_num, length=16):
        """
        Create an alternating pattern for a specific trigger
        
        Args:
            trigger_num: Trigger number (0-6)
            length: Pattern length
        """
        pattern = []
        for i in range(length):
            step = [False] * self.num_triggers
            if i % 2 == 0:  # Even steps
                step[trigger_num] = True
            pattern.append(step)
        
        self.set_trigger_pattern(pattern)
        print(f"Alternating pattern created for trigger {trigger_num}")
    
    def get_configuration(self):
        """
        Get trigger generator configuration
        
        Returns:
            Dictionary with configuration information
        """
        return {
            'num_triggers': self.num_triggers,
            'trigger_pins': self.trigger_pins.copy(),
            'is_running': self.is_running,
            'pattern_enabled': self.pattern_enabled,
            'pattern_length': self.pattern_length,
            'current_pattern_index': self.current_pattern_index
        }
