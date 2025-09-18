"""
Test Program for Dual-Core Sequencer Architecture

This test program exercises the dual-core sequencer functionality including
inter-core communication, low-power core clock generation, potentiometer reading,
and high-performance core trigger generation with neopixel feedback.

Algorithm Overview:
- Initialize inter-core communication system
- Start low-power core components (clock generator, potentiometer)
- Start high-performance core components (trigger generator, neopixel display)
- Test various trigger patterns and clock sources
- Demonstrate external clock input functionality
- Provide comprehensive testing and monitoring
"""

import time

# Import the dual-core libraries directly (flat file system)
from neopixel_display import NeopixelDisplay
from intercore_communication import InterCoreCommunication
from clock_generator_lp import LowPowerClockGenerator
from potentiometer_lp import LowPowerPotentiometer
from trigger_generator_hp import HighPerformanceTriggerGenerator

def test_intercore_communication(intercore_comm):
    """Test inter-core communication functionality"""
    print("Testing inter-core communication...")
    print("=" * 40)
    
    # Test shared memory operations
    print("Testing shared memory operations...")
    intercore_comm.set_shared_data('test_value', 42)
    test_value = intercore_comm.get_shared_data('test_value')
    print(f"Shared memory test: {test_value}")
    
    # Test message sending
    print("Testing message sending...")
    intercore_comm.send_clock_update(120.0, 'internal')
    intercore_comm.send_trigger_pattern([True, False, True, False, True, False, True])
    
    # Test system status
    status = intercore_comm.get_system_status()
    print("System status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("Inter-core communication test completed\n")

def test_low_power_clock_generator(clock_gen):
    """Test low-power clock generator"""
    print("Testing low-power clock generator...")
    print("=" * 40)
    
    # Test BPM setting
    print("Testing BPM setting...")
    test_bpms = [60, 120, 180, 240]
    for bpm in test_bpms:
        clock_gen.set_bpm(bpm)
        time.sleep(0.5)
        status = clock_gen.get_status()
        print(f"BPM set to {bpm}, actual: {status['current_bpm']:.1f}")
    
    # Test external clock setup
    print("Testing external clock setup...")
    clock_gen.setup_external_clock_input(10)  # Pin 10 for external clock
    clock_gen.enable_external_clock()
    
    # Test clock start/stop
    print("Testing clock start/stop...")
    clock_gen.start()
    time.sleep(2)
    clock_gen.stop()
    
    print("Low-power clock generator test completed\n")

def test_low_power_potentiometer(pot_gen):
    """Test low-power potentiometer"""
    print("Testing low-power potentiometer...")
    print("=" * 40)
    
    # Test configuration
    print("Testing potentiometer configuration...")
    pot_gen.set_sampling_rate(100)  # 10 Hz
    pot_gen.set_decimation_factor(4)
    pot_gen.set_averaging_samples(8)
    pot_gen.set_bpm_range(10, 200)
    
    # Test start/stop
    print("Testing potentiometer start/stop...")
    pot_gen.start()
    time.sleep(3)
    
    # Get statistics
    stats = pot_gen.get_statistics()
    print("Potentiometer statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    pot_gen.stop()
    print("Low-power potentiometer test completed\n")

def test_high_performance_trigger_generator(trigger_gen):
    """Test high-performance trigger generator"""
    print("Testing high-performance trigger generator...")
    print("=" * 40)
    
    # Test trigger scheduling
    print("Testing trigger scheduling...")
    trigger_gen.schedule_trigger(0, True)
    trigger_gen.schedule_trigger(2, True)
    trigger_gen.schedule_trigger(4, True)
    
    # Test pattern creation
    print("Testing pattern creation...")
    simple_pattern = "1010101010101010"  # Alternating pattern
    trigger_gen.create_simple_pattern(simple_pattern)
    
    # Test alternating pattern
    trigger_gen.create_alternating_pattern(1, 8)  # Trigger 1, 8 steps
    
    # Test pattern enable/disable
    trigger_gen.enable_pattern(True)
    time.sleep(1)
    trigger_gen.enable_pattern(False)
    
    # Test statistics
    stats = trigger_gen.get_trigger_statistics()
    print("Trigger generator statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("High-performance trigger generator test completed\n")

def test_dual_core_integration(intercore_comm, clock_gen, pot_gen, trigger_gen, neopixel_display):
    """Test integrated dual-core functionality"""
    print("Testing dual-core integration...")
    print("=" * 40)
    
    # Start all components
    print("Starting all dual-core components...")
    clock_gen.start()
    pot_gen.start()
    trigger_gen.start()
    
    # Setup a test pattern
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
    
    print("Running integrated test for 10 seconds...")
    print("Watch the neopixel display for visual feedback")
    print("Clock LED should be blinking on GPIO15")
    
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
        # Process inter-core messages
        intercore_comm.process_messages()
        
        # Get system status
        status = intercore_comm.get_system_status()
        clock_status = clock_gen.get_status()
        pot_stats = pot_gen.get_statistics()
        trigger_stats = trigger_gen.get_trigger_statistics()
        
        # Display status
        print(f"\rClock: {clock_status['current_bpm']:.1f} BPM ({clock_status['clock_source']}) | "
              f"Pot: {pot_stats['bpm_value']:.1f} BPM | "
              f"Triggers: {sum(trigger_stats['current_states'])} active | "
              f"Pattern: {trigger_stats['current_pattern_index']}/{trigger_stats['pattern_length']}", end="")
        
        time.sleep(0.1)
    
    print("\n\nStopping all components...")
    trigger_gen.stop()
    pot_gen.stop()
    clock_gen.stop()
    
    print("Dual-core integration test completed\n")

def test_external_clock_functionality(clock_gen, intercore_comm):
    """Test external clock input functionality"""
    print("Testing external clock functionality...")
    print("=" * 40)
    
    # Setup external clock
    clock_gen.setup_external_clock_input(10)  # Pin 10
    clock_gen.start()
    
    print("External clock test setup complete")
    print("Connect an external clock signal to pin 10 to test")
    print("The system should automatically switch to external clock")
    print("Press Ctrl+C to stop test")
    
    try:
        for i in range(50):  # Run for 5 seconds
            status = clock_gen.get_status()
            system_status = intercore_comm.get_system_status()
            
            print(f"\rClock source: {status['clock_source']} | "
                  f"BPM: {status['current_bpm']:.1f} | "
                  f"External active: {status['external_clock_active']} | "
                  f"External freq: {status['external_clock_frequency']:.1f} BPM", end="")
            
            time.sleep(0.1)
        
        print("\n\nExternal clock test completed")
        
    except KeyboardInterrupt:
        print("\n\nExternal clock test interrupted")
    
    clock_gen.stop()

def run_comprehensive_test():
    """Run all dual-core tests in sequence"""
    print("Starting Dual-Core Sequencer Test Suite")
    print("=" * 50)
    
    # Initialize components
    neopixel_display = NeopixelDisplay(pin=0, brightness=0.1)
    intercore_comm = InterCoreCommunication()
    
    # Low-power core components
    clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15, min_bpm=60, max_bpm=180)
    pot_gen = LowPowerPotentiometer(intercore_comm, pin=2, decimation_factor=4, averaging_samples=8)
    
    # High-performance core components
    trigger_gen = HighPerformanceTriggerGenerator(intercore_comm, neopixel_display)
    
    print("Dual-core components initialized:")
    print(f"  Neopixel display: 6x20 matrix with gate control")
    print(f"  Inter-core communication: Active")
    print(f"  Low-power clock generator: GPIO15 LED, 60-180 BPM")
    print(f"  Low-power potentiometer: Pin 2, decimation factor 4")
    print(f"  High-performance trigger generator: 7 outputs")
    print()
    
    try:
        # Run all test functions
        test_intercore_communication(intercore_comm)
        test_low_power_clock_generator(clock_gen)
        test_low_power_potentiometer(pot_gen)
        test_high_performance_trigger_generator(trigger_gen)
        test_dual_core_integration(intercore_comm, clock_gen, pot_gen, trigger_gen, neopixel_display)
        
        print("=" * 50)
        print("All automated tests completed successfully!")
        print()
        
        # Interactive external clock test
        print("Starting interactive external clock test...")
        test_external_clock_functionality(clock_gen, intercore_comm)
        
        print("Test suite finished successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        # Clean up
        trigger_gen.stop()
        pot_gen.stop()
        clock_gen.stop()
        intercore_comm.stop_communication()
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("All dual-core tests completed successfully!")
    else:
        print("Dual-core test suite failed!")
