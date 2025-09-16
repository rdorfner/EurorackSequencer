"""
Test Program for Rotary Encoder Library

This test program exercises all functionality of the rotary encoder library
including rotation detection, button press/release, callbacks, and various
operating modes. The test demonstrates both polling and callback-based operation.

Algorithm Overview:
- Initialize rotary encoder with specified pins
- Test basic rotation detection and position tracking
- Test button press/release detection with debouncing
- Demonstrate callback functionality for rotation and button events
- Test various operating modes (polling, waiting, status monitoring)
- Provide real-time monitoring with visual feedback
- Test configuration changes and edge cases
"""

import time
import sys
import os

# Add the drivers directory to the path to import our library
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drivers'))

from rotary_encoder import RotaryEncoder

def test_basic_rotation(encoder):
    """Test basic rotation detection"""
    print("Testing basic rotation detection...")
    print("=" * 40)
    print("Rotate the encoder to test position tracking")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        for i in range(100):  # Run for 100 samples
            encoder.update()
            
            position = encoder.get_position()
            direction = encoder.get_direction()
            
            # Create visual indicator for direction
            if direction > 0:
                direction_indicator = "CW"
            elif direction < 0:
                direction_indicator = "CCW"
            else:
                direction_indicator = "---"
            
            print(f"\rPosition: {position:4d} | Direction: {direction_indicator:3s}", end="")
            time.sleep(0.05)
        
        print("\n\nBasic rotation test completed\n")
        
    except KeyboardInterrupt:
        print("\n\nBasic rotation test interrupted\n")

def test_button_functionality(encoder):
    """Test button press/release functionality"""
    print("Testing button functionality...")
    print("=" * 40)
    print("Press and release the button to test detection")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        for i in range(200):  # Run for 200 samples
            encoder.update()
            
            button_pressed = encoder.is_button_pressed()
            was_pressed = encoder.was_button_pressed()
            was_released = encoder.was_button_released()
            
            # Create visual indicators
            button_status = "PRESSED" if button_pressed else "RELEASED"
            press_indicator = "✓" if was_pressed else " "
            release_indicator = "✓" if was_released else " "
            
            print(f"\rButton: {button_status:8s} | Press: {press_indicator} | Release: {release_indicator}", end="")
            time.sleep(0.05)
        
        print("\n\nButton functionality test completed\n")
        
    except KeyboardInterrupt:
        print("\n\nButton functionality test interrupted\n")

def test_callbacks(encoder):
    """Test callback functionality"""
    print("Testing callback functionality...")
    print("=" * 40)
    
    # Set up callbacks
    rotation_count = 0
    button_press_count = 0
    button_release_count = 0
    
    def rotation_callback(direction, position):
        nonlocal rotation_count
        rotation_count += 1
        direction_text = "CW" if direction > 0 else "CCW"
        print(f"Rotation callback: {direction_text} at position {position}")
    
    def button_callback(pressed):
        nonlocal button_press_count, button_release_count
        if pressed:
            button_press_count += 1
            print(f"Button callback: PRESSED (count: {button_press_count})")
        else:
            button_release_count += 1
            print(f"Button callback: RELEASED (count: {button_release_count})")
    
    encoder.set_rotation_callback(rotation_callback)
    encoder.set_button_callback(button_callback)
    
    print("Callbacks set up. Rotate encoder and press button to test callbacks.")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        for i in range(300):  # Run for 300 samples
            encoder.update()
            time.sleep(0.05)
        
        print(f"\nCallback test completed:")
        print(f"  Rotation callbacks: {rotation_count}")
        print(f"  Button press callbacks: {button_press_count}")
        print(f"  Button release callbacks: {button_release_count}")
        print()
        
    except KeyboardInterrupt:
        print(f"\nCallback test interrupted:")
        print(f"  Rotation callbacks: {rotation_count}")
        print(f"  Button press callbacks: {button_press_count}")
        print(f"  Button release callbacks: {button_release_count}")
        print()

def test_position_reset(encoder):
    """Test position reset functionality"""
    print("Testing position reset...")
    print("=" * 40)
    
    # Get initial position
    initial_position = encoder.get_position()
    print(f"Initial position: {initial_position}")
    
    # Reset to 0
    encoder.reset_position(0)
    print(f"Position after reset to 0: {encoder.get_position()}")
    
    # Reset to 100
    encoder.reset_position(100)
    print(f"Position after reset to 100: {encoder.get_position()}")
    
    # Reset to -50
    encoder.reset_position(-50)
    print(f"Position after reset to -50: {encoder.get_position()}")
    
    print("Position reset test completed\n")

def test_wait_functions(encoder):
    """Test wait functions"""
    print("Testing wait functions...")
    print("=" * 40)
    
    # Test wait for rotation
    print("Testing wait_for_rotation (5 second timeout)...")
    print("Rotate the encoder within 5 seconds")
    
    if encoder.wait_for_rotation(5000):
        print(f"Rotation detected! New position: {encoder.get_position()}")
    else:
        print("No rotation detected within timeout")
    
    # Test wait for button press
    print("\nTesting wait_for_button_press (5 second timeout)...")
    print("Press the button within 5 seconds")
    
    if encoder.wait_for_button_press(5000):
        print("Button press detected!")
    else:
        print("No button press detected within timeout")
    
    print("Wait functions test completed\n")

