# Getting Actual Configuration from Your Genmitsu Kiosk

## Why This is Necessary

The firmware binary does NOT contain the default configuration values as extractable constants. The machine-specific settings are either:
1. Compiled into the code (requires full decompilation)
2. Calculated at runtime
3. Stored in NVS (non-volatile storage) - user configurable

**You MUST extract these values from your actual device.**

## Prerequisites

- USB cable
- Serial terminal software (Arduino IDE Serial Monitor, PuTTY, screen, or minicom)
- Your Genmitsu Kiosk powered on and connected

## Step 1: Connect to Device

### On Linux/Mac:
```bash
# Find the device
ls /dev/tty* | grep -i usb

# Connect with screen
screen /dev/ttyUSB0 115200

# Or with minicom
minicom -D /dev/ttyUSB0 -b 115200
```

### On Windows:
1. Open Device Manager
2. Find "Ports (COM & LPT)"
3. Note the COM port (e.g., COM3)
4. Use PuTTY or Arduino IDE Serial Monitor
5. Set baud rate to **115200**

### Using Arduino IDE Serial Monitor:
1. Tools → Board → ESP32 Dev Module
2. Tools → Port → Select your port
3. Tools → Serial Monitor
4. Set baud rate to **115200** in bottom right

## Step 2: Get All Settings

In the serial terminal, type:

```
$$
```

Press Enter. You will see output like:

```
$0=10
$1=25
$2=0
...
$100=80.000
$101=80.000
$102=100.000
$110=5000.000
$111=5000.000
$112=500.000
$120=200.000
$121=200.000
$122=50.000
$130=100.000
$131=100.000
$132=10.000
...
```

**SAVE ALL OF THIS OUTPUT TO A FILE**

## Step 3: Get Coordinate System Info

Type:

```
$#
```

This shows work coordinate offsets and tool length offsets.

## Step 4: Get Build Info

Type:

```
$I
```

This shows the firmware version and build information.

## Step 5: Extract Critical Values

From the `$$` output, extract these CRITICAL values:

### Steps per MM ($100-$102)
```
$100 = ???  (X axis steps per mm)
$101 = ???  (Y axis steps per mm)
$102 = ???  (Z axis steps per mm, if present)
```

### Max Rates ($110-$112)
```
$110 = ???  (X axis max rate mm/min)
$111 = ???  (Y axis max rate mm/min)
$112 = ???  (Z axis max rate mm/min, if present)
```

### Accelerations ($120-$122)
```
$120 = ???  (X axis acceleration mm/sec^2)
$121 = ???  (Y axis acceleration mm/sec^2)
$122 = ???  (Z axis acceleration mm/sec^2, if present)
```

### Max Travel ($130-$132)
```
$130 = ???  (X axis max travel mm)
$131 = ???  (Y axis max travel mm)
$132 = ???  (Z axis max travel mm, if present)
```

### Other Important Settings
```
$3  = ???  (Direction invert mask)
$4  = ???  (Step enable invert)
$5  = ???  (Limit pins invert)
$10 = ???  (Status report mask)
$11 = ???  (Junction deviation mm)
$12 = ???  (Arc tolerance mm)
$13 = ???  (Report inches)
$20 = ???  (Soft limits enable)
$21 = ???  (Hard limits enable)
$22 = ???  (Homing cycle enable)
$23 = ???  (Homing direction invert mask)
$24 = ???  (Homing feed rate mm/min)
$25 = ???  (Homing seek rate mm/min)
$26 = ???  (Homing debounce ms)
$27 = ???  (Homing pull-off mm)
$30 = ???  (Max spindle speed - min S value)
$31 = ???  (Min spindle speed - max S value)
$32 = ???  (Laser mode 0=off, 1=on)
```

## Step 6: Get Extended Settings (if available)

Some Grbl_ESP32 builds use extended settings with names:

Type:

```
$GCode/LaserMode
$GCode/MaxS
$GCode/MinS
$Spindle/PWM/Frequency
$Laser/FullPower
```

Each on a separate line to see their values.

## Step 7: Update Machine Definition

Open `genmitsu_kiosk_machine.h` and replace all the ??? values with the actual values from your device.

For example, if your device shows:
```
$100=80.000
```

Then change:
```cpp
// #define DEFAULT_X_STEPS_PER_MM          ???
```

To:
```cpp
#define DEFAULT_X_STEPS_PER_MM          80.0
```

## Step 8: Verify GPIO Pins (Advanced)

### Method 1: From Extended Settings (if available)

Try these commands:
```
$Axes/X/StepperEnable/Pin
$Axes/Y/StepperEnable/Pin
$Spindle/OutputPin
$Spindle/EnablePin
```

### Method 2: Physical Tracing

1. **DISCONNECT POWER AND USB**
2. Open the enclosure (be careful, laser hazard!)
3. Use a multimeter in continuity mode
4. Trace connections from ESP32 pins to:
   - Stepper drivers (Step, Dir, Enable pins)
   - Laser driver (PWM, Enable)
   - Limit switches
5. **Document findings before reassembling**

### Method 3: Test with Multimeter (CAREFUL!)

1. Connect device, connect multimeter to suspected pins
2. Issue movement commands at LOW speed
3. Watch for voltage changes on pins during motion
4. **DO NOT TEST LASER PINS WITHOUT PROPER SAFETY**

## Step 9: Test Configuration

After updating the machine definition:

1. Build the firmware
2. Flash to a SPARE ESP32 first (not your working device!)
3. Test basic functions:
   - Connect via serial
   - Issue $$ - verify settings match
   - Test motion at LOW speeds
   - Test limits (if configured)
   - Test laser at MINIMUM power
4. Only after thorough testing, flash to actual device

## Common Settings Examples

### Typical Belt-Driven Laser (reference only):
```
Steps/mm:    80-160 (depends on pulley teeth, belt pitch, microstepping)
Max Rate:    3000-8000 mm/min
Acceleration: 50-200 mm/sec^2
Max Travel:   100mm (for Genmitsu Kiosk - VERIFIED)
```

### Typical PWM Settings for Laser:
```
Frequency:    5000 Hz (found in binary)
Resolution:   10-bit (256-1024 levels)
Max S Value:  1000 or 255 (depends on configuration)
```

## Safety Warnings

⚠️ **CRITICAL SAFETY WARNINGS:**

1. **NEVER test laser without proper eye protection**
2. **ALWAYS start with minimum power settings**
3. **VERIFY emergency stop works**
4. **CHECK motion direction before full speed**
5. **USE SPARE ESP32 for testing first**
6. **BACKUP original firmware before flashing**
7. **INCORRECT STEPS/MM CAN CRASH MECHANICS**

## Troubleshooting

### No Response from Device
- Check correct port selected
- Try different baud rates (9600, 57600, 115200)
- Press reset button on ESP32
- Check USB cable (must be data cable, not charge-only)

### Garbled Output
- Wrong baud rate (should be 115200)
- Electromagnetic interference
- Bad USB cable

### Settings Not Showing
- Device might not be running Grbl
- Firmware might be corrupted
- Try sending Ctrl+X (software reset) first

## Need Help?

If you cannot get settings from device:

1. Contact Genmitsu support for official documentation
2. Ask on Grbl_ESP32 Discord: https://discord.gg/8xF5KTcqZ8
3. Post on CNC/Laser forums with your device model
4. Check if Genmitsu has published machine definition

## File Backup

Before making any changes, save your current settings:

```bash
# In serial terminal, capture all output from:
$$
$#
$I

# Save to: genmitsu_kiosk_original_settings.txt
```

This allows you to restore if something goes wrong.

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Required reading before compilation
