# Dual-Core Sequencer Architecture

## Overview

The ESP32-C6 Sequencer project has been enhanced to support dual-core architecture, leveraging both the high-performance (HP) core and low-power (LP) core for optimal performance and power efficiency.

## Core Responsibilities

### Low-Power Core (LP Core)
- **Clock Generation**: Precise timing with hardware timers
- **Potentiometer Reading**: ADC sampling with decimation and averaging
- **External Clock Input**: Detection and frequency measurement
- **Real-time Operations**: Critical timing functions

### High-Performance Core (HP Core)
- **User Interface**: Rotary encoders, buttons, neopixel display
- **Pattern Management**: Trigger patterns, sequencer logic
- **Visual Feedback**: Neopixel display updates
- **System Control**: Overall sequencer management

## Inter-Core Communication

### Communication Methods
1. **Shared Memory**: Thread-safe data exchange
2. **Message Queues**: Inter-core message passing
3. **Inter-Processor Interrupts**: Real-time signaling
4. **Event Synchronization**: Coordinated operations

### Message Types
- `CMD_CLOCK_UPDATE`: BPM and clock source updates
- `CMD_TRIGGER_PATTERN`: Trigger pattern data
- `CMD_EXTERNAL_CLOCK`: External clock detection
- `CMD_POTENTIOMETER_READ`: Potentiometer value requests
- `RESP_CLOCK_TICK`: Clock tick notifications
- `RESP_POTENTIOMETER_VALUE`: Potentiometer readings
- `RESP_EXTERNAL_CLOCK_DETECTED`: External clock events

## Key Features

### External Clock Support
- Automatic detection of external clock signals
- Frequency measurement and BPM calculation
- Seamless switching between internal and external clocks
- Timeout handling for external clock loss

### Potentiometer Optimization
- Decimation for reduced sampling rate
- Running average for noise reduction
- Configurable averaging windows
- Efficient ADC usage

### Trigger Generation
- Pattern-based trigger scheduling
- Real-time trigger execution
- Neopixel visual feedback
- Statistics and monitoring

## File Structure

```
micropython_lib/drivers/
├── intercore_communication.py    # Inter-core communication system
├── clock_generator_lp.py         # Low-power core clock generator
├── potentiometer_lp.py           # Low-power core potentiometer
├── trigger_generator_hp.py       # High-performance core trigger generator
└── neopixel_display.py           # Neopixel display (unchanged)

micropython_lib/utils/
└── test_dual_core_sequencer.py   # Comprehensive dual-core test
```

## Usage Example

```python
# Initialize inter-core communication
intercore_comm = InterCoreCommunication()

# Low-power core components
clock_gen = LowPowerClockGenerator(intercore_comm, led_pin=15)
pot_gen = LowPowerPotentiometer(intercore_comm, pin=2)

# High-performance core components
neopixel_display = NeopixelDisplay(pin=0)
trigger_gen = HighPerformanceTriggerGenerator(intercore_comm, neopixel_display)

# Start all components
clock_gen.start()
pot_gen.start()
trigger_gen.start()

# Set trigger pattern
pattern = [
    [True, False, False, False, False, False, False],   # Step 1
    [False, True, False, False, False, False, False],   # Step 2
    # ... more steps
]
trigger_gen.set_trigger_pattern(pattern)
trigger_gen.enable_pattern(True)
```

## Benefits

### Power Efficiency
- Low-power core handles timing-critical tasks
- High-performance core can sleep when not needed
- Optimized ADC sampling with decimation

### Real-Time Performance
- Dedicated core for audio timing
- No interference from UI tasks
- Consistent trigger timing

### Scalability
- Easy to add features to high-performance core
- Low-power core remains focused on timing
- Better code organization

## Testing

Run the comprehensive test suite:

```python
import test_dual_core_sequencer
test_dual_core_sequencer.run_comprehensive_test()
```

The test suite includes:
- Inter-core communication testing
- Clock generator functionality
- Potentiometer reading and decimation
- Trigger pattern generation
- External clock input testing
- Integrated dual-core operation

## Future Enhancements

1. **ESP-IDF Integration**: Direct dual-core programming
2. **Custom C Extensions**: Optimized inter-core communication
3. **FreeRTOS Primitives**: Advanced synchronization
4. **Hardware DMA**: Direct memory access for data transfer
5. **Power Management**: Advanced sleep modes and wake-up
