"""
Comprehensive Sequencer Test

This test combines:
1. Basic clock and potentiometer functionality (with improved BPM range)
2. Neopixel display testing
3. Trigger pattern generation
4. Dual-core architecture testing
5. Real-time monitoring and control

Features:
- Improved BPM range calibration (15-200 BPM)
- Neopixel display patterns
- Trigger output testing
- Comprehensive status monitoring
- Runs until Ctrl+C
"""

import time
import machine
import _thread

# Import the dual-core libraries
from neopixel_display import NeopixelDisplay, RED, GREEN, BLUE, WHITE, CYAN, MAGENTA, PURPLE, GREY, YELLOW, ORANGE, INDIGO, VIOLET
from intercore_communication import InterCoreCommunication
from clock_generator_lp import LowPowerClockGenerator
from potentiometer_lp import LowPowerPotentiometer
from trigger_generator_hp import HighPerformanceTriggerGenerator

def calibrate_bpm_range():
    """Calibrate BPM range to ensure full 15-200 BPM coverage"""
    print("Calibrating BPM range...")
    
    # Read potentiometer to find actual min/max values
    adc = machine.ADC(machine.Pin(1))
    adc.atten(machine.ADC.ATTN_11DB)
    adc.width(machine.ADC.WIDTH_12BIT)
    
    print("Turn potentiometer to minimum position and press Enter...")
    input()  # Wait for user input
    min_raw = adc.read()
    min_normalized = min_raw / 4095.0
    
    print("Turn potentiometer to maximum position and press Enter...")
    input()  # Wait for user input
    max_raw = adc.read()
    max_normalized = max_raw / 4095.0
    
    print(f"Calibration results:")
    print(f"  Min raw: {min_raw} ({min_normalized:.3f})")
    print(f"  Max raw: {max_raw} ({max_normalized:.3f})")
    print(f"  Range: {max_normalized - min_normalized:.3f}")
    
    return min_normalized, max_normalized

def test_neopixel_patterns(neopixel_display):
    """Test various neopixel display patterns"""
    print("Testing neopixel display patterns...")
    
    colors = [RED, GREEN, BLUE, WHITE, CYAN, MAGENTA, PURPLE, GREY, YELLOW, ORANGE, INDIGO, VIOLET]
    color_names = ["RED", "GREEN", "BLUE", "WHITE", "CYAN", "MAGENTA", "PURPLE", "GREY", "YELLOW", "ORANGE", "INDIGO", "VIOLET"]
    
    # Test individual pixels
    print("Testing individual pixels...")
    for i in range(12):
        neopixel_display.set_pixel(i, 0, colors[i])
        time.sleep(0.1)
    
    time.sleep(1)
    neopixel_display.clear()
    
    # Test lines
    print("Testing line drawing...")
    neopixel_display.draw_line(0, 0, 19, 0, RED)
    neopixel_display.draw_line(0, 1, 19, 1, GREEN)
    neopixel_display.draw_line(0, 2, 19, 2, BLUE)
    time.sleep(1)
    
    # Test rectangles
    print("Testing rectangle drawing...")
    neopixel_display.draw_rectangle(2, 3, 6, 5, WHITE, filled=True)
    neopixel_display.draw_rectangle(12, 3, 16, 5, YELLOW, filled=False)
    time.sleep(1)
    
    # Test circles
    print("Testing circle drawing...")
    neopixel_display.draw_circle(10, 2, 2, CYAN, filled=True)
    time.sleep(1)
    
    # Test gates
    print("Testing gate control...")
    for i in range(6):
        neopixel_display.set_gate(i + 1, 1)  # Green
        time.sleep(0.2)
    time.sleep(1)
    
    for i in range(6):
        neopixel_display.set_gate(i + 1, 0)  # Red
        time.sleep(0.2)
    
    neopixel_display.clear()
    print("Neopixel display test completed!")

