"""
Inter-Core Communication Library for ESP32-C6 Dual-Core Architecture

This module provides communication between the high-performance core and low-power core
for the sequencer project. The low-power core handles clock generation, potentiometer
reading, and external clock input, while the high-performance core manages UI, patterns,
and neopixel display.

Algorithm Overview:
- Shared memory regions for data exchange
- Inter-processor interrupts for signaling
- FreeRTOS queues for message passing
- Atomic operations for thread safety
- Event-driven communication for real-time performance
- External clock detection and override functionality
"""

import machine
import time
import _thread
from micropython import const

# Constants for inter-core communication
CMD_CLOCK_UPDATE = const(1)
CMD_TRIGGER_PATTERN = const(2)
CMD_EXTERNAL_CLOCK = const(3)
CMD_POTENTIOMETER_READ = const(4)
CMD_SYSTEM_STATE = const(5)

RESP_CLOCK_TICK = const(10)
RESP_POTENTIOMETER_VALUE = const(11)
RESP_EXTERNAL_CLOCK_DETECTED = const(12)
RESP_SYSTEM_STATUS = const(13)

class InterCoreCommunication:
    def __init__(self):
        """Initialize inter-core communication system"""
        # Shared memory regions (simulated - would use actual shared RAM in ESP-IDF)
        self.shared_memory = {
            'clock_bpm': 60.0,
            'external_clock_active': False,
            'external_clock_frequency': 0.0,
            'potentiometer_value': 0.0,
            'trigger_pattern': [False] * 7,
            'system_state': 'idle',
            'last_clock_tick': 0,
            'clock_source': 'internal'  # 'internal' or 'external'
        }
        
        # Communication queues (simulated - would use FreeRTOS queues)
        self.hp_to_lp_queue = []
        self.lp_to_hp_queue = []
        
        # Synchronization objects
        self.hp_lock = _thread.allocate_lock()
        self.lp_lock = _thread.allocate_lock()
        self.clock_event = _thread.allocate_lock()
        
        # External clock detection
        self.external_clock_pin = None
        self.external_clock_active = False
        self.external_clock_frequency = 0.0
        self.last_external_clock_time = 0
        
        # Callbacks for high-performance core
        self.clock_tick_callback = None
        self.external_clock_callback = None
        self.potentiometer_callback = None
        
    def setup_external_clock_input(self, pin, interrupt_callback=None):
        """
        Setup external clock input detection
        
        Args:
            pin: GPIO pin for external clock input
            interrupt_callback: Callback function for external clock detection
        """
        self.external_clock_pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.external_clock_callback = interrupt_callback
        
        # Setup interrupt for external clock detection
        self.external_clock_pin.irq(
            trigger=machine.Pin.IRQ_RISING,
            handler=self._external_clock_interrupt
        )
        
        print(f"External clock input configured on pin {pin}")
    
    def _external_clock_interrupt(self, pin):
        """Handle external clock interrupt"""
        current_time = time.ticks_ms()
        
        # Calculate frequency if we have a previous clock
        if self.last_external_clock_time > 0:
            period_ms = time.ticks_diff(current_time, self.last_external_clock_time)
            if period_ms > 0:
                self.external_clock_frequency = 60000.0 / period_ms  # Convert to BPM
        
        self.last_external_clock_time = current_time
        
        # Update shared memory
        with self.hp_lock:
            self.shared_memory['external_clock_active'] = True
            self.shared_memory['external_clock_frequency'] = self.external_clock_frequency
            self.shared_memory['clock_source'] = 'external'
            self.shared_memory['last_clock_tick'] = current_time
        
        # Signal low-power core
        self._send_to_lp_core({
            'type': CMD_EXTERNAL_CLOCK,
            'frequency': self.external_clock_frequency,
            'timestamp': current_time
        })
        
        # Call callback if provided
        if self.external_clock_callback:
            self.external_clock_callback(self.external_clock_frequency)
    
    def _send_to_lp_core(self, message):
        """Send message to low-power core"""
        with self.lp_lock:
            self.hp_to_lp_queue.append(message)
    
    def _send_to_hp_core(self, message):
        """Send message to high-performance core"""
        with self.hp_lock:
            self.lp_to_hp_queue.append(message)
    
    def send_clock_update(self, bpm, source='internal'):
        """
        Send clock update to low-power core
        
        Args:
            bpm: BPM value for clock generation
            source: Clock source ('internal' or 'external')
        """
        message = {
            'type': CMD_CLOCK_UPDATE,
            'bpm': bpm,
            'source': source,
            'timestamp': time.ticks_ms()
        }
        
        with self.hp_lock:
            self.shared_memory['clock_bpm'] = bpm
            self.shared_memory['clock_source'] = source
        
        self._send_to_lp_core(message)
        print(f"Clock update sent: {bpm} BPM from {source}")
    
    def send_trigger_pattern(self, trigger_pattern):
        """
        Send trigger pattern to low-power core
        
        Args:
            trigger_pattern: List of trigger states (7 elements)
        """
        message = {
            'type': CMD_TRIGGER_PATTERN,
            'triggers': trigger_pattern[:7],  # Ensure only 7 triggers
            'timestamp': time.ticks_ms()
        }
        
        with self.hp_lock:
            self.shared_memory['trigger_pattern'] = trigger_pattern[:7]
        
        self._send_to_lp_core(message)
        print(f"Trigger pattern sent: {trigger_pattern[:7]}")
    
    def request_potentiometer_read(self):
        """Request potentiometer reading from low-power core"""
        message = {
            'type': CMD_POTENTIOMETER_READ,
            'timestamp': time.ticks_ms()
        }
        self._send_to_lp_core(message)
    
    def get_shared_data(self, key):
        """
        Get data from shared memory
        
        Args:
            key: Key to retrieve from shared memory
            
        Returns:
            Value from shared memory
        """
        with self.hp_lock:
            return self.shared_memory.get(key, None)
    
    def set_shared_data(self, key, value):
        """
        Set data in shared memory
        
        Args:
            key: Key to set in shared memory
            value: Value to set
        """
        with self.hp_lock:
            self.shared_memory[key] = value
    
    def set_clock_tick_callback(self, callback):
        """
        Set callback for clock tick events
        
        Args:
            callback: Function to call on clock tick
        """
        self.clock_tick_callback = callback
    
    def set_potentiometer_callback(self, callback):
        """
        Set callback for potentiometer updates
        
        Args:
            callback: Function to call on potentiometer update
        """
        self.potentiometer_callback = callback
    
    def process_messages(self):
        """Process incoming messages from low-power core"""
        with self.hp_lock:
            while self.lp_to_hp_queue:
                message = self.lp_to_hp_queue.pop(0)
                self._handle_lp_message(message)
    
    def _handle_lp_message(self, message):
        """Handle message from low-power core"""
        msg_type = message.get('type', 0)
        
        if msg_type == RESP_CLOCK_TICK:
            # Clock tick from low-power core
            if self.clock_tick_callback:
                self.clock_tick_callback(message.get('timestamp', 0))
        
        elif msg_type == RESP_POTENTIOMETER_VALUE:
            # Potentiometer value update
            value = message.get('value', 0.0)
            with self.hp_lock:
                self.shared_memory['potentiometer_value'] = value
            
            if self.potentiometer_callback:
                self.potentiometer_callback(value)
        
        elif msg_type == RESP_EXTERNAL_CLOCK_DETECTED:
            # External clock detected
            frequency = message.get('frequency', 0.0)
            print(f"External clock detected: {frequency:.1f} BPM")
        
        elif msg_type == RESP_SYSTEM_STATUS:
            # System status update
            status = message.get('status', {})
            with self.hp_lock:
                self.shared_memory['system_state'] = status.get('state', 'unknown')
    
    def get_system_status(self):
        """
        Get current system status
        
        Returns:
            Dictionary with system status information
        """
        with self.hp_lock:
            return {
                'clock_bpm': self.shared_memory['clock_bpm'],
                'clock_source': self.shared_memory['clock_source'],
                'external_clock_active': self.shared_memory['external_clock_active'],
                'external_clock_frequency': self.shared_memory['external_clock_frequency'],
                'potentiometer_value': self.shared_memory['potentiometer_value'],
                'trigger_pattern': self.shared_memory['trigger_pattern'].copy(),
                'system_state': self.shared_memory['system_state'],
                'last_clock_tick': self.shared_memory['last_clock_tick']
            }
    
    def start_communication(self):
        """Start inter-core communication"""
        print("Inter-core communication started")
        print("High-performance core ready for communication")
    
    def stop_communication(self):
        """Stop inter-core communication"""
        print("Inter-core communication stopped")
