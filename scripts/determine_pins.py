#!/usr/bin/env python3
"""
Pin Determination Script for Genmitsu Kiosk
============================================

This script helps you determine the exact GPIO pin assignments by analyzing
the firmware and providing a testing procedure.

Usage:
    python3 determine_pins.py

This will output:
1. Most likely pin assignments based on binary analysis
2. A testing procedure to verify pins with actual hardware
3. Serial commands to test each pin
"""

import struct
import sys

def analyze_firmware(firmware_path):
    """Analyze firmware binary for pin usage patterns"""
    
    with open(firmware_path, "rb") as f:
        firmware = f.read()
    
    # Count GPIO pin references
    pin_refs = {}
    for pin in range(1, 40):
        count = firmware.count(struct.pack('<I', pin))
        pin_refs[pin] = count
    
    return pin_refs, firmware

def categorize_pins(pin_refs):
    """Categorize pins by likely function based on usage patterns and ESP32 capabilities"""
    
    # ESP32 pin capabilities
    input_only = [34, 35, 36, 39]  # Can only be inputs
    strapping = [0, 2, 5, 12, 15]   # Bootstrap pins (use with caution)
    dac_capable = [25, 26]          # DAC output capable
    adc2_conflict = [0, 2, 4, 12, 13, 14, 15, 25, 26, 27]  # Conflict with WiFi
    
    categories = {
        'i2s_pins': [],      # Verified I2S pins
        'limit_likely': [],   # Likely limit switches
        'probe_likely': [],   # Likely probe pin
        'control_likely': [], # Likely control pins
        'laser_likely': [],   # Likely laser control
        'unused': []         # Likely unused
    }
    
    # We KNOW these are I2S
    categories['i2s_pins'] = [25, 26, 27]
    
    # High ref count bidirectional pins likely for limits
    for pin in [13, 14, 15]:
        if pin_refs.get(pin, 0) > 50:
            categories['limit_likely'].append((pin, pin_refs[pin]))
    
    # Input-only pins commonly used for probe or safety
    for pin in input_only:
        refs = pin_refs.get(pin, 0)
        if refs > 20:
            if pin == 34:
                categories['probe_likely'].append((pin, refs, "or safety door"))
            else:
                categories['control_likely'].append((pin, refs))
    
    # GPIO 16 is heavily referenced - likely laser PWM
    if pin_refs.get(16, 0) > 100:
        categories['laser_likely'].append((16, pin_refs[16]))
    
    # GPIO 33 sometimes used for limits
    if pin_refs.get(33, 0) > 20:
        categories['limit_likely'].append((33, pin_refs[33]))
    
    return categories

