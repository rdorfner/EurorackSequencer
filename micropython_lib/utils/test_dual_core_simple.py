"""
Simplified Dual-Core Sequencer Test for MicroPython

This is a simplified version of the dual-core test that works with MicroPython's
import system and doesn't rely on complex path manipulation.
"""

import time
import sys

# Import the dual-core libraries directly
from neopixel_display import NeopixelDisplay
from intercore_communication import InterCoreCommunication
from clock_generator_lp import LowPowerClockGenerator
from potentiometer_lp import LowPowerPotentiometer
from trigger_generator_hp import HighPerformanceTriggerGenerator

def test_basic_dual_core_functionality():
    """Test basic dual-core functionality"""
    print("Starting Dual-Core Sequencer Test")
    print("=" * 40)
    
    try:
        # Initialize components
        print("Initializing components...")
        neopixel_display = NeopixelDisplay(pin=0, brightness=0.1)
        intercore_comm = InterCoreCommunication()
        
        # Low-power core components
        clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15, min_bpm=60, max_bpm=180)
        pot_gen = LowPowerPotentiometer(intercore_comm, pin=2, decimation_factor=4, averaging_samples=8)
        
        # High-performance core components
        trigger_gen = HighPerformanceTriggerGenerator(intercore_comm, neopixel_display)
        
        print("Components initialized successfully!")
        print()
        
        # Test 1: Inter-core communication
        print("Test 1: Inter-core communication...")
        intercore_comm.set_shared_data('test_value', 42)
        test_value = intercore_comm.get_shared_data('test_value')
        print(f"Shared memory test: {test_value}")
        
        status = intercore_comm.get_system_status()
        print("System status retrieved successfully")
        print()
        
        # Test 2: Clock generator
        print("Test 2: Low-power clock generator...")
        clock_gen.set_bpm(120)
        print("BPM set to 120")
        
        clock_gen.start()
        print("Clock generator started")
        time.sleep(2)
        
        clock_status = clock_gen.get_status()
        print(f"Clock status: {clock_status['current_bpm']:.1f} BPM, running: {clock_status['is_running']}")
        clock_gen.stop()
        print("Clock generator stopped")
        print()
        
        # Test 3: Potentiometer
        print("Test 3: Low-power potentiometer...")
        pot_gen.set_sampling_rate(100)  # 10 Hz
        pot_gen.start()
        print("Potentiometer started")
        time.sleep(2)
        
        pot_stats = pot_gen.get_statistics()
        print(f"Potentiometer value: {pot_stats['normalized_value']:.3f}")
        print(f"BPM value: {pot_stats['bpm_value']:.1f}")
        pot_gen.stop()
        print("Potentiometer stopped")
        print()
        
        # Test 4: Trigger generator
        print("Test 4: High-performance trigger generator...")
        trigger_gen.start()
        print("Trigger generator started")
        
        # Create a simple pattern
        simple_pattern = "1010101010101010"  # Alternating pattern
        trigger_gen.create_simple_pattern(simple_pattern)
        trigger_gen.enable_pattern(True)
        print("Simple pattern created and enabled")
        
        time.sleep(2)
        trigger_gen.enable_pattern(False)
        trigger_gen.stop()
        print("Trigger generator stopped")
        print()
        
        # Test 5: Integrated test
        print("Test 5: Integrated dual-core test...")
        print("Starting all components for 5 seconds...")
        
        clock_gen.start()
        pot_gen.start()
        trigger_gen.start()
        
        # Create a test pattern
        test_pattern = [
            [True, False, False, False, False, False, False],   # Step 1: Trigger 0
            [False, True, False, False, False, False, False],   # Step 2: Trigger 1
            [False, False, True, False, False, False, False],   # Step 3: Trigger 2
            [False, False, False, True, False, False, False],   # Step 4: Trigger 3
            [False, False, False, False, True, False, False],   # Step 5: Trigger 4
            [False, False, False, False, False, True, False],   # Step 6: Trigger 5
            [False, False, False, False, False, False, True],   # Step 7: Trigger 6
            [False, False, False, False, False, False, False],  # Step 8: No triggers
        ]
        
        trigger_gen.set_trigger_pattern(test_pattern)
        trigger_gen.enable_pattern(True)
        
        print("Watch the neopixel display and LED for activity...")
        print("Clock LED should be blinking on GPIO15")
        
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 5000:  # 5 seconds
            # Process inter-core messages
            intercore_comm.process_messages()
            
            # Get status
            clock_status = clock_gen.get_status()
            pot_stats = pot_gen.get_statistics()
            trigger_stats = trigger_gen.get_trigger_statistics()
            
            # Display status
            print(f"\rClock: {clock_status['current_bpm']:.1f} BPM | "
                  f"Pot: {pot_stats['bpm_value']:.1f} BPM | "
                  f"Pattern: {trigger_stats['current_pattern_index']}/{trigger_stats['pattern_length']}", end="")
            
            time.sleep(0.2)
        
        print("\n\nStopping all components...")
        trigger_gen.stop()
        pot_gen.stop()
        clock_gen.stop()
        
        print("=" * 40)
        print("All dual-core tests completed successfully!")
        print()
        print("Summary:")
        print("- Inter-core communication: ✓")
        print("- Low-power clock generator: ✓")
        print("- Low-power potentiometer: ✓")
        print("- High-performance trigger generator: ✓")
        print("- Integrated dual-core operation: ✓")
        
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_external_clock():
    """Test external clock functionality"""
    print("\nTesting external clock functionality...")
    print("=" * 40)
    
    try:
        intercore_comm = InterCoreCommunication()
        clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15)
        
        # Setup external clock
        clock_gen.setup_external_clock_input(10)  # Pin 10
        clock_gen.start()
        
        print("External clock test setup complete")
        print("Connect an external clock signal to pin 10 to test")
        print("The system should automatically switch to external clock")
        print("Running for 10 seconds...")
        
        for i in range(50):  # Run for 5 seconds
            status = clock_gen.get_status()
            system_status = intercore_comm.get_system_status()
            
            print(f"\rClock source: {status['clock_source']} | "
                  f"BPM: {status['current_bpm']:.1f} | "
                  f"External active: {status['external_clock_active']}", end="")
            
            time.sleep(0.1)
        
        print("\nExternal clock test completed")
        clock_gen.stop()
        
    except Exception as e:
        print(f"External clock test failed: {e}")

if __name__ == "__main__":
    success = test_basic_dual_core_functionality()
    if success:
        test_external_clock()
        print("\nDual-core test suite completed successfully!")
    else:
        print("Dual-core test suite failed!")