def test_polling(encoder):
    """Test polling functionality"""
    print("Testing polling functionality...")
    print("=" * 40)
    print("Polling encoder for 3 seconds...")
    print("Rotate encoder and press button during polling")
    
    initial_position = encoder.get_position()
    initial_time = time.ticks_ms()
    
    encoder.poll(3000)  # Poll for 3 seconds
    
    final_position = encoder.get_position()
    final_time = time.ticks_ms()
    
    print(f"Polling completed:")
    print(f"  Initial position: {initial_position}")
    print(f"  Final position: {final_position}")
    print(f"  Position change: {final_position - initial_position}")
    print(f"  Polling duration: {time.ticks_diff(final_time, initial_time)}ms")
    print()

def test_debounce_settings(encoder):
    """Test debounce settings"""
    print("Testing debounce settings...")
    print("=" * 40)
    
    # Test different debounce delays
    debounce_delays = [10, 50, 100, 200]
    
    for delay in debounce_delays:
        print(f"Testing debounce delay: {delay}ms")
        encoder.set_debounce_delay(delay)
        
        # Test button with this debounce setting
        print("  Press button quickly multiple times")
        time.sleep(2)
        
        # Count button presses
        press_count = 0
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 2000:
            encoder.update()
            if encoder.was_button_pressed():
                press_count += 1
            time.sleep_ms(10)
        
        print(f"  Button presses detected: {press_count}")
        print()
    
    # Reset to default
    encoder.set_debounce_delay(50)
    print("Debounce settings test completed\n")

def test_status_monitoring(encoder):
    """Test status monitoring"""
    print("Testing status monitoring...")
    print("=" * 40)
    
    # Get initial status
    status = encoder.get_status()
    print("Initial status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nMonitoring status for 5 seconds...")
    print("Rotate encoder and press button to see changes")
    print()
    
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
        encoder.update()
        
        status = encoder.get_status()
        print(f"\rPosition: {status['position']:4d} | "
              f"Direction: {status['direction']:2d} | "
              f"Button: {'PRESSED' if status['button_pressed'] else 'RELEASED':8s}", end="")
        
        time.sleep(0.1)
    
    print("\n\nStatus monitoring test completed\n")

def test_edge_cases(encoder):
    """Test edge cases and error conditions"""
    print("Testing edge cases...")
    print("=" * 40)
    
    # Test position reset with extreme values
    print("Testing extreme position values...")
    encoder.reset_position(1000000)
    print(f"Position after reset to 1000000: {encoder.get_position()}")
    
    encoder.reset_position(-1000000)
    print(f"Position after reset to -1000000: {encoder.get_position()}")
    
    # Test debounce delay edge cases
    print("\nTesting debounce delay edge cases...")
    encoder.set_debounce_delay(0)
    print(f"Debounce delay set to 0: {encoder.get_status()['debounce_delay']}")
    
    encoder.set_debounce_delay(1000)
    print(f"Debounce delay set to 1000: {encoder.get_status()['debounce_delay']}")
    
    # Reset to default
    encoder.set_debounce_delay(50)
    
    print("Edge cases test completed\n")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("Starting Rotary Encoder Library Test Suite")
    print("=" * 50)
    
    # Initialize rotary encoder
    # Note: These pin numbers should be adjusted based on your hardware setup
    encoder = RotaryEncoder(pin_a=3, pin_b=4, pin_button=5, pull_up=True)
    
    print("Rotary encoder initialized:")
    print(f"  Encoder A pin: {encoder.pin_a}")
    print(f"  Encoder B pin: {encoder.pin_b}")
    print(f"  Button pin: {encoder.pin_button}")
    print(f"  Pull-up resistors: Enabled")
    print()
    
    try:
        # Run all test functions
        test_position_reset(encoder)
        test_basic_rotation(encoder)
        test_button_functionality(encoder)
        test_callbacks(encoder)
        test_wait_functions(encoder)
        test_polling(encoder)
        test_debounce_settings(encoder)
        test_status_monitoring(encoder)
        test_edge_cases(encoder)
        
        print("=" * 50)
        print("All automated tests completed successfully!")
        print()
        
        # Final interactive test
        print("Starting final interactive test...")
        print("This will run for 10 seconds with real-time monitoring")
        print("Rotate encoder and press button to see all functionality")
        print()
        
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
            encoder.update()
            
            status = encoder.get_status()
            position = status['position']
            direction = status['direction']
            button_pressed = status['button_pressed']
            
            # Create visual indicators
            direction_text = "CW" if direction > 0 else "CCW" if direction < 0 else "---"
            button_text = "PRESSED" if button_pressed else "RELEASED"
            
            print(f"\rPosition: {position:4d} | Direction: {direction_text:3s} | Button: {button_text:8s}", end="")
            time.sleep(0.1)
        
        print("\n\nFinal interactive test completed!")
        print("Test suite finished successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("All tests completed successfully!")
    else:
        print("Test suite failed!")
