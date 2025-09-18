"""
Test Program for Trigger Generator Library

This test program exercises all functionality of the trigger generator library
including trigger scheduling, timing, neopixel feedback, and integration with
the clock generator. The test demonstrates trigger patterns and visual feedback.

Algorithm Overview:
- Initialize neopixel display and trigger generator
- Test individual trigger outputs and scheduling
- Demonstrate trigger patterns and timing
- Test integration with clock generator
- Provide visual feedback through neopixel display
- Test trigger statistics and configuration
- Demonstrate high-priority thread operation
"""

import time
import sys
import os

# Add the drivers directory to the path to import our libraries
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drivers'))

from neopixel_display import NeopixelDisplay
from trigger_generator import TriggerGenerator
from clock_generator import ClockGenerator
from potentiometer import Potentiometer

def test_basic_trigger_operations(trigger_gen):
    """Test basic trigger operations"""
    print("Testing basic trigger operations...")
    print("=" * 40)
    
    # Test individual trigger scheduling
    print("Testing individual trigger scheduling...")
    for i in range(trigger_gen.num_triggers):
        print(f"Scheduling trigger {i}")
        trigger_gen.schedule_trigger(i, True)
        time.sleep(0.1)
    
    # Test trigger state queries
    print("Testing trigger state queries...")
    for i in range(trigger_gen.num_triggers):
        state = trigger_gen.get_trigger_state(i)
        print(f"Trigger {i} state: {state}")
    
    print("Basic trigger operations test completed\n")

def test_trigger_scheduling(trigger_gen):
    """Test trigger scheduling patterns"""
    print("Testing trigger scheduling patterns...")
    print("=" * 40)
    
    # Test single trigger
    print("Testing single trigger scheduling...")
    trigger_gen.schedule_trigger(0, True)
    time.sleep(0.1)
    
    # Test multiple triggers
    print("Testing multiple trigger scheduling...")
    trigger_states = [True, False, True, False, True, False, True]
    trigger_gen.schedule_triggers(clock_states)
    time.sleep(0.1)
    
    # Test all triggers
    print("Testing all triggers...")
    all_triggers = [True] * trigger_gen.num_triggers
    trigger_gen.schedule_triggers(all_triggers)
    time.sleep(0.1)
    
    print("Trigger scheduling test completed\n")

def test_trigger_timing(trigger_gen):
    """Test trigger timing and duration"""
    print("Testing trigger timing...")
    print("=" * 40)
    
    # Schedule a trigger and measure timing
    print("Scheduling trigger 0 and measuring timing...")
    start_time = time.ticks_ms()
    trigger_gen.schedule_trigger(0, True)
    
    # Wait for trigger to be processed
    time.sleep(0.1)
    
    # Check if trigger is active
    if trigger_gen.get_trigger_state(0):
        print("Trigger 0 is active")
    
    # Wait for 50ms reset
    time.sleep(0.1)
    
    # Check if trigger was reset
    if not trigger_gen.get_trigger_state(0):
        print("Trigger 0 was reset after 50ms")
    
    print("Trigger timing test completed\n")

def test_trigger_statistics(trigger_gen):
    """Test trigger statistics"""
    print("Testing trigger statistics...")
    print("=" * 40)
    
    # Get initial statistics
    stats = trigger_gen.get_trigger_statistics()
    print("Initial statistics:")
    print(f"  Trigger counts: {stats['trigger_count']}")
    print(f"  Last trigger times: {stats['last_trigger_time']}")
    
    # Schedule some triggers
    for i in range(3):
        trigger_gen.schedule_trigger(i, True)
        time.sleep(0.1)
    
    # Get updated statistics
    stats = trigger_gen.get_trigger_statistics()
    print("Updated statistics:")
    print(f"  Trigger counts: {stats['trigger_count']}")
    print(f"  Current states: {stats['current_states']}")
    
    # Reset statistics
    trigger_gen.reset_statistics()
    stats = trigger_gen.get_trigger_statistics()
    print("After reset:")
    print(f"  Trigger counts: {stats['trigger_count']}")
    
    print("Trigger statistics test completed\n")

