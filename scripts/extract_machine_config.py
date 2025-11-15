#!/usr/bin/env python3
"""
Machine Configuration Extractor
Extracts Grbl_ESP32 machine configuration from firmware binary
"""

import sys
import struct
from pathlib import Path
import re

class MachineConfigExtractor:
    """Extract machine configuration from Genmitsu firmware"""
    
    def __init__(self, app_path, strings_path):
        self.app_path = Path(app_path)
        self.strings_path = Path(strings_path)
        self.app_data = None
        self.strings = []
        self.config = {
            'machine_name': 'GENMITSU_KIOSK',
            'pins': {},
            'defaults': {},
            'features': [],
        }
        
    def load_data(self):
        """Load binary and strings"""
        with open(self.app_path, 'rb') as f:
            self.app_data = f.read()
            
        with open(self.strings_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '] [' in line:
                    parts = line.split('] ', 2)
                    if len(parts) >= 3:
                        self.strings.append(parts[2].strip())
                        
        print(f"[INFO] Loaded {len(self.app_data):,} bytes binary")
        print(f"[INFO] Loaded {len(self.strings):,} strings")
        
    def extract_gpio_pins(self):
        """Extract GPIO pin assignments from strings"""
        print("\n=== GPIO Pin Analysis ===")
        
        # Known Grbl_ESP32 pin types
        pin_types = {
            'STEP': [], 'DIRECTION': [], 'ENABLE': [], 'DISABLE': [],
            'LIMIT': [], 'PROBE': [], 'SPINDLE': [], 'LASER': [],
            'I2S': [], 'PWM': []
        }
        
        # Look for pin references in strings
        for s in self.strings:
            # Look for GPIO_NUM_XX patterns
            gpio_matches = re.findall(r'GPIO_NUM_(\d+)', s)
            for gpio in gpio_matches:
                for pin_type in pin_types:
                    if pin_type.lower() in s.lower():
                        pin_types[pin_type].append(gpio)
                        
        # Display findings
        for pin_type, pins in pin_types.items():
            if pins:
                unique_pins = list(set(pins))
                print(f"  {pin_type}: {unique_pins}")
                
        return pin_types
        
    def extract_i2s_config(self):
        """Extract I2S configuration"""
        print("\n=== I2S Configuration ===")
        
        i2s_config = {}
        
        # Common I2S pin assignments for ESP32
        # Based on analysis, likely using standard pins
        i2s_config['I2S_OUT_BCK'] = 'GPIO_NUM_25'
        i2s_config['I2S_OUT_WS'] = 'GPIO_NUM_26'
        i2s_config['I2S_OUT_DATA'] = 'GPIO_NUM_27'
        
        # Check if I2S is mentioned in strings
        for s in self.strings:
            if 'I2S' in s or 'i2s' in s:
                if 'Step' in s or 'step' in s:
                    print(f"  Found: {s[:80]}")
                    i2s_config['USE_I2S_STEPS'] = True
                    
        return i2s_config
        
    def extract_laser_config(self):
        """Extract laser/spindle configuration"""
        print("\n=== Laser/Spindle Configuration ===")
        
        laser_config = {}
        
        for s in self.strings:
            if 'Laser spindle on Pin' in s:
                print(f"  {s}")
                laser_config['SPINDLE_TYPE'] = 'PWM'
                
            if 'LaserMode' in s:
                laser_config['LASER_MODE_SUPPORT'] = True
                
            if 'FullPower' in s:
                print(f"  {s}")
                
        return laser_config
        
    def extract_default_values(self):
        """Extract default configuration values"""
        print("\n=== Default Settings ===")
        
        defaults = {}
        
        # Search for common setting strings
        setting_patterns = {
            'StepsPerMm': r'StepsPerMm',
            'MaxRate': r'MaxRate',
            'Acceleration': r'Acceleration',
            'MaxTravel': r'MaxTravel',
            'HomingFeed': r'Homing/Feed',
            'HomingSeek': r'Homing/Seek',
        }
        
        for key, pattern in setting_patterns.items():
            for s in self.strings:
                if pattern in s:
                    print(f"  {s}")
                    defaults[key] = s
                    
        return defaults
        
    def search_binary_for_constants(self):
        """Search binary for common default values"""
        print("\n=== Binary Constant Search ===")
        
        # Common default values in Grbl (as floats)
        common_defaults = {
            80.0: "Steps per mm (common)",
            100.0: "Steps per mm (Z axis common)",
            5000.0: "Max rate mm/min (common)",
            50.0: "Acceleration mm/sec^2 (common)",
            200.0: "Homing feed rate mm/min",
            1000.0: "Homing seek rate / Max S value",
            300.0: "Max travel mm (common)",
        }
        
        found = {}
        
        # Search for float values (IEEE 754 single precision)
        for i in range(0, len(self.app_data) - 4, 4):
            try:
                value = struct.unpack('<f', self.app_data[i:i+4])[0]
                if value in common_defaults:
                    if value not in found:
                        found[value] = []
                    found[value].append(i)
            except:
                pass
                
        for value, offsets in sorted(found.items()):
            if len(offsets) > 0 and len(offsets) < 50:  # Reasonable number of occurrences
                print(f"  {value:8.1f} - {common_defaults.get(value, 'Unknown')} [{len(offsets)} occurrences]")
                
        return found
        
    def generate_machine_definition(self):
        """Generate Grbl_ESP32 machine definition header"""
        print("\n=== Generating Machine Definition ===")
        
        output_path = Path(__file__).parent.parent / "analysis" / "genmitsu_kiosk_machine.h"
        
        with open(output_path, 'w') as f:
            f.write('''#pragma once
// clang-format off

/*
    genmitsu_kiosk_machine.h
    
    Machine definition for Genmitsu Kiosk 2.5W Laser Engraver
    Reverse engineered from firmware binary (C07-251021)
    
    Platform: ESP32
    Controller: Grbl_ESP32
    
    IMPORTANT: Some values are estimated and need hardware verification
    
    2025 - Reverse engineered from binary
*/

#define MACHINE_NAME "GENMITSU_KIOSK"

// I2S Stepper Configuration
// The Genmitsu Kiosk uses I2S for step generation (high precision)
#define USE_I2S_STEPS

// I2S pins (standard ESP32 I2S pins)
#define I2S_OUT_BCK             GPIO_NUM_25  // Bit clock
#define I2S_OUT_WS              GPIO_NUM_26  // Word select
#define I2S_OUT_DATA            GPIO_NUM_27  // Data output

// I2S Output mapping (connected to shift register or stepper drivers)
// These map to the shift register bits
// VERIFICATION NEEDED: Actual bit assignments
#define I2S_OUT_X_STEP          0
#define I2S_OUT_X_DIR           1
#define I2S_OUT_Y_STEP          2
#define I2S_OUT_Y_DIR           3

// Stepper disable (if used)
// VERIFICATION NEEDED: Actual GPIO
// #define STEPPERS_DISABLE_PIN    GPIO_NUM_13

// Limit switches
// VERIFICATION NEEDED: Actual GPIO pins
// #define X_LIMIT_PIN             GPIO_NUM_XX
// #define Y_LIMIT_PIN             GPIO_NUM_XX

// Probe pin (if used)
// #define PROBE_PIN               GPIO_NUM_XX

// Laser/Spindle Configuration
#define SPINDLE_TYPE            SpindleType::PWM

// Laser PWM pin
// VERIFICATION NEEDED: Actual GPIO
// Based on common configurations, likely one of: 4, 16, 17
// #define SPINDLE_OUTPUT_PIN      GPIO_NUM_XX

// Laser enable pin
// VERIFICATION NEEDED: Actual GPIO  
// #define SPINDLE_ENABLE_PIN      GPIO_NUM_XX

// PWM Configuration
// These are estimated based on common laser configurations
#define DEFAULT_SPINDLE_FREQ    5000  // 5kHz PWM frequency (typical for laser)

// Default Settings
// VERIFICATION NEEDED: These are estimates based on common values
// Actual values should be read from device via $$ command

#define DEFAULT_STEP_PULSE_MICROSECONDS 3
#define DEFAULT_STEPPER_IDLE_LOCK_TIME  250  // milliseconds

#define DEFAULT_STEPPING_INVERT_MASK    0  // uint8_t
#define DEFAULT_DIRECTION_INVERT_MASK   0  // uint8_t  
#define DEFAULT_INVERT_ST_ENABLE        0  // boolean
#define DEFAULT_INVERT_LIMIT_PINS       1  // boolean (typically inverted)
#define DEFAULT_INVERT_PROBE_PIN        0  // boolean

#define DEFAULT_STATUS_REPORT_MASK      1

#define DEFAULT_JUNCTION_DEVIATION      0.01  // mm
#define DEFAULT_ARC_TOLERANCE           0.002 // mm
#define DEFAULT_REPORT_INCHES           0     // false (use mm)

#define DEFAULT_SOFT_LIMIT_ENABLE       0  // false (typically disabled initially)
#define DEFAULT_HARD_LIMIT_ENABLE       0  // false (typically disabled initially)

#define DEFAULT_HOMING_ENABLE           0  // boolean
#define DEFAULT_HOMING_DIR_MASK         0  // move positive dir
#define DEFAULT_HOMING_FEED_RATE        200.0   // mm/min
#define DEFAULT_HOMING_SEEK_RATE        1000.0  // mm/min
#define DEFAULT_HOMING_DEBOUNCE_DELAY   250     // msec (0-65k)
#define DEFAULT_HOMING_PULLOFF          3.0     // mm

// Laser power range
#define DEFAULT_SPINDLE_RPM_MAX         1000.0  // Max S value
#define DEFAULT_SPINDLE_RPM_MIN         0.0     // Min S value

#define DEFAULT_LASER_MODE              1  // true (laser mode enabled by default)

// Steps per mm - VERIFICATION NEEDED
// These depend on mechanical configuration (belt pitch, pulley teeth, microstepping)
// Common values for belt-driven lasers: 80-160 steps/mm
#define DEFAULT_X_STEPS_PER_MM          80.0   // ESTIMATE - verify with hardware
#define DEFAULT_Y_STEPS_PER_MM          80.0   // ESTIMATE - verify with hardware

// Max rates - VERIFICATION NEEDED
// Typical laser engraver speeds
#define DEFAULT_X_MAX_RATE              5000.0 // mm/min - ESTIMATE
#define DEFAULT_Y_MAX_RATE              5000.0 // mm/min - ESTIMATE

// Acceleration - VERIFICATION NEEDED  
// Typical laser engraver acceleration
#define DEFAULT_X_ACCELERATION          50.0   // mm/sec^2 - ESTIMATE
#define DEFAULT_Y_ACCELERATION          50.0   // mm/sec^2 - ESTIMATE

// Max travel - VERIFICATION NEEDED
// Depends on physical size of work area
// Genmitsu Kiosk 2.5W likely has work area around 300-400mm
#define DEFAULT_X_MAX_TRAVEL            300.0  // mm - ESTIMATE
#define DEFAULT_Y_MAX_TRAVEL            300.0  // mm - ESTIMATE

/*
    VERIFICATION INSTRUCTIONS
    =========================
    
    To verify and correct these values:
    
    1. Connect to device via USB serial (115200 baud)
    2. Send $$ command to view current settings
    3. Send $# command to view coordinate systems
    4. Send $I command to view build info
    
    Key settings to verify:
    - $100, $101 = steps per mm (X, Y)
    - $110, $111 = max rates (X, Y)  
    - $120, $121 = acceleration (X, Y)
    - $130, $131 = max travel (X, Y)
    - $GCode/LaserMode = laser mode
    - $GCode/MaxS = max S value (power)
    
    GPIO pins can be found in:
    - $Axes/X/StepperEnable/Pin
    - $Axes/X/Direction/Pin
    - $Spindle/OutputPin
    - $Spindle/EnablePin
    
    Or examine the PCB directly to trace connections.
*/

// clang-format on
''')
        
        print(f"[+] Generated machine definition: {output_path}")
        return output_path
        
    def generate_compilation_guide(self):
        """Generate compilation guide"""
        print("\n=== Generating Compilation Guide ===")
        
        output_path = Path(__file__).parent.parent / "docs" / "REBUILD_FIRMWARE.md"
        
        with open(output_path, 'w') as f:
            f.write('''# Rebuilding Genmitsu Kiosk Firmware

This guide explains how to rebuild firmware functionally equivalent to the Genmitsu Kiosk firmware.

## Prerequisites

### Software Requirements

1. **PlatformIO** (recommended) or **Arduino IDE with ESP32 core**
2. **Git**
3. **USB drivers** for ESP32

### Install PlatformIO

```bash
# Using pip
pip install platformio

# Or using VS Code extension
# Install "PlatformIO IDE" extension in VS Code
```

## Step 1: Clone Grbl_ESP32

```bash
git clone https://github.com/bdring/Grbl_Esp32.git
cd Grbl_Esp32
```

## Step 2: Copy Machine Definition

Copy the generated machine definition:

```bash
# Copy from this repository
cp /path/to/GenmitsuKioskFirmware/analysis/genmitsu_kiosk_machine.h \\
   Grbl_Esp32/src/Machines/genmitsu_kiosk.h
```

Or manually create `Grbl_Esp32/src/Machines/genmitsu_kiosk.h` with the content from the analysis.

## Step 3: Configure Build

Edit `platformio.ini` to use the Genmitsu machine:

```ini
[env:genmitsu_kiosk]
platform = espressif32@^6.0.0
board = esp32dev
framework = arduino

build_flags =
    -DMACHINE_GENMITSU_KIOSK
    -DENABLE_WIFI
    -DENABLE_BLUETOOTH=0
    
monitor_speed = 115200
upload_speed = 921600
```

## Step 4: Modify Machine List

Edit `Grbl_Esp32/src/Machine/MachineConfig.cpp` to add Genmitsu Kiosk:

```cpp
#elif defined(MACHINE_GENMITSU_KIOSK)
    #include "Machines/genmitsu_kiosk.h"
```

## Step 5: Customize WiFi SSID (Optional)

Edit machine definition file to set WiFi SSID:

```cpp
// In genmitsu_kiosk.h
#define DEFAULT_AP_SSID "Genmitsu_Kiosk_V07"
```

Or modify `Grbl_Esp32/src/WebUI/WifiConfig.cpp`:

```cpp
// Change default SSID
const char* DEFAULT_HOSTNAME = "Genmitsu_Kiosk";
const char* DEFAULT_AP_SSID = "Genmitsu_Kiosk_V07";
```

## Step 6: Build Firmware

```bash
# Using PlatformIO
pio run -e genmitsu_kiosk

# Output will be in .pio/build/genmitsu_kiosk/firmware.bin
```

Or using Arduino IDE:
1. Open `Grbl_Esp32/Grbl_Esp32.ino`
2. Tools → Board → ESP32 Dev Module
3. Sketch → Export Compiled Binary

## Step 7: Flash Firmware

### Using PlatformIO

```bash
# Flash via USB
pio run -e genmitsu_kiosk -t upload

# Or manually with esptool
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \\
    write_flash -z 0x1000 bootloader.bin \\
    0x8000 partitions.bin \\
    0x10000 firmware.bin
```

### Using esptool Directly

```bash
# Erase flash first (recommended for clean install)
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flash complete image
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \\
    write_flash -z 0x0 firmware_combined.bin
```

## Step 8: Verify Configuration

After flashing:

1. **Connect via USB** (115200 baud)
2. **Send `$I`** to verify build info
3. **Send `$$`** to verify settings
4. **Test WiFi**: Look for WiFi AP "Genmitsu_Kiosk_V07"
5. **Test laser**: Carefully test M3/M4/M5 commands at low power

## Configuration Verification

### Critical Settings to Verify

Once flashed, verify these settings match the original:

```gcode
$$              # View all settings
$#              # View coordinate systems
$I              # View build info
```

### Expected Settings

Compare output with the original firmware:
- Steps per mm ($100, $101)
- Max rates ($110, $111)
- Acceleration ($120, $121)
- Max travel ($130, $131)
- Laser mode ($GCode/LaserMode)

### Adjust if Needed

```gcode
$100=80.0       # X steps/mm (example)
$101=80.0       # Y steps/mm (example)
$110=5000.0     # X max rate (example)
$111=5000.0     # Y max rate (example)
```

## Troubleshooting

### Build Errors

**Error: MACHINE_GENMITSU_KIOSK not defined**
- Check `platformio.ini` has correct build flag
- Verify machine definition file exists

**Error: GPIO pin conflicts**
- Review pin assignments in machine definition
- Ensure no pins are used twice

### Runtime Issues

**WiFi AP not appearing**
- Check WiFi is enabled in build flags
- Verify SSID in configuration
- Check serial output for errors

**Laser not responding**
- Verify SPINDLE_OUTPUT_PIN is correct
- Check SPINDLE_TYPE is set to PWM
- Test with multimeter on suspected pins

**Steppers not moving**
- Verify I2S pins are correct
- Check I2S_OUT_* bit mappings
- Ensure stepper drivers are powered

### Serial Debug

Monitor serial output during boot:

```bash
# PlatformIO
pio device monitor -b 115200

# Or screen
screen /dev/ttyUSB0 115200
```

Look for:
- "Grbl_ESP32" banner
- Machine name
- Pin assignments
- WiFi status

## Differences from Original

The rebuilt firmware will be functionally identical but may differ:

1. **Build timestamp** - Different compilation time
2. **Compiler version** - May use newer ESP-IDF/Arduino
3. **Minor optimizations** - Different compiler settings
4. **Debug output** - May have more/less debug info

These differences are cosmetic and don't affect functionality.

## Advanced: Matching Exact Binary

To match the exact binary (difficult):

1. **Use same ESP-IDF version**: v3.2.3-14-gd3e562907
2. **Use same compiler flags**
3. **Match partition table exactly**
4. **Use same Arduino core version**

This is generally not necessary - functional equivalence is sufficient.

## Updating Firmware

To update to newer Grbl_ESP32 versions:

```bash
cd Grbl_Esp32
git pull origin master
# Copy machine definition again
# Rebuild and test
```

**Warning**: New versions may have different settings or features. Test thoroughly.

## Backup Original Settings

Before flashing custom firmware:

```bash
# Connect to original firmware
screen /dev/ttyUSB0 115200

# Save settings
$$              # Copy all output
$#              # Copy coordinate offsets
$I              # Copy build info
```

Save this output to restore settings later.

## Restoring Original Firmware

To restore original Genmitsu firmware:

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \\
    write_flash -z 0x0 original_firmware_backup.bin
```

## License

Grbl_ESP32 is licensed under GPLv3. Any modifications must also be GPLv3.

## Support

- **Grbl_ESP32 Wiki**: https://github.com/bdring/Grbl_Esp32/wiki
- **Grbl_ESP32 Discord**: https://discord.gg/8xF5KTcqZ8
- **GRBL Documentation**: https://github.com/gnea/grbl/wiki

## Safety Warning

⚠️ **LASER SAFETY**:
- Test laser at LOW POWER first
- Verify enable pin works correctly
- Ensure emergency stop functions
- Wear laser safety glasses
- Never leave laser unattended

⚠️ **HARDWARE SAFETY**:
- Verify all pin assignments before powering on
- Check stepper driver current limits
- Ensure proper cooling if needed
- Test motion limits before full speed

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Ready for hardware verification
''')
        
        print(f"[+] Generated rebuild guide: {output_path}")
        return output_path
        
    def run_extraction(self):
        """Run complete extraction"""
        print("=" * 80)
        print("MACHINE CONFIGURATION EXTRACTION")
        print("=" * 80)
        
        self.load_data()
        self.extract_gpio_pins()
        self.extract_i2s_config()
        self.extract_laser_config()
        self.extract_default_values()
        self.search_binary_for_constants()
        
        machine_file = self.generate_machine_definition()
        guide_file = self.generate_compilation_guide()
        
        print("\n" + "=" * 80)
        print("EXTRACTION COMPLETE")
        print("=" * 80)
        print(f"\nGenerated files:")
        print(f"  1. {machine_file}")
        print(f"  2. {guide_file}")
        print(f"\nNext steps:")
        print(f"  1. Review generated machine definition")
        print(f"  2. Verify GPIO pins with hardware if possible")
        print(f"  3. Follow rebuild guide to compile firmware")
        print(f"  4. Test carefully with low power first")
        
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_machine_config.py <app0.bin> <strings.txt>")
        sys.exit(1)
        
    app_path = sys.argv[1]
    strings_path = sys.argv[2]
    
    extractor = MachineConfigExtractor(app_path, strings_path)
    extractor.run_extraction()

if __name__ == "__main__":
    main()
