"""
Low-Power Core Potentiometer Library for ESP32-C6 Sequencer Project

This module provides potentiometer reading functionality optimized for the low-power core
of the ESP32-C6. It includes decimation for averaging, efficient ADC sampling, and
inter-core communication for potentiometer value updates.

Algorithm Overview:
- Run on low-power core for efficient power consumption
- Decimation and averaging for noise reduction
- Configurable sampling rates and averaging windows
- Inter-core communication for value updates
- Automatic BPM calculation and scaling
- Efficient ADC usage with minimal power consumption
"""

import machine
import time
import _thread
from intercore_communication import InterCoreCommunication, CMD_POTENTIOMETER_READ, RESP_POTENTIOMETER_VALUE

class LowPowerPotentiometer:
    def __init__(self, intercore_comm, pin=1, resolution=12, decimation_factor=8, averaging_samples=16):
        """
        Initialize low-power potentiometer
        
        Args:
            intercore_comm: InterCoreCommunication object
            pin: ADC pin number (default: 1)
            resolution: ADC resolution in bits (default: 12)
            decimation_factor: Decimation factor for sampling (default: 8)
            averaging_samples: Number of samples for averaging (default: 16)
        """
        self.intercore_comm = intercore_comm
        self.pin = pin
        self.resolution = resolution
        self.decimation_factor = decimation_factor
        self.averaging_samples = averaging_samples
        self.max_value = (2 ** resolution) - 1
        
        # Initialize ADC
        self.adc = machine.ADC(machine.Pin(pin))
        self.adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution
        
        # Decimation and averaging
        self.sample_buffer = []
        self.decimation_counter = 0
        self.current_average = 0.0
        self.last_sent_value = 0.0
        
        # BPM scaling
        self.min_bpm = 15.0
        self.max_bpm = 200.0
        
        # Potentiometer range compensation (based on observed limits)
        self.observed_min_raw = 0
        self.observed_max_raw = 3311
        self.observed_range = self.observed_max_raw - self.observed_min_raw
        self.scale_factor = 4095.0 / self.observed_range
        
        # Thread management
        self.sampling_thread = None
        self.thread_lock = _thread.allocate_lock()
        self.is_running = False
        
        # Sampling control
        self.sampling_interval_ms = 50  # 20 Hz sampling rate
        self.value_change_threshold = 0.01  # 1% change threshold
        
        # Statistics
        self.sample_count = 0
        self.last_sample_time = 0
        
    def _read_adc_sample(self):
        """Read a single ADC sample"""
        return self.adc.read()
    
    def _decimate_sample(self, sample):
        """
        Apply decimation to reduce sampling rate
        
        Args:
            sample: Raw ADC sample
            
        Returns:
            Decimated sample or None if not ready
        """
        self.decimation_counter += 1
        
        if self.decimation_counter >= self.decimation_factor:
            self.decimation_counter = 0
            return sample
        
        return None
    
    def _update_average(self, sample):
        """
        Update running average with new sample
        
        Args:
            sample: ADC sample to add to average
        """
        # Add sample to buffer
        self.sample_buffer.append(sample)
        
        # Keep only the last N samples
        if len(self.sample_buffer) > self.averaging_samples:
            self.sample_buffer.pop(0)
        
        # Calculate new average
        if self.sample_buffer:
            self.current_average = sum(self.sample_buffer) / len(self.sample_buffer)
    
    def _normalize_value(self, raw_value):
        """
        Normalize ADC value to 0.0-1.0 range with compensation for limited potentiometer range
        
        Args:
            raw_value: Raw ADC value
            
        Returns:
            Normalized value (0.0-1.0)
        """
        # Apply scaling to compensate for limited potentiometer range
        scaled_value = (raw_value - self.observed_min_raw) * self.scale_factor
        scaled_value = max(0, min(4095, scaled_value))  # Clamp to valid range
        return scaled_value / self.max_value
    
    def _calculate_bpm(self, normalized_value):
        """
        Calculate BPM from normalized potentiometer value
        
        Args:
            normalized_value: Normalized potentiometer value (0.0-1.0)
            
        Returns:
            BPM value
        """
        return self.min_bpm + (normalized_value * (self.max_bpm - self.min_bpm))
    
    def _should_send_update(self, new_value):
        """
        Determine if value update should be sent to high-performance core
        
        Args:
            new_value: New normalized value
            
        Returns:
            True if update should be sent
        """
        if abs(new_value - self.last_sent_value) >= self.value_change_threshold:
            return True
        
        # Send periodic updates even if value hasn't changed much
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_sample_time) > 1000:  # 1 second
            return True
        
        return False
    
    def _send_value_update(self, normalized_value, bpm_value):
        """
        Send potentiometer value update to high-performance core
        
        Args:
            normalized_value: Normalized potentiometer value
            bpm_value: Calculated BPM value
        """
        self.intercore_comm._send_to_hp_core({
            'type': RESP_POTENTIOMETER_VALUE,
            'normalized_value': normalized_value,
            'bpm_value': bpm_value,
            'raw_average': self.current_average,
            'sample_count': self.sample_count,
            'timestamp': time.ticks_ms()
        })
        
        self.last_sent_value = normalized_value
        self.last_sample_time = time.ticks_ms()
    
    def _sampling_thread_function(self):
        """Main sampling thread function for low-power core"""
        while self.is_running:
            with self.thread_lock:
                # Read ADC sample
                raw_sample = self._read_adc_sample()
                self.sample_count += 1
                
                # Apply decimation
                decimated_sample = self._decimate_sample(raw_sample)
                
                if decimated_sample is not None:
                    # Update running average
                    self._update_average(decimated_sample)
                    
                    # Normalize value
                    normalized_value = self._normalize_value(self.current_average)
                    
                    # Calculate BPM
                    bpm_value = self._calculate_bpm(normalized_value)
                    
                    # Check if we should send update
                    if self._should_send_update(normalized_value):
                        self._send_value_update(normalized_value, bpm_value)
                        print(f"Potentiometer: {normalized_value:.3f} -> {bpm_value:.1f} BPM")
            
            # Sleep for sampling interval
            time.sleep_ms(self.sampling_interval_ms)
    
    def start(self):
        """Start the low-power potentiometer sampling"""
        if not self.is_running:
            self.is_running = True
            
            # Clear sample buffer
            self.sample_buffer = []
            self.decimation_counter = 0
            self.current_average = 0.0
            self.last_sent_value = 0.0
            
            # Start sampling thread
            self.sampling_thread = _thread.start_new_thread(self._sampling_thread_function, ())
            
            print(f"Low-power potentiometer started: {self.sampling_interval_ms}ms interval, {self.decimation_factor}x decimation")
    
    def stop(self):
        """Stop the low-power potentiometer sampling"""
        if self.is_running:
            self.is_running = False
            
            # Wait for thread to finish
            time.sleep_ms(100)
            
            print("Low-power potentiometer stopped")
    
    def set_sampling_rate(self, interval_ms):
        """
        Set sampling interval
        
        Args:
            interval_ms: Sampling interval in milliseconds
        """
        self.sampling_interval_ms = max(10, interval_ms)  # Minimum 10ms
        print(f"Sampling interval set to {self.sampling_interval_ms}ms")
    
    def set_decimation_factor(self, factor):
        """
        Set decimation factor
        
        Args:
            factor: Decimation factor (higher = less frequent sampling)
        """
        self.decimation_factor = max(1, factor)
        print(f"Decimation factor set to {self.decimation_factor}")
    
    def set_averaging_samples(self, samples):
        """
        Set number of samples for averaging
        
        Args:
            samples: Number of samples to average
        """
        self.averaging_samples = max(1, samples)
        print(f"Averaging samples set to {self.averaging_samples}")
    
    def set_bpm_range(self, min_bpm, max_bpm):
        """
        Set BPM range for potentiometer scaling
        
        Args:
            min_bpm: Minimum BPM value
            max_bpm: Maximum BPM value
        """
        self.min_bpm = max(1.0, min_bpm)
        self.max_bpm = max(self.min_bpm + 1.0, max_bpm)
        print(f"BPM range set to {self.min_bpm}-{self.max_bpm}")
    
    def set_change_threshold(self, threshold):
        """
        Set value change threshold for updates
        
        Args:
            threshold: Threshold value (0.0-1.0)
        """
        self.value_change_threshold = max(0.001, min(0.1, threshold))
        print(f"Change threshold set to {self.value_change_threshold:.3f}")
    
    def get_current_value(self):
        """
        Get current normalized potentiometer value
        
        Returns:
            Current normalized value (0.0-1.0)
        """
        if self.sample_buffer:
            return self._normalize_value(self.current_average)
        return 0.0
    
    def get_current_bpm(self):
        """
        Get current BPM value
        
        Returns:
            Current BPM value
        """
        normalized_value = self.get_current_value()
        return self._calculate_bpm(normalized_value)
    
    def get_statistics(self):
        """
        Get potentiometer statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'sample_count': self.sample_count,
            'current_average': self.current_average,
            'normalized_value': self.get_current_value(),
            'bpm_value': self.get_current_bpm(),
            'buffer_size': len(self.sample_buffer),
            'decimation_factor': self.decimation_factor,
            'averaging_samples': self.averaging_samples,
            'sampling_interval_ms': self.sampling_interval_ms,
            'last_sent_value': self.last_sent_value
        }
    
    def get_configuration(self):
        """
        Get potentiometer configuration
        
        Returns:
            Dictionary with configuration
        """
        return {
            'pin': self.pin,
            'resolution': self.resolution,
            'decimation_factor': self.decimation_factor,
            'averaging_samples': self.averaging_samples,
            'sampling_interval_ms': self.sampling_interval_ms,
            'min_bpm': self.min_bpm,
            'max_bpm': self.max_bpm,
            'change_threshold': self.value_change_threshold,
            'is_running': self.is_running
        }
    
    def force_update(self):
        """Force send current value to high-performance core"""
        if self.sample_buffer:
            normalized_value = self._normalize_value(self.current_average)
            bpm_value = self._calculate_bpm(normalized_value)
            self._send_value_update(normalized_value, bpm_value)
            print(f"Forced update: {normalized_value:.3f} -> {bpm_value:.1f} BPM")
