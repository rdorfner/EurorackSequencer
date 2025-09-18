"""
Test Program for Clock Generator Library

This test program exercises all functionality of the clock generator library
including BPM control via potentiometer, start/stop/pause operations, and
real-time monitoring. The test demonstrates clock rate changes and provides
visual feedback through the LED.

Algorithm Overview:
- Initialize potentiometer and clock generator
- Test basic clock operations (start, stop, pause, resume)
- Demonstrate BPM range control via potentiometer
- Test manual BPM setting and automatic updates
- Provide real-time monitoring with status display
- Test configuration changes and edge cases
- Demonstrate thread safety and cleanup
"""

import time
import sys
import os

# Add the drivers directory to the path to import our libraries
#sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drivers'))

from potentiometer import Potentiometer
from clock_generator import ClockGenerator

def test_basic_operations(clock):
    """Test basic clock operations"""
    print("Testing basic clock operations...")
    print("=" * 40)
    
    # Test start
    print("Starting clock...")
    clock.start()
    time.sleep(2)
    
    # Test pause
    print("Pausing clock...")
    clock.pause()
    time.sleep(1)
    
    # Test resume
    print("Resuming clock...")
    clock.resume()
    time.sleep(2)
    
    # Test stop
    print("Stopping clock...")
    clock.stop()
    time.sleep(1)
    
    print("Basic operations test completed\n")

def test_bpm_control(clock):
    """Test BPM control via potentiometer"""
    print("Testing BPM control via potentiometer...")
    print("=" * 40)
    print("Turn the potentiometer to change clock rate")
    print("Clock will run for 10 seconds")
    print()
    
    clock.start()
    start_time = time.time()
    
    try:
        while time.time() - start_time < 10:
            bpm = clock.get_bpm()
            status = clock.get_status()
            
            # Create a simple visual indicator
            bpm_normalized = (bpm - clock.min_bpm) / (clock.max_bpm - clock.min_bpm)
            bar_length = 20
            bar_fill = int(bpm_normalized * bar_length)
            bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            print(f"\rBPM: {bpm:6.1f} | Period: {status['period_ms']:4d}ms | [{bar}]", end="")
            time.sleep(0.1)
        
        print("\n\nBPM control test completed\n")
        
    except KeyboardInterrupt:
        print("\n\nBPM control test interrupted\n")
    finally:
        clock.stop()

def test_manual_bpm_setting(clock):
    """Test manual BPM setting"""
    print("Testing manual BPM setting...")
    print("=" * 40)
    
    test_bpms = [10, 60, 120, 200, 5, 240]
    
    for bpm in test_bpms:
        print(f"Setting BPM to {bpm}...")
        clock.set_bpm(bpm)
        time.sleep(0.5)
        
        actual_bpm = clock.get_bpm()
        print(f"  Actual BPM: {actual_bpm:.1f}")
        time.sleep(1)
    
    print("Manual BPM setting test completed\n")

def test_pulse_width_adjustment(clock):
    """Test pulse width adjustment"""
    print("Testing pulse width adjustment...")
    print("=" * 40)
    
    clock.set_bpm(60)  # Set to 60 BPM for consistent testing
    clock.start()
    
    pulse_widths = [25, 50, 100, 200]
    
    for width in pulse_widths:
        print(f"Setting pulse width to {width}ms...")
        clock.set_pulse_width(width)
        time.sleep(2)
    
    clock.stop()
    print("Pulse width adjustment test completed\n")

def test_bpm_range_adjustment(clock):
    """Test BPM range adjustment"""
    print("Testing BPM range adjustment...")
    print("=" * 40)
    
    # Test different BPM ranges
    ranges = [
        (10, 100),    # Narrow range
        (1, 300),     # Wide range
        (50, 150),    # Medium range
        (5, 240),     # Original range
    ]
    
    for min_bpm, max_bpm in ranges:
        print(f"Setting BPM range to {min_bpm}-{max_bpm}...")
        clock.set_bpm_range(min_bpm, max_bpm)
        
        status = clock.get_status()
        print(f"  Current BPM: {status['current_bpm']:.1f}")
        print(f"  Min BPM: {status['min_bpm']}")
        print(f"  Max BPM: {status['max_bpm']}")
        time.sleep(1)
    
    print("BPM range adjustment test completed\n")

