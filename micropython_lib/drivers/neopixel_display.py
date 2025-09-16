"""
Neopixel Display Library for ESP32-C6 Sequencer Project

This module provides a comprehensive interface for controlling a 6x20 neopixel display
with additional gate control pixels. The display uses a bottom-left origin coordinate
system where (0,0) is pixel 0, and the matrix extends to (19,5) at pixel 119.
Six additional gate pixels (120-125) provide gate control functionality.

Algorithm Overview:
- Coordinate conversion from (x,y) to linear pixel index
- Color management with predefined color constants
- Drawing primitives (pixels, lines, rectangles, circles)
- Gate control with red/green state indication
- Display buffer management and update operations
"""

import machine
import neopixel
import math

# Color constants (RGB values)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
INDIGO = (75, 0, 130)
VIOLET = (238, 130, 238)

# Display configuration
DISPLAY_WIDTH = 20
DISPLAY_HEIGHT = 6
TOTAL_DISPLAY_PIXELS = DISPLAY_WIDTH * DISPLAY_HEIGHT  # 120 pixels
GATE_PIXELS = 6
TOTAL_PIXELS = TOTAL_DISPLAY_PIXELS + GATE_PIXELS  # 126 pixels

class NeopixelDisplay:
    def __init__(self, pin=0, brightness=0.1):
        """
        Initialize the neopixel display
        
        Args:
            pin: GPIO pin number for neopixel data line (default: 0 for d0)
            brightness: Display brightness 0.0-1.0 (default: 0.1 for 10%)
        """
        self.pin = pin
        self.brightness = brightness
        self.np = neopixel.NeoPixel(machine.Pin(pin), TOTAL_PIXELS)
        self.clear()
        
    def _xy_to_index(self, x, y):
        """
        Convert (x,y) coordinates to linear pixel index
        Origin is bottom-left, x increases right, y increases up
        
        Args:
            x: Column (0-19)
            y: Row (0-5)
            
        Returns:
            Linear pixel index (0-119)
        """
        if not (0 <= x < DISPLAY_WIDTH and 0 <= y < DISPLAY_HEIGHT):
            raise ValueError(f"Coordinates ({x},{y}) out of range")
        return y * DISPLAY_WIDTH + x
    
    def _gate_index(self, gate_num):
        """
        Get pixel index for gate control pixel
        
        Args:
            gate_num: Gate number (1-6)
            
        Returns:
            Linear pixel index (120-125)
        """
        if not (1 <= gate_num <= GATE_PIXELS):
            raise ValueError(f"Gate number {gate_num} out of range (1-6)")
        return TOTAL_DISPLAY_PIXELS + gate_num - 1
    
    def set_pixel(self, x, y, color):
        """
        Set a single pixel at (x,y) coordinates
        
        Args:
            x: Column (0-19)
            y: Row (0-5)
            color: RGB tuple (r, g, b)
        """
        index = self._xy_to_index(x, y)
        self.np[index] = color
        self.np.write()
    
    def get_pixel(self, x, y):
        """
        Get color of pixel at (x,y) coordinates
        
        Args:
            x: Column (0-19)
            y: Row (0-5)
            
        Returns:
            RGB tuple (r, g, b)
        """
        index = self._xy_to_index(x, y)
        return self.np[index]
    
    def clear(self):
        """Clear all pixels (set to black)"""
        for i in range(TOTAL_PIXELS):
            self.np[i] = (0, 0, 0)
        self.np.write()
    
    def set_gate(self, gate_num, state):
        """
        Set gate state (red=0, green=1)
        
        Args:
            gate_num: Gate number (1-6)
            state: Gate state (0=off/red, 1=on/green)
        """
        index = self._gate_index(gate_num)
        color = RED if state == 0 else GREEN
        self.np[index] = color
        self.np.write()
    
    def get_gate(self, gate_num):
        """
        Get gate state
        
        Args:
            gate_num: Gate number (1-6)
            
        Returns:
            Gate state (0=off, 1=on)
        """
        index = self._gate_index(gate_num)
        color = self.np[index]
        return 0 if color == RED else 1
