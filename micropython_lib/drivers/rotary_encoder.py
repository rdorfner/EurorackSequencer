"""
Rotary Encoder Library for ESP32-C6 Sequencer Project

This module provides an interface for reading rotary encoders with push button
functionality. The encoder uses two pins for quadrature encoding and a third
pin for the push button. All inputs are pulled high with resistors, so the
button generates a low-going signal when pressed.

Algorithm Overview:
- Initialize encoder pins with pull-up resistors
- Implement quadrature decoding for rotation detection
- Handle push button with debouncing
- Provide callback support for rotation and button events
- Support both polling and interrupt-driven operation
- Implement proper debouncing for reliable operation
"""

import machine
import time

class RotaryEncoder:
    def __init__(self, pin_a, pin_b, pin_button, pull_up=True):
        """
        Initialize rotary encoder
        
        Args:
            pin_a: Pin number for encoder A (quadrature signal)
            pin_b: Pin number for encoder B (quadrature signal)
            pin_button: Pin number for push button
            pull_up: Enable internal pull-up resistors (default: True)
        """
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_button = pin_button
        
        # Initialize encoder pins
        if pull_up:
            self.encoder_a = machine.Pin(pin_a, machine.Pin.IN, machine.Pin.PULL_UP)
            self.encoder_b = machine.Pin(pin_b, machine.Pin.IN, machine.Pin.PULL_UP)
            self.button = machine.Pin(pin_button, machine.Pin.IN, machine.Pin.PULL_UP)
        else:
            self.encoder_a = machine.Pin(pin_a, machine.Pin.IN)
            self.encoder_b = machine.Pin(pin_b, machine.Pin.IN)
            self.button = machine.Pin(pin_button, machine.Pin.IN)
        
        # Encoder state
        self.last_state_a = self.encoder_a.value()
        self.last_state_b = self.encoder_b.value()
        self.position = 0
        self.direction = 0  # 1 for CW, -1 for CCW
        
        # Button state
        self.button_pressed = False
        self.button_released = False
        self.last_button_state = self.button.value()
        self.button_debounce_time = 0
        self.button_debounce_delay = 50  # 50ms debounce delay
        
        # Callbacks
        self.rotation_callback = None
        self.button_callback = None
        
        # Timing for debouncing
        self.last_update_time = time.ticks_ms()
        
    def update(self):
        """
        Update encoder state - call this regularly or from interrupt
        """
        current_time = time.ticks_ms()
        
        # Read current encoder states
        state_a = self.encoder_a.value()
        state_b = self.encoder_b.value()
        
        # Check for encoder rotation
        if state_a != self.last_state_a or state_b != self.last_state_b:
            # Determine direction based on quadrature
            if state_a != self.last_state_a:
                if state_a == state_b:
                    self.direction = 1  # Clockwise
                    self.position += 1
                else:
                    self.direction = -1  # Counter-clockwise
                    self.position -= 1
                
                # Call rotation callback if set
                if self.rotation_callback:
                    self.rotation_callback(self.direction, self.position)
            
            self.last_state_a = state_a
            self.last_state_b = state_b
        
        # Check button state
        current_button_state = self.button.value()
        
        # Button is pressed when it goes low (pulled high normally)
        if current_button_state == 0 and self.last_button_state == 1:
            # Button just pressed
            if time.ticks_diff(current_time, self.button_debounce_time) > self.button_debounce_delay:
                self.button_pressed = True
                self.button_debounce_time = current_time
                
                # Call button callback if set
                if self.button_callback:
                    self.button_callback(True)  # True = pressed
        
        elif current_button_state == 1 and self.last_button_state == 0:
            # Button just released
            if time.ticks_diff(current_time, self.button_debounce_time) > self.button_debounce_delay:
                self.button_released = True
                self.button_debounce_time = current_time
                
                # Call button callback if set
                if self.button_callback:
                    self.button_callback(False)  # False = released
        
        self.last_button_state = current_button_state
    
    def get_position(self):
        """
        Get current encoder position
        
        Returns:
            Current position value
        """
        return self.position
    
    def get_direction(self):
        """
        Get last rotation direction
        
        Returns:
            Direction (1 for CW, -1 for CCW, 0 for no rotation)
        """
        return self.direction
    
    def reset_position(self, position=0):
        """
        Reset encoder position
        
        Args:
            position: New position value (default: 0)
        """
        self.position = position
        self.direction = 0
    
    def is_button_pressed(self):
        """
        Check if button is currently pressed
        
        Returns:
            True if button is pressed, False otherwise
        """
        return self.button.value() == 0
    
    def was_button_pressed(self):
        """
        Check if button was pressed since last call
        
        Returns:
            True if button was pressed, False otherwise
        """
        if self.button_pressed:
            self.button_pressed = False
            return True
        return False
    
    def was_button_released(self):
        """
        Check if button was released since last call
        
        Returns:
            True if button was released, False otherwise
        """
        if self.button_released:
            self.button_released = False
            return True
        return False
    
    def set_rotation_callback(self, callback):
        """
        Set callback function for rotation events
        
        Args:
            callback: Function to call on rotation (direction, position)
        """
        self.rotation_callback = callback
    
    def set_button_callback(self, callback):
        """
        Set callback function for button events
        
        Args:
            callback: Function to call on button press/release (pressed)
        """
        self.button_callback = callback
    
    def set_debounce_delay(self, delay_ms):
        """
        Set button debounce delay
        
        Args:
            delay_ms: Debounce delay in milliseconds
        """
        self.button_debounce_delay = delay_ms
    
    def get_status(self):
        """
        Get encoder status information
        
        Returns:
            Dictionary with status information
        """
        return {
            'position': self.position,
            'direction': self.direction,
            'button_pressed': self.is_button_pressed(),
            'button_was_pressed': self.button_pressed,
            'button_was_released': self.button_released,
            'pin_a': self.pin_a,
            'pin_b': self.pin_b,
            'pin_button': self.pin_button,
            'debounce_delay': self.button_debounce_delay
        }
    
    def poll(self, duration_ms=1000):
        """
        Poll encoder for a specified duration
        
        Args:
            duration_ms: Duration to poll in milliseconds
        """
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
            self.update()
            time.sleep_ms(10)  # Small delay to prevent excessive CPU usage
    
    def wait_for_rotation(self, timeout_ms=5000):
        """
        Wait for encoder rotation
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            True if rotation detected, False if timeout
        """
        start_time = time.ticks_ms()
        initial_position = self.position
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            self.update()
            if self.position != initial_position:
                return True
            time.sleep_ms(10)
        
        return False
    
    def wait_for_button_press(self, timeout_ms=5000):
        """
        Wait for button press
        
        Args:
            timeout_ms: Timeout in milliseconds
            
        Returns:
            True if button pressed, False if timeout
        """
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            self.update()
            if self.was_button_pressed():
                return True
            time.sleep_ms(10)
        
        return False
