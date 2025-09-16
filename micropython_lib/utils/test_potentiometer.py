"""
Test Program for Potentiometer Library

This test program exercises all functionality of the potentiometer library
including raw readings, voltage conversion, smoothing, scaling, and calibration.
The test demonstrates various reading modes and provides real-time monitoring.

Algorithm Overview:
- Initialize potentiometer on pin D2
- Test raw ADC readings and voltage conversion
- Demonstrate smoothing functionality
- Test various scaling modes (percentage, normalized, custom range)
- Perform calibration procedure
- Provide real-time monitoring with visual feedback
- Test configuration and information retrieval
"""

import time
import sys
import os

# Add the drivers directory to the path to import our library
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drivers'))

from potentiometer import Potentiometer

def test_basic_readings(pot):
    """Test basic reading functions"""
    print("Testing basic reading functions...")
    print("=" * 40)
    
    for i in range(10):
        raw = pot.read_raw()
        voltage = pot.read_voltage()
        percentage = pot.read_percentage()
        normalized = pot.read_normalized()
        
        print(f"Sample {i+1:2d}: Raw={raw:4d}, Voltage={voltage:.3f}V, "
              f"Percentage={percentage:5.1f}%, Normalized={normalized:.3f}")
        time.sleep(0.5)
    
    print("Basic readings test completed\n")

def test_smoothing(pot):
    """Test smoothing functionality"""
    print("Testing smoothing functionality...")
    print("=" * 40)
    
    # Test with different smoothing levels
    smoothing_levels = [1, 3, 5, 10]
    
    for samples in smoothing_levels:
        pot.set_smoothing_samples(samples)
        print(f"Testing with {samples} smoothing samples:")
        
        for i in range(5):
            raw = pot.read_smoothed_raw()
            voltage = pot.read_smoothed_voltage()
            print(f"  Sample {i+1}: Raw={raw:4d}, Voltage={voltage:.3f}V")
            time.sleep(0.3)
        print()
    
    # Reset to default
    pot.set_smoothing_samples(5)
    print("Smoothing test completed\n")

def test_scaling(pot):
    """Test various scaling functions"""
    print("Testing scaling functions...")
    print("=" * 40)
    
    # Test custom range scaling
    ranges = [
        (0, 100),      # 0-100
        (-50, 50),     # -50 to +50
        (0, 255),      # 0-255 (like PWM)
        (1000, 2000),  # 1000-2000 (like servo)
    ]
    
    for min_val, max_val in ranges:
        print(f"Scaling to range {min_val}-{max_val}:")
        for i in range(3):
            scaled = pot.read_range(min_val, max_val)
            print(f"  Sample {i+1}: {scaled:.2f}")
            time.sleep(0.3)
        print()
    
    print("Scaling test completed\n")

def test_calibration(pot):
    """Test calibration functionality"""
    print("Testing calibration functionality...")
    print("=" * 40)
    
    print("Before calibration:")
    print(f"  Min raw: {pot.min_raw}, Max raw: {pot.max_raw}")
    print(f"  Calibrated percentage: {pot.read_calibrated_percentage():.1f}%")
    
    # Note: In a real test, you would call pot.calibrate() here
    # For automated testing, we'll simulate calibration values
    print("\nSimulating calibration...")
    pot.min_raw = 100
    pot.max_raw = 4000
    
    print("After calibration:")
    print(f"  Min raw: {pot.min_raw}, Max raw: {pot.max_raw}")
    print(f"  Calibrated percentage: {pot.read_calibrated_percentage():.1f}%")
    
    print("Calibration test completed\n")

