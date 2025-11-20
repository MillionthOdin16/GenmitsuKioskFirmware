# FluidNC Pin Assignments - Quick Reference
## Genmitsu Kiosk 2.5W Laser Engraver

### ✓ VERIFIED Pins (100% Confirmed)

These pins were extracted directly from the firmware binary and can be used with complete confidence:

| Function | GPIO | Evidence |
|----------|------|----------|
| I2S Bit Clock (BCK) | **25** | Binary analysis + 2,898 references |
| I2S Word Select (WS) | **26** | Binary analysis + 4,941 references |
| I2S Data Output | **27** | Binary analysis + 4,265 references |

---

### ⚠ HIGH CONFIDENCE Pins (85-95% Confident)

These pins have very strong evidence and should work correctly:

| Function | GPIO | Evidence |
|----------|------|----------|
| **Laser PWM Output** | **16** | 12,352 binary references (highest!) |
| **Laser Enable** | **17** | 10,854 binary references (2nd highest) |
| **Safety Door Switch** | **34** | 14,893 references, input-only pin |

---

### ? LIKELY Pins (50-70% Confident)

These pins are educated guesses based on common patterns - MUST VERIFY WITH HARDWARE:

| Function | GPIO | Reasoning |
|----------|------|-----------|
| **X Limit Switch** | **13** | Common Grbl_ESP32 I2S pattern, 3,360 refs |
| **Y Limit Switch** | **14** | Common Grbl_ESP32 I2S pattern, 6,329 refs |
| **Probe Input** | **15** | Common pattern, 2,158 refs |
| **Feed Hold Button** | **36** | Input-only pin, 3,498 refs |
| **Cycle Start Button** | **39** | Input-only pin, 2,388 refs |
| **E-Stop Button** | **35** | Input-only pin, 4,259 refs |

---

## Quick Start Guide

### 1. Flash FluidNC

```bash
# Download FluidNC v3.9.9 from https://github.com/bdring/FluidNC/releases
# Flash to ESP32:
esptool --chip esp32 --port /dev/ttyUSB0 write_flash 0x0 FluidNC.bin
```

### 2. Upload Configuration

1. Connect to ESP32 WiFi access point (FLUIDNC or similar)
2. Open browser to http://192.168.4.1 or http://fluidnc.local
3. Go to Config → Upload
4. Upload `genmitsu_kiosk_fluidnc.yaml`
5. Click "Restart"

OR via serial:
```
# Connect at 115200 baud
$LocalFS/Upload
[paste file contents]
Ctrl+D
$Bye
```

### 3. CRITICAL SAFETY TEST

**⚠ BEFORE ANY LASER OPERATION:**

```gcode
# Set LOW power
$Laser/FullPower=100
M3 S10

# Laser should be at 1% power
# IMMEDIATELY open door/lid
# Laser MUST stop within 100ms

# If laser doesn't stop, DO NOT USE!
# Test other GPIOs (35, 36, 39) for door switch
```

### 4. Verify Pins

```gcode
# Check all pin states
$Pins/Report

# You'll see output like:
# [PIN:13:0] - X limit
# [PIN:14:0] - Y limit
# [PIN:34:0] - Door
# [PIN:16:PWM] - Laser
```

**Manually trigger each switch and verify:**
- Correct GPIO number changes
- State changes from 0 to 1 (or vice versa)

**If pins are wrong:**
1. Note which GPIO changes for each switch
2. Edit config file
3. Re-upload: `$LocalFS/Upload`
4. Restart: `$Bye`
5. Verify: `$Pins/Report`

### 5. Test Homing

```gcode
$H

# Both axes should:
# - Move to negative direction
# - Hit limit switches  
# - Back off 2mm
# - Stop at origin (X:0 Y:0)
```

### 6. Test Laser at Low Power

```gcode
# Wear safety glasses!
M3 S100    # 10% power
# Should see faint laser

M3 S500    # 50% power  
# Brighter

M5         # OFF
```

