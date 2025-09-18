"""
Simple Dual-Core Hardware Test

This test demonstrates actual dual-core functionality:
- Low-power core: Reads potentiometer and flashes LED at BPM rate (15-200 BPM)
- High-performance core: Prints status information and processes messages
- Runs until Ctrl+C is received
"""

import time
import _thread

# Import the dual-core libraries
from neopixel_display import NeopixelDisplay
from intercore_communication import InterCoreCommunication
from clock_generator_lp import LowPowerClockGenerator
from potentiometer_lp import LowPowerPotentiometer
from trigger_generator_hp import HighPerformanceTriggerGenerator

def simple_dual_core_test():
    """Simple dual-core test with observable hardware behavior"""
    print("Simple Dual-Core Hardware Test")
    print("=" * 40)
    print("Low-power core: Reads potentiometer, flashes LED at BPM rate")
    print("High-performance core: Prints status information")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Initialize components
        print("Initializing components...")
        neopixel_display = NeopixelDisplay(pin=0, brightness=0.1)
        intercore_comm = InterCoreCommunication()
        
        # Low-power core components
        clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15, min_bpm=15, max_bpm=200)
        pot_gen = LowPowerPotentiometer(intercore_comm, pin=2, decimation_factor=2, averaging_samples=4)
        
        # High-performance core components  
        trigger_gen = HighPerformanceTriggerGenerator(intercore_comm, neopixel_display)
        
        print("Components initialized successfully!")
        print()
        
        # Start low-power core components
        print("Starting low-power core components...")
        pot_gen.start()
        clock_gen.start()
        
        print("Low-power core components started!")
        print("LED on GPIO15 should now be flashing at the BPM rate")
        print("BPM rate is controlled by potentiometer on pin 2")
        print()
        
        # Start high-performance core components
        print("Starting high-performance core components...")
        trigger_gen.start()
        
        print("High-performance core components started!")
        print()
        
        # Main loop - high-performance core prints status
        print("Starting status monitoring...")
        print("Format: [Time] Pot Value -> BPM | LED State | Clock Source")
        print("-" * 60)
        
        start_time = time.ticks_ms()
        last_pot_value = 0
        last_bpm = 0
        
        while True:
            current_time = time.ticks_ms()
            elapsed_ms = time.ticks_diff(current_time, start_time)
            elapsed_sec = elapsed_ms / 1000.0
            
            # Process inter-core messages
            intercore_comm.process_messages()
            
            # Get status from low-power core
            pot_stats = pot_gen.get_statistics()
            clock_status = clock_gen.get_status()
            
            pot_value = pot_stats['normalized_value']
            bpm = pot_stats['bpm_value']
            led_state = clock_status['led_state']
            clock_source = clock_status['clock_source']
            
            # Only print when values change significantly
            if abs(pot_value - last_pot_value) > 0.01 or abs(bpm - last_bpm) > 1.0:
                print(f"[{elapsed_sec:6.1f}s] Pot: {pot_value:.3f} -> {bpm:5.1f} BPM | LED: {'ON ' if led_state else 'OFF'} | Source: {clock_source}")
                last_pot_value = pot_value
                last_bpm = bpm
            
            # Small delay to prevent excessive printing
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nStopping test...")
        
        # Stop all components
        try:
            trigger_gen.stop()
            pot_gen.stop()
            clock_gen.stop()
            print("All components stopped successfully")
        except:
            print("Error stopping components")
        
        print("Test completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_dual_core_test()