def test_real_time_monitoring(pot):
    """Test real-time monitoring with visual feedback"""
    print("Testing real-time monitoring...")
    print("=" * 40)
    print("Turn the potentiometer to see real-time values")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        for i in range(50):  # Run for 50 samples
            raw = pot.read_smoothed_raw()
            voltage = pot.read_smoothed_voltage()
            percentage = pot.read_percentage()
            
            # Create a simple visual bar
            bar_length = 20
            bar_fill = int((percentage / 100.0) * bar_length)
            bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            print(f"\rRaw: {raw:4d} | Voltage: {voltage:.3f}V | "
                  f"Percentage: {percentage:5.1f}% | [{bar}]", end="")
            
            time.sleep(0.1)
        
        print("\n\nReal-time monitoring test completed\n")
        
    except KeyboardInterrupt:
        print("\n\nReal-time monitoring stopped by user\n")

def test_configuration(pot):
    """Test configuration and information functions"""
    print("Testing configuration functions...")
    print("=" * 40)
    
    # Get current configuration
    info = pot.get_info()
    print("Current configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test changing smoothing samples
    print(f"\nOriginal smoothing samples: {pot.smoothing_samples}")
    pot.set_smoothing_samples(10)
    print(f"New smoothing samples: {pot.smoothing_samples}")
    
    # Reset to default
    pot.set_smoothing_samples(5)
    print(f"Reset smoothing samples: {pot.smoothing_samples}")
    
    print("Configuration test completed\n")

def test_edge_cases(pot):
    """Test edge cases and error conditions"""
    print("Testing edge cases...")
    print("=" * 40)
    
    # Test with minimum smoothing samples
    pot.set_smoothing_samples(1)
    print("Testing with 1 smoothing sample:")
    for i in range(3):
        raw = pot.read_smoothed_raw()
        print(f"  Sample {i+1}: {raw}")
        time.sleep(0.1)
    
    # Test with high smoothing samples
    pot.set_smoothing_samples(20)
    print("Testing with 20 smoothing samples:")
    for i in range(3):
        raw = pot.read_smoothed_raw()
        print(f"  Sample {i+1}: {raw}")
        time.sleep(0.1)
    
    # Reset to default
    pot.set_smoothing_samples(5)
    
    # Test calibration edge case (min == max)
    print("Testing calibration edge case (min == max):")
    original_min = pot.min_raw
    original_max = pot.max_raw
    pot.min_raw = 1000
    pot.max_raw = 1000  # Same as min
    calibrated = pot.read_calibrated_percentage()
    print(f"  Calibrated percentage with min==max: {calibrated:.1f}%")
    
    # Restore original values
    pot.min_raw = original_min
    pot.max_raw = original_max
    
    print("Edge cases test completed\n")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("Starting Potentiometer Library Test Suite")
    print("=" * 50)
    
    # Initialize potentiometer
    pot = Potentiometer(pin=2, resolution=12, smoothing_samples=5)
    print("Potentiometer initialized on pin D2 with 12-bit resolution")
    print()
    
    try:
        # Run all test functions
        test_basic_readings(pot)
        test_smoothing(pot)
        test_scaling(pot)
        test_calibration(pot)
        test_configuration(pot)
        test_edge_cases(pot)
        
        print("=" * 50)
        print("All automated tests completed successfully!")
        print()
        
        # Interactive real-time monitoring
        print("Starting interactive real-time monitoring...")
        print("This will run for 10 seconds, then you can choose to continue or exit")
        print()
        
        start_time = time.time()
        while time.time() - start_time < 10:
            raw = pot.read_smoothed_raw()
            voltage = pot.read_smoothed_voltage()
            percentage = pot.read_percentage()
            
            # Create a simple visual bar
            bar_length = 20
            bar_fill = int((percentage / 100.0) * bar_length)
            bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            print(f"\rRaw: {raw:4d} | Voltage: {voltage:.3f}V | "
                  f"Percentage: {percentage:5.1f}% | [{bar}]", end="")
            
            time.sleep(0.1)
        
        print("\n\nInteractive monitoring completed!")
        print("Test suite finished successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("All tests completed successfully!")
    else:
        print("Test suite failed!")
