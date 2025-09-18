"""
Simple Potentiometer Test for ESP32C6-SMD-XIAO
This script tests the potentiometer connected to an ADC pin
"""

import machine
import time

def test_potentiometer():
    """Test potentiometer on ADC pin"""
    print("ESP32C6-SMD-XIAO Potentiometer Test")
    print("=" * 40)
    
    # Initialize ADC on pin 2 (D2 on XIAO ESP32-C6)
    # Note: XIAO ESP32-C6 has ADC pins: A0=GPIO2, A1=GPIO3, A2=GPIO4, A3=GPIO5
    adc = machine.ADC(machine.Pin(2))  # A0 pin
    adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V range
    adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution
    
    print("ADC initialized on pin 2 (A0)")
    print("Turn the potentiometer to see values change")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Read raw ADC value
            raw_value = adc.read()
            
            # Convert to voltage (12-bit: 0-4095 -> 0-3.3V)
            voltage = (raw_value / 4095.0) * 3.3
            
            # Convert to percentage
            percentage = (raw_value / 4095.0) * 100.0
            
            # Create a simple visual bar
            bar_length = 20
            bar_fill = int((percentage / 100.0) * bar_length)
            bar = "█" * bar_fill + "░" * (bar_length - bar_fill)
            
            print(f"\rRaw: {raw_value:4d} | Voltage: {voltage:.3f}V | "
                  f"Percentage: {percentage:5.1f}% | [{bar}]", end="")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
        print("Potentiometer test completed!")

if __name__ == "__main__":
    test_potentiometer()


