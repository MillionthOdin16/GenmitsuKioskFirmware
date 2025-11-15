# GPIO Pin Mapping and Hardware Configuration

This document details the GPIO pin assignments and hardware configuration for the Genmitsu Kiosk 2.5W laser engraver.

## GPIO Configuration Overview

The Genmitsu Kiosk uses ESP32 GPIO pins for various control functions including:
- Stepper motor control (via I2S)
- Laser PWM output
- Limit switches
- Control panel inputs
- Status indicators

## Pin Assignment Categories

### Stepper Motor Control (I2S-based)

The firmware uses I2S for precise step generation. This is a common technique in Grbl_ESP32 that provides:
- High precision timing
- Offloads CPU from step generation
- Supports high step rates

**I2S Pins** (Standard ESP32 I2S configuration):
- GPIO 26 - I2S WS (Word Select)
- GPIO 25 - I2S BCK (Bit Clock)  
- GPIO 27 - I2S Data Out

These pins connect to a shift register or stepper driver that demultiplexes the signal to individual step/direction pins.

### Laser Control

Based on string analysis, the laser control uses:

**Laser PWM Output**: Configurable GPIO pin
- Function: Variable power control
- Type: PWM output
- Frequency: Configurable (typically 1-5 kHz for laser diodes)
- Resolution: Configurable bit depth

**Laser Enable**: Separate GPIO pin
- Function: Hardware laser enable/disable
- Type: Digital output
- Can be inverted via settings

**Note**: Exact GPIO numbers are configured in NVS settings. Default configuration would be found in the Grbl_ESP32 machine definition file for this specific model.

### Limit Switches

String analysis shows support for limit switches on configurable pins:
- X-axis limit
- Y-axis limit  
- Z-axis limit (if present)
- Optional: Probe pin for tool length sensing

Format from strings: `%s limit switch on pin %s`

### Control Interface

**User Digital Outputs**: Configurable number of digital control pins
- Format: `User Digital Output:%d on Pin:%s`

**User Analog Outputs**: PWM-based analog outputs
- Format: `User Analog Output:%d on Pin:%s Freq:%0.0fHz`

### UART Communication

**Serial Port** (for G-code input):
- TX pin: Configurable via settings
- RX pin: Configurable via settings  
- RTS/CTS: Optional hardware flow control
- Baud rate: 115200 (default GRBL)

### Special GPIO Constraints

From the firmware validation strings:

**Input-Only Pins** (ESP32 limitation):
- GPIO 34-39: Can only be used as inputs
- No pull-up/pull-down resistors available on these pins
- Commonly used for: ADC inputs, limit switches

**DAC Pins** (ESP32 feature):
- GPIO 25, GPIO 26: 8-bit DAC output available
- Note: String shows `DAC spindle pin invalid GPIO_NUM_%d (pin 25 or 26 only)`
- Can be used for analog spindle control (not applicable for laser)

**Strapping Pins** (Bootstrap configuration):
- GPIO 0: Boot mode selection
- GPIO 2: Download mode
- GPIO 5: SDIO timing
- GPIO 12: Flash voltage
- GPIO 15: Debug output enable

## Typical Grbl_ESP32 Pin Mapping

While exact pins are configured in settings, typical Grbl_ESP32 configurations use:

### Common I2S Stepper Configuration
```
I2S Shift Register Output:
  GPIO 26 → WS
  GPIO 25 → BCK
  GPIO 27 → Data Out
  
Shift Register → Stepper Drivers:
  Bit 0 → X Step
  Bit 1 → X Direction
  Bit 2 → Y Step
  Bit 3 → Y Direction
  Bit 4 → Z Step (or laser modulation)
  Bit 5 → Z Direction
  ...additional outputs...
```

### Typical Pin Assignments (Common Grbl_ESP32 Configs)
```
Laser PWM:        GPIO 4 or GPIO 17 (common choices)
Laser Enable:     GPIO 16 or GPIO 5
X Limit:          GPIO 13
Y Limit:          GPIO 14
Probe:            GPIO 15 or GPIO 35
Status LED:       GPIO 2 (built-in LED)
```

**Note**: These are examples. Actual configuration is in the machine's settings file.

