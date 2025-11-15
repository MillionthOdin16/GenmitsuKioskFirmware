# Rebuilding Genmitsu Kiosk Firmware

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
cp /path/to/GenmitsuKioskFirmware/analysis/genmitsu_kiosk_machine.h \
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
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
    write_flash -z 0x1000 bootloader.bin \
    0x8000 partitions.bin \
    0x10000 firmware.bin
```

### Using esptool Directly

```bash
# Erase flash first (recommended for clean install)
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flash complete image
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
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
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
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
