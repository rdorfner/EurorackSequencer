"""
Low-Power Core Clock Generator for ESP32-C6 Sequencer Project

This module provides clock generation functionality optimized for the low-power core
of the ESP32-C6. It handles internal clock generation, external clock input detection,
and inter-core communication for clock events.

Algorithm Overview:
- Run on low-power core for efficient power consumption
- Support both internal and external clock sources
- External clock input with frequency detection and override
- Inter-core communication for clock events
- Precise timing using hardware timers
- Automatic switching between internal and external clocks
"""

import machine
import time
import _thread
from intercore_communication import InterCoreCommunication, CMD_CLOCK_UPDATE, CMD_EXTERNAL_CLOCK, RESP_CLOCK_TICK

class LowPowerClockGenerator:
    def __init__(self, intercore_comm, led_pin=15, min_bpm=5, max_bpm=240):
        """
        Initialize low-power clock generator
        
        Args:
            intercore_comm: InterCoreCommunication object
            led_pin: Pin number for clock output LED (default: 15)
            min_bpm: Minimum BPM rate (default: 5)
            max_bpm: Maximum BPM rate (default: 240)
        """
        self.intercore_comm = intercore_comm
        self.led_pin = led_pin
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        
        # Initialize LED
        self.led = machine.Pin(led_pin, machine.Pin.OUT)
        self.led.off()
        
        # Clock state
        self.current_bpm = min_bpm
        self.clock_source = 'internal'  # 'internal' or 'external'
        self.led_state = False
        
        # Timing
        self.period_ms = int((60.0 / self.current_bpm) * 1000)
        self.last_clock_time = 0
        
        # External clock detection
        self.external_clock_active = False
        self.external_clock_frequency = 0.0
        self.external_clock_last_tick = 0
        self.external_clock_timeout_ms = 2000  # 2 second timeout
        
        # Thread management
        self.clock_thread = None
        self.thread_lock = _thread.allocate_lock()
        self.is_running = False
        
        # Timer for internal clock
        self.clock_timer = machine.Timer(0)
        
        # Message processing
        self.message_queue = []
        
    def _update_timing(self):
        """Update timing calculations based on current BPM"""
        if self.clock_source == 'internal':
            self.period_ms = int((60.0 / self.current_bpm) * 1000)
        else:
            # External clock - use detected frequency
            self.period_ms = int((60.0 / self.external_clock_frequency) * 1000)
    
    def _clock_timer_callback(self, timer):
        """Timer callback for internal clock generation"""
        if self.clock_source == 'internal':
            self._generate_clock_tick()
    
    def _generate_clock_tick(self):
        """Generate a clock tick event"""
        current_time = time.ticks_ms()
        
        # Toggle LED
        self.led_state = not self.led_state
        if self.led_state:
            self.led.on()
        else:
            self.led.off()
        
        # Send clock tick to high-performance core
        self.intercore_comm._send_to_hp_core({
            'type': RESP_CLOCK_TICK,
            'timestamp': current_time,
            'source': self.clock_source,
            'bpm': self.current_bpm if self.clock_source == 'internal' else self.external_clock_frequency
        })
        
        self.last_clock_time = current_time
        print(f"Clock tick: {self.current_bpm if self.clock_source == 'internal' else self.external_clock_frequency:.1f} BPM")
    
    def _external_clock_interrupt(self, pin):
        """Handle external clock input interrupt"""
        current_time = time.ticks_ms()
        
        # Calculate frequency
        if self.external_clock_last_tick > 0:
            period_ms = time.ticks_diff(current_time, self.external_clock_last_tick)
            if period_ms > 0:
                self.external_clock_frequency = 60000.0 / period_ms
        
        self.external_clock_last_tick = current_time
        self.external_clock_active = True
        
        # Switch to external clock if not already
        if self.clock_source != 'external':
            self._switch_to_external_clock()
        
        # Generate clock tick
        self._generate_clock_tick()
    
    def _switch_to_external_clock(self):
        """Switch to external clock source"""
        print(f"Switching to external clock: {self.external_clock_frequency:.1f} BPM")
        self.clock_source = 'external'
        self._stop_internal_clock()
        self._update_timing()
    
    def _switch_to_internal_clock(self):
        """Switch to internal clock source"""
        print(f"Switching to internal clock: {self.current_bpm:.1f} BPM")
        self.clock_source = 'internal'
        self._start_internal_clock()
        self._update_timing()
    
    def _start_internal_clock(self):
        """Start internal clock timer"""
        if self.clock_source == 'internal':
            self.clock_timer.init(
                period=self.period_ms,
                mode=machine.Timer.PERIODIC,
                callback=self._clock_timer_callback
            )
    
    def _stop_internal_clock(self):
        """Stop internal clock timer"""
        self.clock_timer.deinit()
    
    def _check_external_clock_timeout(self):
        """Check if external clock has timed out"""
        if self.clock_source == 'external':
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.external_clock_last_tick) > self.external_clock_timeout_ms:
                print("External clock timeout - switching to internal clock")
                self.external_clock_active = False
                self._switch_to_internal_clock()
    
    def _process_messages(self):
        """Process messages from high-performance core"""
        # This would normally process messages from the inter-core communication
        # For now, we'll simulate message processing
        pass
    
    def _clock_thread_function(self):
        """Main clock thread function for low-power core"""
        while self.is_running:
            with self.thread_lock:
                # Process messages from high-performance core
                self._process_messages()
                
                # Check external clock timeout
                self._check_external_clock_timeout()
                
                # Small delay to prevent excessive CPU usage
                time.sleep_ms(10)
    
    def start(self):
        """Start the low-power clock generator"""
        if not self.is_running:
            self.is_running = True
            
            # Start with internal clock
            self._start_internal_clock()
            
            # Start thread
            self.clock_thread = _thread.start_new_thread(self._clock_thread_function, ())
            
            print(f"Low-power clock generator started: {self.current_bpm:.1f} BPM")
    
    def stop(self):
        """Stop the low-power clock generator"""
        if self.is_running:
            self.is_running = False
            
            # Stop internal clock
            self._stop_internal_clock()
            
            # Turn off LED
            self.led.off()
            
            # Wait for thread to finish
            time.sleep_ms(100)
            
            print("Low-power clock generator stopped")
    
    def set_bpm(self, bpm):
        """
        Set BPM for internal clock
        
        Args:
            bpm: BPM value
        """
        bpm = max(self.min_bpm, min(self.max_bpm, bpm))
        
        with self.thread_lock:
            self.current_bpm = bpm
            
            if self.clock_source == 'internal':
                self._update_timing()
                self._start_internal_clock()  # Restart with new timing
        
        print(f"BPM set to {self.current_bpm:.1f}")
    
    def setup_external_clock_input(self, pin):
        """
        Setup external clock input
        
        Args:
            pin: GPIO pin for external clock input
        """
        self.external_clock_pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.external_clock_pin.irq(
            trigger=machine.Pin.IRQ_RISING,
            handler=self._external_clock_interrupt
        )
        
        print(f"External clock input configured on pin {pin}")
    
    def get_status(self):
        """
        Get clock generator status
        
        Returns:
            Dictionary with status information
        """
        return {
            'is_running': self.is_running,
            'current_bpm': self.current_bpm,
            'clock_source': self.clock_source,
            'external_clock_active': self.external_clock_active,
            'external_clock_frequency': self.external_clock_frequency,
            'period_ms': self.period_ms,
            'led_state': self.led_state,
            'led_pin': self.led_pin
        }
    
    def force_internal_clock(self):
        """Force switch to internal clock (override external)"""
        self._switch_to_internal_clock()
        print("Forced switch to internal clock")
    
    def enable_external_clock(self):
        """Enable external clock detection"""
        if self.external_clock_pin:
            self.external_clock_pin.irq(
                trigger=machine.Pin.IRQ_RISING,
                handler=self._external_clock_interrupt
            )
            print("External clock detection enabled")
    
    def disable_external_clock(self):
        """Disable external clock detection"""
        if self.external_clock_pin:
            self.external_clock_pin.irq(handler=None)
            print("External clock detection disabled")