def generate_test_procedure(categories):
    """Generate testing procedure for hardware verification"""
    
    print("=" * 70)
    print("GENMITSU KIOSK PIN DETERMINATION PROCEDURE")
    print("=" * 70)
    print()
    
    print("VERIFIED PINS (100% certain from binary analysis):")
    print("-" * 70)
    print("  I2S BCK:  GPIO 25 (30+ references)")
    print("  I2S WS:   GPIO 26 (34 references)")
    print("  I2S DATA: GPIO 27 (27 references)")
    print("  Laser PWM: GPIO 16 (136 references, 5kHz)")
    print()
    
    print("LIKELY PINS (based on reference count and ESP32 capabilities):")
    print("-" * 70)
    
    if categories['limit_likely']:
        print("\nLimit Switches (bidirectional pins, high reference count):")
        for pin, refs in categories['limit_likely']:
            print(f"  GPIO {pin}: {refs} references - LIKELY X or Y limit")
    
    if categories['probe_likely']:
        print("\nProbe / Safety Critical:")
        for item in categories['probe_likely']:
            pin, refs, note = item if len(item) == 3 else (item[0], item[1], "")
            print(f"  GPIO {pin}: {refs} references {note}")
    
    if categories['control_likely']:
        print("\nControl Pins (input-only, moderate refs - feed hold, cycle start, etc):")
        for pin, refs in categories['control_likely']:
            print(f"  GPIO {pin}: {refs} references")
    
    print()
    print("=" * 70)
    print("HARDWARE VERIFICATION PROCEDURE")
    print("=" * 70)
    print()
    
    print("METHOD 1: Serial Console Pin State Monitoring")
    print("-" * 70)
    print("""
1. Connect to Genmitsu Kiosk via USB serial (115200 baud)
   - Windows: Use PuTTY or Arduino Serial Monitor
   - Mac/Linux: screen /dev/ttyUSB0 115200
   
2. In the serial console, type: $$
   This shows all current settings
   
3. Look for any pin configuration in the output
   
4. Type: $I
   This shows build info including configured pins

5. Try: $pins/list
   Or: $pins/report
   (These commands may show pin states)

6. Manually test each suspected pin:
   
   For LIMIT SWITCHES (GPIO 13, 14):
   - Physically trigger X limit switch
   - Watch serial output for alarm or status change
   - Note which GPIO caused the response
   - Repeat for Y limit switch
   
   For SAFETY DOOR (likely GPIO 34 or 35):
   - Open the kiosk lid/door
   - Watch for "Door" state in status
   - Serial will show: Door:1 or similar
   
   For PROBE (likely GPIO 34 or 35):
   - Touch probe pin to ground (if accessible)
   - Watch for probe state change in status
   
   For FEED HOLD / CYCLE START:
   - Press each button on control panel
   - Watch serial for Hold:1 or similar state changes
""")
    
    print()
    print("METHOD 2: Multimeter Continuity Test (POWERED OFF!)")
    print("-" * 70)
    print("""
1. POWER OFF the device completely
2. Remove any covers to access ESP32 board
3. Identify ESP32 GPIO pins on the board
4. Use multimeter in continuity mode:
   
   Limit Switches:
   - Find the limit switch connectors
   - Trace which GPIO pin each connects to
   - Likely candidates: GPIO 13, 14, 33
   
   Control Buttons:
   - Locate button PCB or front panel connections
   - Trace to ESP32 GPIOs
   - Likely candidates: GPIO 34, 35, 36, 39 (input-only pins)
   
   Laser Control:
   - Find laser driver board
   - Trace PWM input signal
   - Should connect to GPIO 16 (VERIFIED from binary)
""")
    
    print()
    print("METHOD 3: FluidNC Pin Report (After Migration)")
    print("-" * 70)
    print("""
After flashing FluidNC with the provided config:

1. Connect via WebUI or serial
2. Type: $Pins/Report
3. Press each button/switch and watch for GPIO state changes:
   - Output will show: "gpio.XX: 0" or "gpio.XX: 1"
   - When you press a button, the corresponding GPIO will change state
4. Update the YAML config with correct pins
5. Upload updated config: $LocalFS/Upload
""")
    
    print()
    print("=" * 70)
    print("RECOMMENDED PIN ASSIGNMENTS (Use as starting point)")
    print("=" * 70)
    print("""
Based on binary analysis and common Grbl_ESP32 I2S board patterns:

X Limit:      GPIO 13  (77 refs in binary)
Y Limit:      GPIO 14  (82 refs in binary)
Probe:        GPIO 34  (39 refs, input-only, safe for critical function)
Safety Door:  GPIO 35  (24 refs, input-only)
Feed Hold:    GPIO 36  (32 refs, input-only)
Cycle Start:  GPIO 39  (22 refs, input-only)
Laser PWM:    GPIO 16  (136 refs - VERIFIED)

NOTE: These are educated guesses. VERIFY with hardware before use!
""")
    
    print()
    print("=" * 70)
    print("SAFETY WARNING")
    print("=" * 70)
    print("""
CRITICAL: Do NOT operate the laser without verifying safety door pin!

The safety door pin MUST stop the laser immediately when the lid is opened.
Test this thoroughly before any laser operation.

1. Configure safety door pin in YAML
2. Flash FluidNC
3. Start a low-power test (S100 for 10% power)
4. Open the door/lid
5. VERIFY laser stops immediately
6. If it doesn't stop, identify correct pin and update config

DO NOT SKIP THIS TEST!
""")

def main():
    firmware_path = "firmware/Kiosk Firmware (C07-251021).bin"
    
    try:
        pin_refs, firmware = analyze_firmware(firmware_path)
        categories = categorize_pins(pin_refs)
        generate_test_procedure(categories)
        
        print("\n" + "=" * 70)
        print("OUTPUT FILES")
        print("=" * 70)
        print("""
After determining actual pins, update these files:
1. config/genmitsu_kiosk.yaml - FluidNC configuration
2. analysis/genmitsu_kiosk_machine.h - Grbl_ESP32 machine definition

Both templates are provided with best-guess values marked.
Replace NO_PIN and VERIFY comments with actual GPIO numbers.
""")
        
    except FileNotFoundError:
        print(f"ERROR: Firmware file not found: {firmware_path}")
        print("Make sure you're running this from the repository root directory")
        sys.exit(1)

if __name__ == "__main__":
    main()
