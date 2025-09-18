"""
Simple Clock and Potentiometer Test

This is a minimal test that just:
1. Reads the potentiometer
2. Flashes the LED at the BPM rate calculated from the potentiometer
3. Prints status every second
4. Runs until Ctrl+C
"""

import time
import machine

def simple_clock_pot_test():
    """Simple test of clock generation and potentiometer reading"""
    print("Simple Clock and Potentiometer Test")
    print("=" * 40)
    print("Reading potentiometer on GPIO01")
    print("Flashing LED on GPIO15 at BPM rate")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Initialize hardware
        print("Initializing hardware...")
        
        # LED on GPIO15
        led = machine.Pin(15, machine.Pin.OUT)
        led.off()
        
        # Potentiometer on GPIO01
        adc = machine.ADC(machine.Pin(1))
        adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range
        adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution
        
        print("Hardware initialized successfully!")
        print()
        
        # BPM range
        min_bpm = 15.0
        max_bpm = 200.0
        
        # Timing variables
        last_led_toggle = 0
        last_status_print = 0
        led_state = False
        
        print("Starting main loop...")
        print("Format: [Time] Pot Value -> BPM | LED State")
        print("-" * 50)
        
        start_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            elapsed_ms = time.ticks_diff(current_time, start_time)
            elapsed_sec = elapsed_ms / 1000.0
            
            # Read potentiometer
            raw_value = adc.read()
            normalized_value = raw_value / 4095.0  # 12-bit ADC
            
            # Calculate BPM
            bpm = min_bpm + (normalized_value * (max_bpm - min_bpm))
            
            # Calculate LED toggle period (half the beat period)
            beat_period_ms = int((60.0 / bpm) * 1000)  # Period in ms
            led_period_ms = beat_period_ms // 2  # LED toggles twice per beat
            
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
                print(f"[{elapsed_sec:6.1f}s] Pot: {normalized_value:.3f} -> {bpm:5.1f} BPM | LED: {'ON ' if led_state else 'OFF'}")
                last_status_print = current_time
            
            # Small delay to prevent excessive CPU usage
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping test...")
        try:
            led.off()
            print("LED turned off")
        except:
            pass
        print("Test completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_clock_pot_test()