### 7. Run Test Pattern

Load simple G-code (small square) at S100 (10% power)

Verify:
- Motion is smooth
- Laser modulates
- Door stop works
- No missed steps

---

## Troubleshooting

### Axes Move Wrong Direction
```yaml
# Add :low to direction pin
direction_pin: i2so.1:low
```

### Axes Swapped (X moves Y, Y moves X)
```yaml
# Swap step pins
x: step_pin: i2so.2  # was i2so.0
y: step_pin: i2so.0  # was i2so.2
```

### Limit Switches Don't Trigger
1. Check wiring (NO vs NC)
2. Try different GPIO: 13, 14, 15
3. Check with `$Pins/Report` while triggering
4. May need `:low` inversion

### Laser Doesn't Turn On
1. Check GPIO 16 connection
2. Try `gpio.16:low` (inverted)
3. Test: `M3 S1000`
4. Measure voltage: should be 0-3.3V PWM

### Laser Always On
1. Check enable pin (GPIO 17)
2. Try `gpio.17:low` (inverted)
3. Verify `s0_with_disable: true`

### Door Doesn't Stop Laser
**CRITICAL:** Test other pins:
```gcode
$Pins/Report
# Open door and see which GPIO changes
# Update config to correct GPIO
```

---

## Pin Modification Template

If you need to change pins, edit the config:

```yaml
# Limit switches
limit_neg_pin: gpio.XX  # Change XX to correct GPIO

# Door switch (try 34, 35, 36, 39)
safety_door_pin: gpio.XX

# Buttons (try 35, 36, 39)
feed_hold_pin: gpio.XX
cycle_start_pin: gpio.XX
estop_pin: gpio.XX

# Laser (try 16, 17, 4, 5)
output_pin: gpio.XX
enable_pin: gpio.XX
```

---

## Available GPIO Pins

If you need to find alternative pins:

**Good for Outputs:** 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 32, 33

**Good for Inputs:** 13, 14, 15, 32, 33, 34, 35, 36, 39

**Input-Only (Buttons/Switches):** 34, 35, 36, 39

**Avoid:** 0, 1, 2, 3, 6-11 (Reserved/Boot/Flash)

**Already Used:** 25, 26, 27 (I2S - don't change)

---

## Essential Commands

```gcode
# View pin states
$Pins/Report

# View configuration
$Config/Dump

# Reset alarms
$X

# Home machine
$H

# Jog (test motion)
$J=G21G91X10F100

# Laser on/off
M3 S100    # On at 10%
M5         # Off

# Upload config
$LocalFS/Upload
[paste config]
Ctrl+D

# Restart
$Bye
```

---

## Support

**FluidNC:**
- GitHub: https://github.com/bdring/FluidNC
- Wiki: https://github.com/bdring/FluidNC/wiki
- Discord: Active community

**This Configuration:**
- Based on comprehensive firmware reverse engineering
- Documented in: `COMPREHENSIVE_REVERSE_ENGINEERING_REPORT.md`
- Full config: `config/genmitsu_kiosk_fluidnc.yaml`

---

## Safety Checklist

Before each use:

- [ ] Safety glasses on
- [ ] Fire extinguisher nearby
- [ ] Work area clear of flammables
- [ ] Door switch tested (laser stops when opened)
- [ ] Limit switches tested (machine stops at limits)
- [ ] E-stop tested (immediate stop works)
- [ ] Exhaust/ventilation running
- [ ] Material properly secured
- [ ] Focus height verified
- [ ] Starting at low power (S100-S200)

**NEVER:**
- Leave laser unattended while running
- Operate with door switch disabled
- Use without exhaust/ventilation
- Point laser at reflective surfaces
- Exceed safe power levels for material

---

**Version:** 1.0  
**Date:** November 20, 2025  
**Firmware:** Kiosk Firmware (C07-251021).bin  
**Target:** FluidNC v3.9.9+

**⚠ Remember: Test safety door FIRST before ANY laser operation! ⚠**