def test_real_time_monitoring(clock):
    """Test real-time monitoring with detailed status"""
    print("Testing real-time monitoring...")
    print("=" * 40)
    print("Turn the potentiometer to see real-time BPM changes")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    clock.start()
    
    try:
        for i in range(100):  # Run for 100 samples
            status = clock.get_status()
            bpm = status['current_bpm']
            period = status['period_ms']
            pulse_width = status['pulse_width_ms']
            
            # Create visual indicators
            bpm_normalized = (bpm - clock.min_bpm) / (clock.max_bpm - clock.min_bpm)
            bar_length = 20
            bar_fill = int(bpm_normalized * bar_length)
            bpm_bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            # Status indicator
            if status['is_paused']:
                status_indicator = "PAUSED"
            elif status['is_running']:
                status_indicator = "RUNNING"
            else:
                status_indicator = "STOPPED"
            
            print(f"\rStatus: {status_indicator:7s} | BPM: {bpm:6.1f} | "
                  f"Period: {period:4d}ms | Pulse: {pulse_width:3d}ms | [{bpm_bar}]", end="")
            
            time.sleep(0.1)
        
        print("\n\nReal-time monitoring test completed\n")
        
    except KeyboardInterrupt:
        print("\n\nReal-time monitoring stopped by user\n")
    finally:
        clock.stop()

def test_edge_cases(clock):
    """Test edge cases and error conditions"""
    print("Testing edge cases...")
    print("=" * 40)
    
    # Test starting already running clock
    print("Testing starting already running clock...")
    clock.start()
    clock.start()  # Should not cause issues
    time.sleep(1)
    
    # Test stopping already stopped clock
    print("Testing stopping already stopped clock...")
    clock.stop()
    clock.stop()  # Should not cause issues
    
    # Test pausing stopped clock
    print("Testing pausing stopped clock...")
    clock.pause()  # Should not cause issues
    
    # Test resuming non-paused clock
    print("Testing resuming non-paused clock...")
    clock.start()
    clock.resume()  # Should not cause issues
    time.sleep(1)
    
    # Test extreme BPM values
    print("Testing extreme BPM values...")
    clock.set_bpm(0)  # Should clamp to min
    print(f"  BPM after setting 0: {clock.get_bpm()}")
    
    clock.set_bpm(1000)  # Should clamp to max
    print(f"  BPM after setting 1000: {clock.get_bpm()}")
    
    # Test extreme pulse widths
    print("Testing extreme pulse widths...")
    clock.set_pulse_width(0)  # Should clamp to min
    clock.set_pulse_width(2000)  # Should clamp to max
    
    clock.stop()
    print("Edge cases test completed\n")

def test_configuration_info(clock):
    """Test configuration and information functions"""
    print("Testing configuration and information...")
    print("=" * 40)
    
    # Get status information
    status = clock.get_status()
    print("Current configuration:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test force BPM update
    print("\nTesting force BPM update...")
    clock.force_bpm_update()
    print(f"  Current BPM: {clock.get_bpm():.1f}")
    
    print("Configuration info test completed\n")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("Starting Clock Generator Library Test Suite")
    print("=" * 50)
    
    # Initialize potentiometer and clock generator
    pot = Potentiometer(pin=1, resolution=12, smoothing_samples=5)
    clock = ClockGenerator(pot, led_pin=15, min_bpm=5, max_bpm=240, pulse_width_ms=50)
    
    print("Potentiometer initialized on pin D1")
    print("Clock generator initialized with LED on pin GPIO15")
    print("BPM range: 5-240, Pulse width: 50ms")
    print()
    
    try:
        # Run all test functions
        test_basic_operations(clock)
        test_manual_bpm_setting(clock)
        test_pulse_width_adjustment(clock)
        test_bpm_range_adjustment(clock)
        test_configuration_info(clock)
        test_edge_cases(clock)
        
        print("=" * 50)
        print("All automated tests completed successfully!")
        print()
        
        # Interactive tests
        print("Starting interactive tests...")
        print("These tests require potentiometer interaction")
        print()
        
        # Ask user if they want to run interactive tests
        print("Would you like to run interactive tests? (y/n): ", end="")
        # For automated testing, we'll assume yes
        run_interactive = True
        
        if run_interactive:
            test_bpm_control(clock)
            test_real_time_monitoring(clock)
        
        print("Test suite finished successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        # Clean up
        clock.cleanup()
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("All tests completed successfully!")
    else:
        print("Test suite failed!")