def test_trigger_configuration(trigger_gen):
    """Test trigger configuration"""
    print("Testing trigger configuration...")
    print("=" * 40)
    
    # Get configuration
    config = trigger_gen.get_configuration()
    print("Current configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Test changing trigger pin (simulation)
    print("Testing trigger pin configuration...")
    original_pins = config['trigger_pins'].copy()
    print(f"Original pins: {original_pins}")
    
    print("Trigger configuration test completed\n")

def test_trigger_testing(trigger_gen):
    """Test trigger testing functions"""
    print("Testing trigger testing functions...")
    print("=" * 40)
    
    # Test individual trigger
    print("Testing individual trigger...")
    trigger_gen.test_trigger(0, 200)
    time.sleep(0.3)
    
    # Test all triggers
    print("Testing all triggers...")
    trigger_gen.test_all_triggers(100)
    
    print("Trigger testing functions test completed\n")

def test_clock_integration(trigger_gen, clock_gen):
    """Test integration with clock generator"""
    print("Testing clock integration...")
    print("=" * 40)
    
    # Connect trigger generator to clock
    clock_gen.set_trigger_generator(trigger_gen)
    
    # Schedule some triggers
    trigger_gen.schedule_trigger(0, True)
    trigger_gen.schedule_trigger(2, True)
    trigger_gen.schedule_trigger(4, True)
    
    print("Starting clock for 3 seconds with scheduled triggers...")
    clock_gen.start()
    time.sleep(3)
    clock_gen.stop()
    
    # Check trigger statistics
    stats = trigger_gen.get_trigger_statistics()
    print(f"Triggers fired during clock test: {stats['trigger_count']}")
    
    print("Clock integration test completed\n")

def test_neopixel_feedback(trigger_gen, neopixel_display):
    """Test neopixel visual feedback"""
    print("Testing neopixel visual feedback...")
    print("=" * 40)
    
    # Schedule triggers and observe neopixel changes
    print("Scheduling triggers to test neopixel feedback...")
    
    for i in range(trigger_gen.num_triggers):
        print(f"Testing trigger {i} neopixel feedback...")
        trigger_gen.schedule_trigger(i, True)
        time.sleep(0.2)
        
        # Check neopixel state
        gate_state = neopixel_display.get_gate(i + 1)
        print(f"  Gate {i + 1} state: {gate_state} (should be 1/green)")
        
        # Wait for reset
        time.sleep(0.1)
        
        # Check neopixel state after reset
        gate_state = neopixel_display.get_gate(i + 1)
        print(f"  Gate {i + 1} state after reset: {gate_state} (should be 0/red)")
        
        time.sleep(0.2)
    
    print("Neopixel feedback test completed\n")

def test_trigger_patterns(trigger_gen):
    """Test various trigger patterns"""
    print("Testing trigger patterns...")
    print("=" * 40)
    
    patterns = [
        [True, False, False, False, False, False, False],  # Single trigger
        [True, True, False, False, False, False, False],   # Two triggers
        [True, False, True, False, True, False, True],     # Alternating
        [True, True, True, True, True, True, True],        # All triggers
        [False, False, False, False, False, False, False]  # No triggers
    ]
    
    pattern_names = [
        "Single trigger",
        "Two triggers", 
        "Alternating pattern",
        "All triggers",
        "No triggers"
    ]
    
    for i, (pattern, name) in enumerate(zip(patterns, pattern_names)):
        print(f"Testing pattern {i + 1}: {name}")
        print(f"  Pattern: {pattern}")
        
        trigger_gen.schedule_triggers(pattern)
        time.sleep(0.2)
        
        # Check which triggers are active
        active_triggers = []
        for j in range(trigger_gen.num_triggers):
            if trigger_gen.get_trigger_state(j):
                active_triggers.append(j)
        
        print(f"  Active triggers: {active_triggers}")
        time.sleep(0.3)  # Wait for reset
    
    print("Trigger patterns test completed\n")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("Starting Trigger Generator Library Test Suite")
    print("=" * 50)
    
    # Initialize components
    neopixel_display = NeopixelDisplay(pin=0, brightness=0.1)
    trigger_gen = TriggerGenerator(neopixel_display, trigger_pins=[3, 4, 5, 6, 7, 8, 9])
    
    # Create a dummy potentiometer for clock generator
    pot = Potentiometer(pin=2, resolution=12, smoothing_samples=5)
    clock_gen = ClockGenerator(pot, led_pin=15, min_bpm=60, max_bpm=120)
    
    print("Components initialized:")
    print(f"  Neopixel display: 6x20 matrix with gate control")
    print(f"  Trigger generator: {trigger_gen.num_triggers} outputs on pins {trigger_gen.trigger_pins}")
    print(f"  Clock generator: LED on pin 15, BPM range 60-120")
    print()
    
    try:
        # Start trigger generator
        trigger_gen.start()
        
        # Run all test functions
        test_basic_trigger_operations(trigger_gen)
        test_trigger_scheduling(trigger_gen)
        test_trigger_timing(trigger_gen)
        test_trigger_statistics(trigger_gen)
        test_trigger_configuration(trigger_gen)
        test_trigger_testing(trigger_gen)
        test_neopixel_feedback(trigger_gen, neopixel_display)
        test_trigger_patterns(trigger_gen)
        test_clock_integration(trigger_gen, clock_gen)
        
        print("=" * 50)
        print("All automated tests completed successfully!")
        print()
        
        # Interactive test
        print("Starting interactive test...")
        print("This will run for 10 seconds with live trigger patterns")
        print("Watch the neopixel display for visual feedback")
        print()
        
        start_time = time.ticks_ms()
        pattern_index = 0
        patterns = [
            [True, False, False, False, False, False, False],
            [True, True, False, False, False, False, False],
            [True, False, True, False, True, False, True],
            [True, True, True, True, True, True, True]
        ]
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
            # Schedule current pattern
            trigger_gen.schedule_triggers(patterns[pattern_index])
            
            # Show current state
            states = trigger_gen.get_all_trigger_states()
            active_count = sum(states)
            print(f"\rPattern {pattern_index + 1}: {active_count} triggers active | States: {states}", end="")
            
            time.sleep(1)
            pattern_index = (pattern_index + 1) % len(patterns)
        
        print("\n\nInteractive test completed!")
        print("Test suite finished successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        # Clean up
        trigger_gen.stop()
        clock_gen.cleanup()
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("All tests completed successfully!")
    else:
        print("Test suite failed!")