def comprehensive_sequencer_test():
    """Comprehensive sequencer test with all components"""
    print("Comprehensive Sequencer Test")
    print("=" * 50)
    print("Testing all sequencer components:")
    print("- Clock generation and potentiometer control")
    print("- Neopixel display patterns")
    print("- Trigger pattern generation")
    print("- Dual-core architecture")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Initialize components
        print("Initializing components...")
        neopixel_display = NeopixelDisplay(pin=0, brightness=0.1)
        intercore_comm = InterCoreCommunication()
        
        # Low-power core components with improved BPM range
        clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15, min_bpm=15, max_bpm=200)
        pot_gen = LowPowerPotentiometer(intercore_comm, pin=1, decimation_factor=2, averaging_samples=4)
        
        # High-performance core components
        trigger_gen = HighPerformanceTriggerGenerator(intercore_comm, neopixel_display)
        
        print("Components initialized successfully!")
        print()
        
        # Test neopixel display
        test_neopixel_patterns(neopixel_display)
        print()
        
        # Start low-power core components
        print("Starting low-power core components...")
        pot_gen.start()
        clock_gen.start()
        
        print("Low-power core components started!")
        print("LED on GPIO15 should be flashing at the BPM rate")
        print("BPM rate is controlled by potentiometer on GPIO01")
        print()
        
        # Start high-performance core components
        print("Starting high-performance core components...")
        trigger_gen.start()
        
        print("High-performance core components started!")
        print()
        
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
        
        print("Trigger pattern enabled!")
        print("Pattern: 8 steps with triggers 0-6 in sequence")
        print()
        
        # Main monitoring loop
        print("Starting comprehensive monitoring...")
        print("Format: [Time] Pot->BPM | LED | Pattern | Triggers")
        print("-" * 70)
        
        start_time = time.ticks_ms()
        last_pot_value = 0
        last_bpm = 0
        pattern_display_counter = 0
        
        while True:
            current_time = time.ticks_ms()
            elapsed_ms = time.ticks_diff(current_time, start_time)
            elapsed_sec = elapsed_ms / 1000.0
            
            # Process inter-core messages
            intercore_comm.process_messages()
            
            # Get status from all components
            pot_stats = pot_gen.get_statistics()
            clock_status = clock_gen.get_status()
            trigger_stats = trigger_gen.get_trigger_statistics()
            
            pot_value = pot_stats['normalized_value']
            bpm = pot_stats['bpm_value']
            led_state = clock_status['led_state']
            clock_source = clock_status['clock_source']
            pattern_index = trigger_stats['current_pattern_index']
            pattern_length = trigger_stats['pattern_length']
            active_triggers = sum(trigger_stats['current_states'])
            
            # Update neopixel display with pattern visualization
            if pattern_display_counter % 10 == 0:  # Update every 10 iterations
                neopixel_display.clear()
                
                # Show current pattern step
                for x in range(20):
                    if x < pattern_length:
                        if x == pattern_index:
                            neopixel_display.set_pixel(x, 0, WHITE)  # Current step
                        else:
                            neopixel_display.set_pixel(x, 0, GREY)   # Other steps
                
                # Show active triggers
                for i in range(min(6, len(trigger_stats['current_states']))):
                    if trigger_stats['current_states'][i]:
                        neopixel_display.set_gate(i + 1, 1)  # Green for active
                    else:
                        neopixel_display.set_gate(i + 1, 0)  # Red for inactive
            
            pattern_display_counter += 1
            
            # Print status when values change significantly
            if abs(pot_value - last_pot_value) > 0.01 or abs(bpm - last_bpm) > 1.0:
                print(f"[{elapsed_sec:6.1f}s] Pot:{pot_value:.3f}->{bpm:5.1f}BPM | LED:{'ON ' if led_state else 'OFF'} | Pattern:{pattern_index}/{pattern_length} | Triggers:{active_triggers}")
                last_pot_value = pot_value
                last_bpm = bpm
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\nStopping comprehensive test...")
        
        # Stop all components
        try:
            trigger_gen.stop()
            pot_gen.stop()
            clock_gen.stop()
            neopixel_display.clear()
            print("All components stopped successfully")
        except:
            print("Error stopping components")
        
        print("Comprehensive test completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def simple_bpm_calibration_test():
    """Simple test to verify BPM range reaches 200"""
    print("Simple BPM Calibration Test")
    print("=" * 40)
    print("This test will help verify the BPM range reaches 200")
    print("Turn the potentiometer and watch the BPM values")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Initialize hardware
        led = machine.Pin(15, machine.Pin.OUT)
        adc = machine.ADC(machine.Pin(1))
        adc.atten(machine.ADC.ATTN_11DB)
        adc.width(machine.ADC.WIDTH_12BIT)
        
        # BPM range
        min_bpm = 15.0
        max_bpm = 200.0
        
        # Timing variables
        last_led_toggle = 0
        last_status_print = 0
        led_state = False
        
        print("Starting BPM calibration test...")
        print("Format: [Time] Raw Value | Normalized | BPM | LED State")
        print("-" * 60)
        
        start_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            elapsed_ms = time.ticks_diff(current_time, start_time)
            elapsed_sec = elapsed_ms / 1000.0
            
            # Read potentiometer
            raw_value = adc.read()
            normalized_value = raw_value / 4095.0
            
            # Calculate BPM with improved scaling
            bpm = min_bpm + (normalized_value * (max_bpm - min_bpm))
            
            # Calculate LED toggle period
            beat_period_ms = int((60.0 / bpm) * 1000)
            led_period_ms = beat_period_ms // 2
            
            # Toggle LED at BPM rate
            if time.ticks_diff(current_time, last_led_toggle) >= led_period_ms:
                led_state = not led_state
                if led_state:
                    led.on()
                else:
                    led.off()
                last_led_toggle = current_time
            
            # Print status every second
            if time.ticks_diff(current_time, last_status_print) >= 1000:
                print(f"[{elapsed_sec:6.1f}s] Raw:{raw_value:4d} | Norm:{normalized_value:.3f} | BPM:{bpm:5.1f} | LED:{'ON ' if led_state else 'OFF'}")
                last_status_print = current_time
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping BPM calibration test...")
        try:
            led.off()
            print("LED turned off")
        except:
            pass
        print("BPM calibration test completed!")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Simple BPM calibration test")
    print("2. Comprehensive sequencer test")
    
    try:
        choice = input("Enter choice (1 or 2): ")
        if choice == "1":
            simple_bpm_calibration_test()
        else:
            comprehensive_sequencer_test()
    except:
        # If input fails, run comprehensive test by default
        comprehensive_sequencer_test()