## Pin Discovery Methods

To determine exact pin assignments for a specific device:

### Method 1: NVS Partition Analysis
The NVS partition (currently empty in this firmware dump) would contain configured pin assignments. Format:
```
Key: "pin/x_step"
Value: GPIO number
```

### Method 2: Serial Console
Connect via UART and issue commands:
```
$I    # Print build info and configuration
$$    # Print all settings (includes pin assignments in comments)
$S    # Print detailed settings
```

### Method 3: Machine Definition File
The Grbl_ESP32 source code includes machine definition files. For Genmitsu Kiosk, look for:
```cpp
// In machine definition .h file
#define X_STEP_PIN          GPIO_NUM_XX
#define X_DIRECTION_PIN     GPIO_NUM_XX
#define LASER_OUTPUT_PIN    GPIO_NUM_XX
#define LASER_ENABLE_PIN    GPIO_NUM_XX
// ... etc
```

### Method 4: Hardware Tracing
Physical examination of the PCB can reveal:
- ESP32 pin connections
- Stepper driver connections
- Laser driver connection
- Limit switch inputs

## Configuration via Settings

Pin assignments can be changed via GRBL settings (if not hardcoded):

```gcode
$Axes/X/StepperEnable/Pin = GPIO_NUM_XX
$Axes/X/Direction/Pin = GPIO_NUM_XX
$Laser/OutputPin = GPIO_NUM_XX
$Laser/EnablePin = GPIO_NUM_XX
```

Settings are stored in NVS and persist across reboots.

## Safety Considerations

### Critical Pins
- **Laser Enable**: Must be properly configured for E-stop
- **Limit Switches**: Essential for preventing mechanical damage
- **Emergency Stop**: Should have dedicated hardware input

### Pin Configuration Warnings
From firmware strings:
- `Warning: Spindle output pin not defined` - Laser won't work without proper config
- `Warning: Spindle output pin %s cannot do PWM` - GPIO must support PWM
- `Laser mode requires PWM output` - Laser needs PWM-capable pin

### GPIO Safety
- Never configure output pins to inputs that have external drive
- Verify pin functions before connecting hardware
- Use proper level shifting for 5V devices (ESP32 is 3.3V)
- Protect laser enable with hardware pulldown for fail-safe

## Advanced Configuration

### Multiple Spindle/Laser Types Supported
The firmware supports multiple output types (discovered from strings):
- **PWM Spindle**: Standard PWM control
- **DAC Spindle**: 8-bit DAC output (GPIO 25/26 only)
- **BESC Spindle**: Brushless ESC control (hobby RC motor controllers)
- **Laser**: PWM with laser-specific features
- **VFD Spindle**: RS485-controlled Variable Frequency Drive

Each type has specific pin requirements and configuration options.

### I2S Configuration Details

The I2S stepper system uses:
- **Sample Rate**: Configurable, typically 2x step rate
- **Bits per Sample**: 32-bit
- **Data Format**: Parallel output via shift register

This allows very precise step timing independent of CPU load.

## Debugging Pin Assignments

If pins are not working as expected:

1. **Check Settings**: Verify pin numbers in NVS
2. **Check PWM Capability**: Not all pins support PWM
3. **Check Conflicts**: Ensure pins aren't used by multiple functions
4. **Check Pull-ups**: Some pins have internal pull-ups that may interfere
5. **Check Strapping**: Bootstrap pins may have special requirements

## Reference Documentation

- ESP32 Pin Mapping: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html
- Grbl_ESP32 Wiki: https://github.com/bdring/Grbl_Esp32/wiki
- ESP32 Datasheet: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf

## Conclusion

Exact GPIO pin assignments for this Genmitsu Kiosk are configured in the machine definition or NVS settings. The firmware supports flexible pin configuration through the Grbl_ESP32 settings system. For precise pin mapping, examine the device's NVS partition when it contains configuration data, or refer to Genmitsu's specific machine definition in the Grbl_ESP32 source code.

---

**Document Status**: Based on static firmware analysis  
**Confidence**: High for general architecture, Medium for specific pin numbers  
**Recommendation**: Verify with serial console output or hardware examination for exact pins
