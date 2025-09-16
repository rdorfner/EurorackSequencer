"""
Test Program for Neopixel Display Library

This test program exercises all functionality of the neopixel display library
including pixel operations, drawing functions, and gate control. The test
demonstrates various drawing primitives, color usage, and coordinate system
validation.

Algorithm Overview:
- Initialize display and clear screen
- Test individual pixel operations
- Test line drawing in various directions
- Test rectangle drawing (outline and filled)
- Test circle drawing (outline and filled)
- Test gate control functionality
- Display color palette demonstration
- Coordinate system boundary testing
"""

import time
import sys
import os

# Add the drivers directory to the path to import our library
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'drivers'))

from neopixel_display import NeopixelDisplay, RED, GREEN, BLUE, WHITE, CYAN, MAGENTA, PURPLE, GREY, YELLOW, ORANGE, INDIGO, VIOLET

def test_basic_operations(display):
    """Test basic pixel operations and coordinate system"""
    print("Testing basic pixel operations...")
    
    # Test individual pixels at corners
    display.set_pixel(0, 0, RED)      # Bottom-left
    display.set_pixel(19, 0, GREEN)   # Bottom-right
    display.set_pixel(0, 5, BLUE)     # Top-left
    display.set_pixel(19, 5, WHITE)   # Top-right
    
    time.sleep(1)
    
    # Test center pixel
    display.set_pixel(10, 3, YELLOW)
    time.sleep(1)
    
    # Clear and test coordinate validation
    display.clear()
    print("Basic operations test completed")

def test_line_drawing(display):
    """Test line drawing in various directions"""
    print("Testing line drawing...")
    
    # Horizontal lines
    display.draw_line(0, 0, 19, 0, RED)      # Bottom edge
    display.draw_line(0, 5, 19, 5, GREEN)    # Top edge
    time.sleep(1)
    
    # Vertical lines
    display.draw_line(0, 0, 0, 5, BLUE)      # Left edge
    display.draw_line(19, 0, 19, 5, WHITE)   # Right edge
    time.sleep(1)
    
    # Diagonal lines
    display.draw_line(0, 0, 19, 5, CYAN)     # Main diagonal
    display.draw_line(19, 0, 0, 5, MAGENTA)  # Anti-diagonal
    time.sleep(1)
    
    # Clear for next test
    display.clear()
    print("Line drawing test completed")

def test_rectangle_drawing(display):
    """Test rectangle drawing (outline and filled)"""
    print("Testing rectangle drawing...")
    
    # Outline rectangles
    display.draw_rectangle(2, 1, 6, 4, RED, filled=False)
    time.sleep(1)
    
    display.draw_rectangle(12, 1, 6, 4, GREEN, filled=False)
    time.sleep(1)
    
    # Filled rectangles
    display.draw_rectangle(2, 1, 6, 4, BLUE, filled=True)
    time.sleep(1)
    
    display.draw_rectangle(12, 1, 6, 4, YELLOW, filled=True)
    time.sleep(1)
    
    # Clear for next test
    display.clear()
    print("Rectangle drawing test completed")

def test_circle_drawing(display):
    """Test circle drawing (outline and filled)"""
    print("Testing circle drawing...")
    
    # Outline circles
    display.draw_circle(5, 3, 2, RED, filled=False)
    time.sleep(1)
    
    display.draw_circle(15, 3, 2, GREEN, filled=False)
    time.sleep(1)
    
    # Filled circles
    display.draw_circle(5, 3, 2, BLUE, filled=True)
    time.sleep(1)
    
    display.draw_circle(15, 3, 2, WHITE, filled=True)
    time.sleep(1)
    
    # Clear for next test
    display.clear()
    print("Circle drawing test completed")

def test_gate_control(display):
    """Test gate control functionality"""
    print("Testing gate control...")
    
    # Set all gates to off (red)
    for gate in range(1, 7):
        display.set_gate(gate, 0)
    time.sleep(1)
    
    # Turn on gates one by one (green)
    for gate in range(1, 7):
        display.set_gate(gate, 1)
        time.sleep(0.5)
    
    # Turn off gates one by one (red)
    for gate in range(1, 7):
        display.set_gate(gate, 0)
        time.sleep(0.5)
    
    print("Gate control test completed")

def test_color_palette(display):
    """Display all available colors"""
    print("Testing color palette...")
    
    colors = [RED, GREEN, BLUE, WHITE, CYAN, MAGENTA, PURPLE, GREY, YELLOW, ORANGE, INDIGO, VIOLET]
    color_names = ["RED", "GREEN", "BLUE", "WHITE", "CYAN", "MAGENTA", "PURPLE", "GREY", "YELLOW", "ORANGE", "INDIGO", "VIOLET"]
    
    # Display each color as a small rectangle
    for i, (color, name) in enumerate(zip(colors, color_names)):
        x = (i % 4) * 5
        y = (i // 4) * 2
        display.draw_rectangle(x, y, 4, 2, color, filled=True)
        print(f"Displaying {name}")
        time.sleep(0.5)
    
    time.sleep(2)
    display.clear()
    print("Color palette test completed")

def test_coordinate_boundaries(display):
    """Test coordinate system boundaries"""
    print("Testing coordinate boundaries...")
    
    # Test boundary conditions
    try:
        display.set_pixel(-1, 0, RED)  # Should fail
    except ValueError:
        print("✓ Correctly rejected negative x coordinate")
    
    try:
        display.set_pixel(20, 0, RED)  # Should fail
    except ValueError:
        print("✓ Correctly rejected x coordinate >= width")
    
    try:
        display.set_pixel(0, -1, RED)  # Should fail
    except ValueError:
        print("✓ Correctly rejected negative y coordinate")
    
    try:
        display.set_pixel(0, 6, RED)  # Should fail
    except ValueError:
        print("✓ Correctly rejected y coordinate >= height")
    
    # Test valid boundary pixels
    display.set_pixel(0, 0, GREEN)    # Bottom-left
    display.set_pixel(19, 5, BLUE)    # Top-right
    time.sleep(1)
    
    display.clear()
    print("Coordinate boundary test completed")

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("Starting Neopixel Display Library Test Suite")
    print("=" * 50)
    
    # Initialize display
    display = NeopixelDisplay(pin=0, brightness=0.1)
    print("Display initialized on pin 0 with 10% brightness")
    
    try:
        # Run all test functions
        test_basic_operations(display)
        test_line_drawing(display)
        test_rectangle_drawing(display)
        test_circle_drawing(display)
        test_gate_control(display)
        test_color_palette(display)
        test_coordinate_boundaries(display)
        
        print("=" * 50)
        print("All tests completed successfully!")
        
        # Final demonstration
        print("Running final demonstration...")
        display.clear()
        
        # Draw a pattern using all features
        display.draw_rectangle(0, 0, 20, 6, WHITE, filled=False)  # Border
        display.draw_line(0, 0, 19, 5, RED)                       # Diagonal
        display.draw_line(19, 0, 0, 5, GREEN)                     # Anti-diagonal
        display.draw_circle(10, 3, 2, BLUE, filled=True)          # Center circle
        
        # Set all gates to on
        for gate in range(1, 7):
            display.set_gate(gate, 1)
        
        print("Final demonstration complete!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("Test suite completed successfully!")
    else:
        print("Test suite failed!")
