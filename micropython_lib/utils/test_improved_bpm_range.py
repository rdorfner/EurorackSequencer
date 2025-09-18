"""
Improved BPM Range Test

This test compensates for the potentiometer not reaching full scale
by adjusting the BPM calculation to use the actual min/max values
observed from the potentiometer.
"""

import time
import machine

def improved_bpm_test():
    """Test with improved BPM range calculation"""
    print("Improved BPM Range Test")
    print("=" * 40)
    print("This test compensates for potentiometer range limitations")
    print("Turn the potentiometer and watch the BPM values")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Initialize hardware
        led = machine.Pin(15, machine.Pin.OUT)
        adc = machine.ADC(machine.Pin(1))
        adc.atten(machine.ADC.ATTN_11DB)
        adc.width(machine.ADC.WIDTH_12BIT)
        
        # Target BPM range
        target_min_bpm = 15.0
        target_max_bpm = 200.0
        
        # Observed potentiometer range (from previous test)
        observed_min_raw = 0      # Minimum observed value
        observed_max_raw = 3311   # Maximum observed value (from test)
        
        # Calculate scaling factors
        observed_range = observed_max_raw - observed_min_raw
        scale_factor = 4095.0 / observed_range  # Scale to full range
        
        print(f"Potentiometer calibration:")
        print(f"  Observed min: {observed_min_raw}")
        print(f"  Observed max: {observed_max_raw}")
        print(f"  Observed range: {observed_range}")
        print(f"  Scale factor: {scale_factor:.3f}")
        print()
        
        # Timing variables
        last_led_toggle = 0
        last_status_print = 0
        led_state = False
        
        print("Starting improved BPM test...")
        print("Format: [Time] Raw | Scaled | BPM | LED State")
        print("-" * 60)
        
        start_time = time.ticks_ms()
        
        while True:
            current_time = time.ticks_ms()
            elapsed_ms = time.ticks_diff(current_time, start_time)
            elapsed_sec = elapsed_ms / 1000.0
            
            # Read potentiometer
            raw_value = adc.read()
            
            # Apply scaling to compensate for limited range
            scaled_value = (raw_value - observed_min_raw) * scale_factor
            scaled_value = max(0, min(4095, scaled_value))  # Clamp to valid range
            normalized_value = scaled_value / 4095.0
            
            # Calculate BPM with full range
            bpm = target_min_bpm + (normalized_value * (target_max_bpm - target_min_bpm))
            
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
                print(f"[{elapsed_sec:6.1f}s] Raw:{raw_value:4d} | Scaled:{scaled_value:4.0f} | BPM:{bpm:5.1f} | LED:{'ON ' if led_state else 'OFF'}")
                last_status_print = current_time
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping improved BPM test...")
        try:
            led.off()
            print("LED turned off")
        except:
            pass
        print("Improved BPM test completed!")

if __name__ == "__main__":
    improved_bpm_test()
