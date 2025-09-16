"""
Potentiometer Library for ESP32-C6 Sequencer Project

This module provides an interface for reading analog values from a potentiometer
connected to the ESP32-C6's A/D converter. The library supports various scaling
options and provides smoothed readings to reduce noise.

Algorithm Overview:
- Initialize ADC on specified pin with configurable resolution
- Read raw ADC values and convert to voltage
- Provide scaling functions for different ranges (0-1, 0-100, etc.)
- Implement smoothing/averaging to reduce noise
- Support calibration for accurate readings
"""

import machine
import time

class Potentiometer:
    def __init__(self, pin=2, resolution=12, smoothing_samples=5):
        """
        Initialize potentiometer on specified ADC pin
        
        Args:
            pin: ADC pin number (default: 2 for D2)
            resolution: ADC resolution in bits (default: 12)
            smoothing_samples: Number of samples for smoothing (default: 5)
        """
        self.pin = pin
        self.resolution = resolution
        self.smoothing_samples = smoothing_samples
        self.max_value = (2 ** resolution) - 1
        
        # Initialize ADC
        self.adc = machine.ADC(machine.Pin(pin))
        self.adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution
        
        # Calibration values (can be adjusted)
        self.min_raw = 0
        self.max_raw = self.max_value
        self.min_voltage = 0.0
        self.max_voltage = 3.3
        
    def read_raw(self):
        """
        Read raw ADC value
        
        Returns:
            Raw ADC value (0 to max_value)
        """
        return self.adc.read()
    
    def read_voltage(self):
        """
        Read voltage value
        
        Returns:
            Voltage in volts (0.0 to 3.3V)
        """
        raw_value = self.read_raw()
        voltage = (raw_value / self.max_value) * self.max_voltage
        return voltage
    
    def read_smoothed_raw(self):
        """
        Read smoothed raw ADC value using multiple samples
        
        Returns:
            Smoothed raw ADC value
        """
        total = 0
        for _ in range(self.smoothing_samples):
            total += self.read_raw()
            time.sleep_us(100)  # Small delay between samples
        return total // self.smoothing_samples
    
    def read_smoothed_voltage(self):
        """
        Read smoothed voltage value
        
        Returns:
            Smoothed voltage in volts
        """
        raw_value = self.read_smoothed_raw()
        voltage = (raw_value / self.max_value) * self.max_voltage
        return voltage
    
    def read_percentage(self):
        """
        Read potentiometer value as percentage (0-100)
        
        Returns:
            Percentage value (0.0 to 100.0)
        """
        raw_value = self.read_smoothed_raw()
        percentage = (raw_value / self.max_value) * 100.0
        return percentage
    
    def read_normalized(self):
        """
        Read potentiometer value as normalized value (0.0-1.0)
        
        Returns:
            Normalized value (0.0 to 1.0)
        """
        raw_value = self.read_smoothed_raw()
        normalized = raw_value / self.max_value
        return normalized
    
    def read_range(self, min_val, max_val):
        """
        Read potentiometer value scaled to specified range
        
        Args:
            min_val: Minimum value of the range
            max_val: Maximum value of the range
            
        Returns:
            Scaled value within the specified range
        """
        normalized = self.read_normalized()
        scaled = min_val + (normalized * (max_val - min_val))
        return scaled
    
    def calibrate(self, samples=100):
        """
        Calibrate the potentiometer by finding min/max values
        
        Args:
            samples: Number of samples to take for calibration
        """
        print("Calibrating potentiometer...")
        print("Turn potentiometer to minimum position and press Enter")
        input()
        
        min_values = []
        for _ in range(samples):
            min_values.append(self.read_raw())
            time.sleep_ms(10)
        self.min_raw = sum(min_values) // len(min_values)
        
        print("Turn potentiometer to maximum position and press Enter")
        input()
        
        max_values = []
        for _ in range(samples):
            max_values.append(self.read_raw())
            time.sleep_ms(10)
        self.max_raw = sum(max_values) // len(max_values)
        
        print(f"Calibration complete: min={self.min_raw}, max={self.max_raw}")
    
    def read_calibrated_percentage(self):
        """
        Read calibrated percentage value using min/max calibration
        
        Returns:
            Calibrated percentage (0.0 to 100.0)
        """
        raw_value = self.read_smoothed_raw()
        if self.max_raw == self.min_raw:
            return 50.0  # Avoid division by zero
        
        calibrated = ((raw_value - self.min_raw) / (self.max_raw - self.min_raw)) * 100.0
        return max(0.0, min(100.0, calibrated))  # Clamp to 0-100 range
    
    def set_smoothing_samples(self, samples):
        """
        Set number of samples for smoothing
        
        Args:
            samples: Number of samples (1 or more)
        """
        self.smoothing_samples = max(1, samples)
    
    def get_info(self):
        """
        Get potentiometer configuration information
        
        Returns:
            Dictionary with configuration info
        """
        return {
            'pin': self.pin,
            'resolution': self.resolution,
            'max_value': self.max_value,
            'smoothing_samples': self.smoothing_samples,
            'min_raw': self.min_raw,
            'max_raw': self.max_raw,
            'min_voltage': self.min_voltage,
            'max_voltage': self.max_voltage
        }
