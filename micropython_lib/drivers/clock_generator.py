"""
Clock Generator Library for ESP32-C6 Sequencer Project

This module provides a clock generator that outputs a clock signal controlled by
a potentiometer. The clock rate is adjustable from 5 BPM to 240 BPM, and the
output is currently configured for the user LED on the ESP32-C6. The clock
runs in its own thread and automatically updates its rate based on potentiometer
readings.

Algorithm Overview:
- Initialize clock generator with potentiometer reference
- Create separate thread for clock operation
- Continuously read potentiometer and update clock rate
- Generate clock pulses with configurable pulse width
- Support start/stop/pause functionality
- Provide BPM range scaling (5-240 BPM)
- Handle thread synchronization and cleanup
"""

import machine
import time
import _thread
from potentiometer import Potentiometer

class ClockGenerator:
    def __init__(self, potentiometer, led_pin=15, min_bpm=5, max_bpm=240, pulse_width_ms=50, trigger_generator=None):
        """
        Initialize clock generator
        
        Args:
            potentiometer: Potentiometer object for rate control
            led_pin: Pin number for clock output LED (default: 15 for GPIO15)
            min_bpm: Minimum BPM rate (default: 5)
            max_bpm: Maximum BPM rate (default: 240)
            pulse_width_ms: Clock pulse width in milliseconds (default: 50)
            trigger_generator: TriggerGenerator object for gate events (optional)
        """
        self.potentiometer = potentiometer
        self.led_pin = led_pin
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.pulse_width_ms = pulse_width_ms
        self.trigger_generator = trigger_generator
        
        # Initialize LED
        self.led = machine.Pin(led_pin, machine.Pin.OUT)
        self.led.off()
        
        # Clock state for LED toggling
        self.led_state = False
        
        # Clock state
        self.is_running = False
        self.is_paused = False
        self.current_bpm = min_bpm
        self.clock_thread = None
        self.thread_lock = _thread.allocate_lock()
        
        # Timing calculations
        self._update_timing()
        
    def _update_timing(self):
        """Update timing calculations based on current BPM"""
        # Convert BPM to period in milliseconds
        # BPM = beats per minute = beats per 60 seconds
        # Period = 60 seconds / BPM * 1000 ms
        self.period_ms = int((60.0 / self.current_bpm) * 1000)
        
        # Calculate sleep time (period minus pulse width)
        self.sleep_time_ms = max(10, self.period_ms - self.pulse_width_ms)
        
    def _clock_thread_function(self):
        """Main clock thread function"""
        while self.is_running:
            with self.thread_lock:
                if not self.is_paused:
                    # Toggle LED state
                    self.led_state = not self.led_state
                    if self.led_state:
                        self.led.on()
                    else:
                        self.led.off()
                    
                    # Call trigger generator on each clock tick
                    if self.trigger_generator:
                        self.trigger_generator.clock_tick()
                    
                    # Sleep for the full period (LED stays in current state)
                    time.sleep_ms(self.period_ms)
                else:
                    # If paused, just sleep briefly
                    time.sleep_ms(10)
            
            # Update BPM from potentiometer (outside lock to avoid blocking)
            self._update_bpm_from_potentiometer()
    
    def _update_bpm_from_potentiometer(self):
        """Update BPM based on potentiometer reading"""
        try:
            # Read potentiometer as percentage (0-100)
            percentage = self.potentiometer.read_percentage()
            
            # Scale percentage to BPM range
            new_bpm = self.min_bpm + (percentage / 100.0) * (self.max_bpm - self.min_bpm)
            
            # Only update if BPM changed significantly (avoid constant updates)
            if abs(new_bpm - self.current_bpm) > 0.5:
                with self.thread_lock:
                    self.current_bpm = new_bpm
                    self._update_timing()
        except Exception as e:
            # If potentiometer read fails, keep current BPM
            pass
    
    def start(self):
        """Start the clock generator"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.clock_thread = _thread.start_new_thread(self._clock_thread_function, ())
            print(f"Clock started at {self.current_bpm:.1f} BPM")
    
    def stop(self):
        """Stop the clock generator"""
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self.led.off()
            # Wait a bit for thread to finish
            time.sleep_ms(100)
            print("Clock stopped")
    
    def pause(self):
        """Pause the clock generator"""
        if self.is_running and not self.is_paused:
            with self.thread_lock:
                self.is_paused = True
            self.led.off()
            print("Clock paused")
    
    def resume(self):
        """Resume the clock generator"""
        if self.is_running and self.is_paused:
            with self.thread_lock:
                self.is_paused = False
            print(f"Clock resumed at {self.current_bpm:.1f} BPM")
    
    def set_bpm(self, bpm):
        """
        Manually set BPM (will be overridden by potentiometer)
        
        Args:
            bpm: BPM value to set
        """
        bpm = max(self.min_bpm, min(self.max_bpm, bpm))
        with self.thread_lock:
            self.current_bpm = bpm
            self._update_timing()
        print(f"BPM set to {self.current_bpm:.1f}")
    
    def get_bpm(self):
        """
        Get current BPM
        
        Returns:
            Current BPM value
        """
        return self.current_bpm
    
    def set_trigger_generator(self, trigger_generator):
        """
        Set the trigger generator for this clock
        
        Args:
            trigger_generator: TriggerGenerator object
        """
        self.trigger_generator = trigger_generator
        print("Trigger generator connected to clock")
    
    def get_status(self):
        """
        Get clock status information
        
        Returns:
            Dictionary with status information
        """
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_bpm': self.current_bpm,
            'period_ms': self.period_ms,
            'pulse_width_ms': self.pulse_width_ms,
            'min_bpm': self.min_bpm,
            'max_bpm': self.max_bpm,
            'led_pin': self.led_pin,
            'led_state': self.led_state,
            'has_trigger_generator': self.trigger_generator is not None
        }
    
    def set_pulse_width(self, width_ms):
        """
        Set clock pulse width
        
        Args:
            width_ms: Pulse width in milliseconds
        """
        self.pulse_width_ms = max(10, min(1000, width_ms))
        self._update_timing()
        print(f"Pulse width set to {self.pulse_width_ms}ms")
    
    def set_bpm_range(self, min_bpm, max_bpm):
        """
        Set BPM range
        
        Args:
            min_bpm: Minimum BPM
            max_bpm: Maximum BPM
        """
        self.min_bpm = max(1, min_bpm)
        self.max_bpm = max(self.min_bpm + 1, max_bpm)
        
        # Clamp current BPM to new range
        if self.current_bpm < self.min_bpm:
            self.current_bpm = self.min_bpm
        elif self.current_bpm > self.max_bpm:
            self.current_bpm = self.max_bpm
        
        self._update_timing()
        print(f"BPM range set to {self.min_bpm}-{self.max_bpm}")
    
    def force_bpm_update(self):
        """Force BPM update from potentiometer"""
        self._update_bpm_from_potentiometer()
        print(f"BPM updated to {self.current_bpm:.1f}")
    
    def cleanup(self):
        """Clean up resources and stop clock"""
        self.stop()
        self.led.off()
        print("Clock generator cleaned up")
