"""
Simple Clock Generator Test with LED on GPIO15
This script tests the clock generator with the user LED flashing at BPM rate
"""

import machine
import time
import _thread

# Simple clock generator for testing
class SimpleClock:
    def __init__(self, pot_pin=2, led_pin=15, min_bpm=5, max_bpm=240):
        self.pot_pin = pot_pin
        self.led_pin = led_pin
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        
        # Initialize ADC for potentiometer
        self.adc = machine.ADC(machine.Pin(pot_pin))
        self.adc.atten(machine.ADC.ATTN_11DB)
        self.adc.width(machine.ADC.WIDTH_12BIT)
        
        # Initialize LED
        self.led = machine.Pin(led_pin, machine.Pin.OUT)
        self.led.off()
        
        # Clock state
        self.is_running = False
        self.current_bpm = min_bpm
        self.clock_thread = None
        
    def read_potentiometer(self):
        """Read potentiometer and convert to BPM"""
        raw = self.adc.read()
        percentage = (raw / 4095.0) * 100.0
        bpm = self.min_bpm + (percentage / 100.0) * (self.max_bpm - self.min_bpm)
        return bpm
    
    def _clock_thread(self):
        """Clock thread function"""
        while self.is_running:
            # Update BPM from potentiometer
            self.current_bpm = self.read_potentiometer()
            
            # Calculate timing
            period_ms = int((60.0 / self.current_bpm) * 1000)
            pulse_width_ms = 50  # 50ms pulse width
            
            # Flash LED
            self.led.on()
            time.sleep_ms(pulse_width_ms)
            self.led.off()
            
            # Sleep for remaining period
            sleep_time = max(10, period_ms - pulse_width_ms)
            time.sleep_ms(sleep_time)
    
    def start(self):
        """Start the clock"""
        if not self.is_running:
            self.is_running = True
            self.clock_thread = _thread.start_new_thread(self._clock_thread, ())
            print(f"Clock started - LED on GPIO{self.led_pin} will flash at BPM rate")
    
    def stop(self):
        """Stop the clock"""
        if self.is_running:
            self.is_running = False
            self.led.off()
            time.sleep_ms(100)  # Wait for thread to finish
            print("Clock stopped")
    
    def get_bpm(self):
        """Get current BPM"""
        return self.current_bpm

def test_clock_with_led():
    """Test the clock generator with LED"""
    print("ESP32C6-SMD-XIAO Clock Generator Test")
    print("=" * 40)
    print("Potentiometer on pin 2 (A0)")
    print("LED on pin GPIO15")
    print("Turn potentiometer to change BPM (5-240)")
    print("Press Ctrl+C to stop")
    print()
    
    # Initialize clock
    clock = SimpleClock(pot_pin=2, led_pin=15)
    
    try:
        # Start clock
        clock.start()
        
        # Monitor and display BPM
        for i in range(200):  # Run for 20 seconds (200 * 0.1s)
            bpm = clock.get_bpm()
            
            # Create visual bar
            bpm_normalized = (bpm - clock.min_bpm) / (clock.max_bpm - clock.min_bpm)
            bar_length = 20
            bar_fill = int(bpm_normalized * bar_length)
            bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            print(f"\rBPM: {bpm:6.1f} | LED flashing at {bpm:.1f} BPM | [{bar}]", end="")
            time.sleep(0.1)
        
        print("\n\nTest completed!")
        
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    finally:
        clock.stop()

if __name__ == "__main__":
    test_clock_with_led()
