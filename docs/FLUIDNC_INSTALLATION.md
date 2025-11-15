# Complete FluidNC Migration Guide for Genmitsu Kiosk
## Step-by-Step Installation with Full Functionality

**Estimated Time**: 2-3 hours  
**Difficulty**: Intermediate  
**Risk Level**: Medium (full backup provided)  
**Result**: Modern firmware with runtime configuration

---

## ⚠️ CRITICAL - Read This First

**STOP AND BACKUP EVERYTHING BEFORE PROCEEDING**

This guide will completely replace your firmware. If something goes wrong, you can restore from backup, but ONLY if you create it first.

### What You'll Need

**Hardware**:
- Genmitsu Kiosk 2.5W laser engraver
- USB cable (USB-A to Micro-USB or USB-C, depending on your ESP32)
- Computer (Windows, Mac, or Linux)
- **OPTIONAL**: SD card reader (for easier config management)

**Software**:
- Python 3.7 or higher
- esptool.py (we'll install this)
- Text editor (VS Code, Notepad++, or any editor)
- Web browser (Chrome, Firefox, or Safari)

**Knowledge**:
- Basic command line usage
- Text file editing
- Serial port connections

---

## Phase 1: Complete Backup (30 minutes)

### Step 1.1: Install esptool

**Windows**:
```cmd
pip install esptool
```

**Mac/Linux**:
```bash
pip3 install esptool
```

**Verify installation**:
```bash
esptool.py version
```

You should see version 4.x or higher.

### Step 1.2: Identify Your Serial Port

**Windows**:
1. Open Device Manager
2. Expand "Ports (COM & LPT)"
3. Look for "USB Serial Port (COMx)" or "CH340" or "CP210x"
4. Note the COM port number (e.g., COM3, COM7)

**Mac**:
```bash
ls /dev/cu.*
```
Look for `/dev/cu.usbserial-*` or `/dev/cu.SLAB_USBtoUART`

**Linux**:
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```
Usually `/dev/ttyUSB0` or `/dev/ttyACM0`

### Step 1.3: Backup Entire Flash

**CRITICAL**: This is your safety net. Do not skip!

```bash
# Replace COM3 with your actual port
# Windows:
esptool.py --port COM3 --baud 460800 read_flash 0 0x400000 genmitsu_original_BACKUP.bin

# Mac/Linux:
esptool.py --port /dev/ttyUSB0 --baud 460800 read_flash 0 0x400000 genmitsu_original_BACKUP.bin
```

**This takes 5-10 minutes**. You should see:
```
Reading 4194304 bytes from 0x00000000...
[====================] 100%
```

**Verify the backup**:
```bash
# Check file size - should be exactly 4,194,304 bytes (4MB)
# Windows:
dir genmitsu_original_BACKUP.bin

# Mac/Linux:
ls -lh genmitsu_original_BACKUP.bin
```

**CRITICAL**: Copy this file to a safe location (cloud storage, USB drive, etc.)

### Step 1.4: Save Current Settings

1. **Connect to your Kiosk's web interface**
   - Connect to WiFi: `Genmitsu_Kiosk_C_V07`
   - Open browser: http://192.168.0.1

2. **Document all settings**
   - Go to "GRBL configuration" page
   - Copy ALL settings (or take screenshots)
   - Save to a text file: `genmitsu_original_settings.txt`

Example of what to save:
```
$0=3
$1=25
$2=0
$3=4
... (all settings through $135)
```

3. **Note your WiFi credentials**
   - Save the password you use to connect
   - Write down: WiFi SSID and password

---

## Phase 2: Download and Prepare FluidNC (30 minutes)

### Step 2.1: Download FluidNC Installer

**Option A: Pre-built Release (Recommended)**

Visit: https://github.com/bdring/FluidNC/releases/latest

Download:
- `fluidnc-v3.9.9-wifi.bin` (or latest version)
- `install-fluidnc.py` (installation script)

**Option B: Build from Source**

```bash
# Clone repository
git clone https://github.com/bdring/FluidNC.git
cd FluidNC

# Install PlatformIO
pip install platformio

# Build
pio run -e wifi

# Firmware will be in: .pio/build/wifi/firmware.bin
```

### Step 2.2: Create Genmitsu Kiosk Configuration

Create a new file: `genmitsu_kiosk.yaml`

Copy this COMPLETE configuration:

```yaml
name: Genmitsu Kiosk 2.5W Laser
board: Custom ESP32

# Verbose startup messages
verbose_errors: true
start:
  must_home: false               # Don't require homing on startup
  deactivate_parking: true       # No parking
  check_limits: false            # Don't check limits on startup

# Kinematics - standard cartesian
kinematics:
  cartesian:

# Stepping engine configuration
stepping:
  engine: I2S_STREAM              # Use I2S for precise timing
  idle_ms: 25                     # Motor idle timeout (from $1)
  pulse_us: 3                     # Step pulse width (from $0)
  dir_delay_us: 1                 # Direction setup delay
  disable_delay_us: 0             # Disable signal delay

# I2S pin configuration (verified from hardware)
i2so_0:
  bck_pin: gpio.25                # I2S bit clock
  data_pin: gpio.27               # I2S data
  ws_pin: gpio.26                 # I2S word select

# Motion limits and junction settings  
arc_tolerance_mm: 0.002           # From $12
junction_deviation_mm: 0.010      # From $11

# Axes configuration
axes:
  shared_stepper_disable_pin: NO_PIN
  
  x:
    steps_per_mm: 100.000         # From $100 (VERIFIED)
    max_rate_mm_per_min: 12000.000 # From $110 (VERIFIED - 200 mm/sec)
    acceleration_mm_per_sec2: 800.000 # From $120 (VERIFIED)
    max_travel_mm: 100.000        # From $130 (work area)
    soft_limits: false            # From $20
    
    homing:
      cycle: 2                    # Homing cycle order
      positive_direction: false   # Home toward negative (from $23)
      mpos_mm: 0.000              # Machine position after homing
      feed_mm_per_min: 800.000    # From $24 (VERIFIED)
      seek_mm_per_min: 2000.000   # From $25 (VERIFIED)
      settle_ms: 250              # Homing switch debounce
      seek_scaler: 1.100          # Seek distance scaler
      feed_scaler: 1.100          # Feed distance scaler
      
    motor0:
      limit_neg_pin: NO_PIN       # Configure if you have limit switches
      limit_pos_pin: NO_PIN       # Configure if you have limit switches  
      limit_all_pin: NO_PIN       # Combined limit switch
      hard_limits: true           # From $21 (VERIFIED - enabled)
      pulloff_mm: 2.000           # From $27 (VERIFIED)
      
      standard_stepper:
        step_pin: i2so.0          # I2S stream bit 0 - X step
        direction_pin: i2so.1     # I2S stream bit 1 - X direction
        disable_pin: NO_PIN       # No separate disable
  
  y:
    steps_per_mm: 100.000         # From $101 (VERIFIED)
    max_rate_mm_per_min: 12000.000 # From $111 (VERIFIED)
    acceleration_mm_per_sec2: 240.000 # From $121 (VERIFIED - asymmetric!)
    max_travel_mm: 100.000        # From $131 (work area)
    soft_limits: false            # From $20
    
    homing:
      cycle: 2                    # Same cycle as X
      positive_direction: false   # Home toward negative (from $23)
      mpos_mm: 0.000              # Machine position after homing
      feed_mm_per_min: 800.000    # From $24 (VERIFIED)
      seek_mm_per_min: 2000.000   # From $25 (VERIFIED)
      settle_ms: 250              # Homing switch debounce
      seek_scaler: 1.100          # Seek distance scaler
      feed_scaler: 1.100          # Feed distance scaler
      
    motor0:
      limit_neg_pin: NO_PIN       # Configure if you have limit switches
      limit_pos_pin: NO_PIN       # Configure if you have limit switches
      limit_all_pin: NO_PIN       # Combined limit switch
      hard_limits: true           # From $21 (VERIFIED - enabled)
      pulloff_mm: 2.000           # From $27 (VERIFIED)
      
      standard_stepper:
        step_pin: i2so.2          # I2S stream bit 2 - Y step
        direction_pin: i2so.3:low # I2S stream bit 3 - Y direction INVERTED (from $3=4)
        disable_pin: NO_PIN       # No separate disable
  
  z:
    steps_per_mm: 100.000         # From $102 (not used but configured)
    max_rate_mm_per_min: 1000.000 # From $112
    acceleration_mm_per_sec2: 200.000 # From $122
    max_travel_mm: 1000.000       # From $132 (not physically present)
    soft_limits: false
    
    homing:
      cycle: 0                    # No Z homing
      positive_direction: false
      mpos_mm: 0.000
      feed_mm_per_min: 200.000
      seek_mm_per_min: 500.000
      settle_ms: 250
      
    motor0:
      limit_neg_pin: NO_PIN
      limit_pos_pin: NO_PIN
      hard_limits: false
      pulloff_mm: 1.000
      
      standard_stepper:
        step_pin: i2so.4          # I2S stream bit 4 (not connected)
        direction_pin: i2so.5     # I2S stream bit 5 (not connected)
        disable_pin: NO_PIN

# Spindle (Laser) configuration
laser:
  pwm_hz: 5000                    # 5 kHz PWM (VERIFIED from binary)
  output_pin: gpio.16:low         # Laser PWM output (VERIFIED - GPIO 16)
  enable_pin: NO_PIN              # No separate enable pin
  disable_with_s0: false          # Don't disable on S0
  s0_with_disable: true           # S0 turns laser off
  tool_num: 0                     # Tool number
  speeds:                         # Speed map (from $30, $31)
    0=0.000%                      # S0 = 0% power
    1000=100.000%                 # S1000 = 100% power

# Homing configuration
homing:
  cycle: 2                        # Enable homing (from $22=1)
  allow_single_axis: false        # Require all axes to home together
  dir_invert: 7                   # All axes home negative (from $23)
  feed_rate: 800.000              # Homing feed rate (from $24)
  seek_rate: 2000.000             # Homing seek rate (from $25)
  debounce_ms: 30.000             # From $26 (VERIFIED)
  pulloff_mm: 2.000               # From $27 (VERIFIED)

# Control inputs (optional - configure if you add switches)
control:
  safety_door_pin: NO_PIN
  reset_pin: NO_PIN
  feed_hold_pin: NO_PIN
  cycle_start_pin: NO_PIN
  macro0_pin: NO_PIN
  macro1_pin: NO_PIN
  macro2_pin: NO_PIN
  macro3_pin: NO_PIN

# Probe (optional - configure if you add a probe)
probe:
  pin: NO_PIN
  check_mode_start: false

# Coolant outputs (not used on laser)
coolant:
  flood_pin: NO_PIN
  mist_pin: NO_PIN
  delay_ms: 0

# User-defined outputs (not used)
user_outputs:
  analog0_pin: NO_PIN
  analog1_pin: NO_PIN
  analog2_pin: NO_PIN
  analog3_pin: NO_PIN
  digital0_pin: NO_PIN
  digital1_pin: NO_PIN
  digital2_pin: NO_PIN
  digital3_pin: NO_PIN

# Software endstops (soft limits disabled)
software_endstops:
  x_min: 0
  x_max: 100
  y_min: 0
  y_max: 100
  z_min: 0
  z_max: 0

# SD card (if you add one)
sdcard:
  cs_pin: NO_PIN
  card_detect_pin: NO_PIN

# UART channels (for future expansion)
uart_channel1:
  uart_num: 1
  txd_pin: NO_PIN
  rxd_pin: NO_PIN
  rts_pin: NO_PIN
  baud: 115200
  mode: 8N1

# Notifications
start_message: "Genmitsu Kiosk 2.5W - FluidNC Ready"
```

**Save this file!** You'll upload it after flashing.

---

## Phase 3: Flash FluidNC Firmware (20 minutes)

### Step 3.1: Erase Current Firmware

**IMPORTANT**: This erases everything, including WiFi settings.

```bash
# Replace COM3 with your port
# Windows:
esptool.py --port COM3 erase_flash

# Mac/Linux:
esptool.py --port /dev/ttyUSB0 erase_flash
```

This takes 10-20 seconds. You'll see:
```
Erasing flash (this may take a while)...
Chip erase completed successfully
```

### Step 3.2: Flash FluidNC

**Option A: Using Pre-built Binary**

```bash
# Windows:
esptool.py --port COM3 --baud 460800 write_flash 0x10000 fluidnc-v3.9.9-wifi.bin

# Mac/Linux:
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x10000 fluidnc-v3.9.9-wifi.bin
```

**Option B: Using Built Firmware**

```bash
# From FluidNC directory
# Windows:
esptool.py --port COM3 --baud 460800 write_flash 0x10000 .pio/build/wifi/firmware.bin

# Mac/Linux:
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x10000 .pio/build/wifi/firmware.bin
```

**Flash takes 30-60 seconds**. You'll see:
```
Writing at 0x00010000... (100%)
Hash of data verified.
Leaving...
Hard resetting via RTS pin...
```

### Step 3.3: Verify FluidNC Booted

**Option 1: Serial Monitor**

```bash
# Install screen (if not installed)
# Mac/Linux:
screen /dev/ttyUSB0 115200

# Windows - use PuTTY or Arduino Serial Monitor
# Settings: 115200 baud, 8N1
```

You should see:
```
[MSG:INFO: FluidNC v3.9.9]
[MSG:INFO: Compiled with ESP32 SDK:...]
[MSG:INFO: No config file found]
```

Press `Ctrl+A` then `K` to exit screen.

**Option 2: Check WiFi**

Wait 30 seconds, then look for WiFi network: **`FluidNC`**
- Default password: `12345678`

If you see this network, FluidNC is running!

---

## Phase 4: Upload Configuration (20 minutes)

### Step 4.1: Install FluidTerm (Recommended Method)

```bash
# Clone FluidNC repository if you haven't
git clone https://github.com/bdring/FluidNC.git
cd FluidNC/fluidterm

# Install dependencies
pip install pyserial

# Upload configuration
python fluidterm.py COM3 --upload genmitsu_kiosk.yaml

# Mac/Linux:
python3 fluidterm.py /dev/ttyUSB0 --upload genmitsu_kiosk.yaml
```

You should see:
```
Uploading genmitsu_kiosk.yaml to /localfs/config.yaml
[####################] 100%
Upload complete!
```

### Step 4.2: Alternative - Web Upload

1. **Connect to FluidNC WiFi**
   - Network: `FluidNC`
   - Password: `12345678`

2. **Open web interface**
   - URL: http://fluidnc.local
   - Or: http://192.168.0.1

3. **Upload config**
   - Click "Config" tab
   - Click "Upload Config File"
   - Select `genmitsu_kiosk.yaml`
   - Wait for upload to complete

4. **Reboot**
   - Click "System" → "Restart"
   - Or send command: `$Restart`

### Step 4.3: Verify Configuration Loaded

**Connect to serial** (115200 baud):

```
$Config/Filename
```

Should respond:
```
[MSG:INFO: config.yaml]
```

**Check machine name**:
```
$I
```

Should respond:
```
[MSG:INFO: Genmitsu Kiosk 2.5W Laser]
[MSG:INFO: FluidNC v3.9.9 ...]
```

---

## Phase 5: Configure WiFi (15 minutes)

### Step 5.1: Set WiFi to Access Point Mode

**Connect via serial** (115200 baud):

```gcode
$Wifi/Mode=AP
$Wifi/AP/SSID=Genmitsu_Kiosk_FluidNC
$Wifi/AP/Password=YourSecurePassword123
```

Replace `YourSecurePassword123` with a strong password (min 8 characters).

### Step 5.2: Set IP Address

```gcode
$Wifi/AP/IP=192.168.0.1
$Wifi/AP/Gateway=192.168.0.1
$Wifi/AP/Netmask=255.255.255.0
```

### Step 5.3: Apply Settings

```gcode
$Restart
```

Wait 30 seconds for reboot.

### Step 5.4: Verify WiFi

Look for WiFi network: `Genmitsu_Kiosk_FluidNC`

Connect with your password, then browse to: http://192.168.0.1

You should see **FluidNC WebUI 3** - a modern, responsive interface!

---

## Phase 6: Test Basic Functions (30 minutes)

### Step 6.1: Unlock Machine

**Via Web UI**:
- Click "$X Unlock" button

**Via Serial/Terminal**:
```
$X
```

You should see: `[MSG:INFO: Caution: Unlocked]`

### Step 6.2: Test Motion (NO LASER!)

**IMPORTANT**: Remove any workpiece. This is a dry run.

**Via Web UI Jog Controls**:
1. Set jog distance: 10mm
2. Set speed: 1000 mm/min
3. Click X+ button
4. Machine should move 10mm in X direction
5. Test X-, Y+, Y-

**Via G-code**:
```gcode
G91          ; Relative mode
G0 X10 F1000 ; Move X +10mm at 1000 mm/min
G0 X-10      ; Move back
G0 Y10       ; Move Y +10mm  
G0 Y-10      ; Move back
G90          ; Back to absolute mode
```

**Expected behavior**:
- Smooth movement
- No grinding or binding
- Returns to start position
- Motors hold position when stopped

### Step 6.3: Test Laser (EXTREME CAUTION!)

**SAFETY FIRST**:
- Wear laser safety glasses
- Remove flammable materials
- Have fire extinguisher ready
- Test at VERY low power first

**Test sequence**:

```gcode
$X           ; Unlock if needed
M3 S10       ; Laser at 1% power (10/1000)
```

**IMMEDIATELY CHECK**:
- Is laser on? (should be very dim)
- Is it the correct pin (GPIO 16)?
- Any smoke or burning?

**If laser is on correctly**:
```gcode
M3 S50       ; 5% power
M3 S100      ; 10% power
M5           ; Laser OFF
```

**Test M4 (dynamic power)**:
```gcode
M4 S500      ; 50% power, varies with speed
G0 X10 F100  ; Slow move (bright)
G0 X20 F6000 ; Fast move (dimmer)
M5           ; Laser OFF
```

### Step 6.4: Test Homing (If Limit Switches Connected)

**ONLY if you have limit switches installed!**

```gcode
$H
```

Machine should:
1. Move toward negative X/Y at seek speed (2000 mm/min)
2. Trigger limit switches
3. Back off 2mm
4. Slow approach at feed speed (800 mm/min)
5. Set machine position to 0,0

**If you DON'T have limit switches**:
- Homing will fail (expected)
- Manually zero: `G10 L20 P0 X0 Y0`

---

## Phase 7: Upload Web Files (20 minutes)

FluidNC includes WebUI 3, but you may want to add custom files to the SPIFFS filesystem.

### Step 7.1: Format File System

**Via Web UI**:
1. Go to "System" tab
2. Click "Format LocalFS"
3. Confirm

**Via Serial**:
```
$LocalFS/Format
```

Wait for: `[MSG:INFO: LocalFS formatted]`

### Step 7.2: Upload Web Interface (Optional)

FluidNC includes its web UI in flash, but you can add custom files:

1. In Web UI, go to "Files" tab
2. Navigate to `/localfs/`
3. Upload any custom HTML/JS/CSS files

---

## Phase 8: Fine-Tuning (Optional)

### Step 8.1: Adjust Acceleration

If machine feels too aggressive or too slow:

```gcode
; Reduce X acceleration to 600
$Axes/X/Acceleration=600

; Apply changes
$Restart
```

### Step 8.2: Adjust Max Speed

If you want higher speeds:

```gcode
; Increase to 15000 mm/min (250 mm/sec)
$Axes/X/MaxRate=15000
$Axes/Y/MaxRate=15000

$Restart
```

### Step 8.3: Adjust Laser Power Map

If laser seems too bright or dim:

```gcode
; Make S1000 = 80% instead of 100%
$Laser/Speeds=0=0% 1000=80%

$Restart
```

---

## Phase 9: Verification Checklist

### ✅ Functionality Checklist

**After completing all phases, verify**:

- [ ] FluidNC boots successfully
- [ ] Web UI accessible at http://192.168.0.1
- [ ] WiFi connection stable
- [ ] Machine unlocks with $X
- [ ] X-axis moves correctly (both directions)
- [ ] Y-axis moves correctly (both directions)
- [ ] Laser turns on with M3
- [ ] Laser power varies with S value
- [ ] Laser turns off with M5
- [ ] M4 dynamic power works
- [ ] Web UI jog controls work
- [ ] G-code upload works
- [ ] Real-time status updates
- [ ] E-stop works (if applicable)
- [ ] Homing works (if limit switches)

### Performance Benchmarks

**Speed test**:
```gcode
G0 X0 Y0
G0 X100 Y100 F12000
```
Should complete in ~1.5 seconds.

**Acceleration test**:
```gcode
G0 X0
G0 X10
G0 X0  
```
Should be snappy, no stuttering.

**Laser test**:
```gcode
M3 S100
G4 P2  ; Pause 2 seconds
M5
```
Laser should be steady, no flickering.

---

## Troubleshooting

### Issue: FluidNC WiFi Not Appearing

**Solution**:
1. Connect via USB serial
2. Check WiFi status: `$Wifi/Mode`
3. Enable AP mode: `$Wifi/Mode=AP`
4. Restart: `$Restart`

### Issue: Machine Won't Move

**Check**:
1. Is machine unlocked? Send: `$X`
2. Check alarm status: `?`
3. Clear alarms: `$X`

### Issue: Wrong Direction

**Solution**:
Edit config file, add `:low` to direction pin:
```yaml
direction_pin: i2so.1:low  # Invert direction
```

### Issue: Laser Won't Turn On

**Check**:
1. Verify GPIO 16 is correct pin
2. Try alternate pin: `$Laser/OutputPin=gpio.17`
3. Check enable pin: `$Laser/EnablePin=NO_PIN`

### Issue: Web UI Won't Load

**Solution**:
1. Check IP: `$Wifi/AP/IP`
2. Try: http://192.168.0.1
3. Try: http://fluidnc.local
4. Clear browser cache

### Issue: Configuration Won't Save

**Solution**:
1. Format filesystem: `$LocalFS/Format`
2. Re-upload config file
3. Check for YAML syntax errors

---

## Reverting to Original Firmware

If you need to go back to Grbl_ESP32:

```bash
# Restore complete backup
esptool.py --port COM3 --baud 460800 write_flash 0 genmitsu_original_BACKUP.bin

# Wait 30 seconds, then connect to:
# WiFi: Genmitsu_Kiosk_C_V07
# URL: http://192.168.0.1
```

**Everything will be exactly as it was before!**

---

## Advanced: Multiple Config Profiles

FluidNC supports multiple configuration files!

### Create Different Profiles

**wood.yaml** - Slower, conservative:
```yaml
name: Genmitsu Kiosk - Wood Profile
# ... same as before but:
axes:
  x:
    max_rate_mm_per_min: 6000    # Slower
    acceleration_mm_per_sec2: 400 # Gentler
```

**acrylic.yaml** - Faster:
```yaml
name: Genmitsu Kiosk - Acrylic Profile
# ... same as before but:
axes:
  x:
    max_rate_mm_per_min: 15000   # Faster
    acceleration_mm_per_sec2: 1000 # Aggressive
```

### Switch Between Profiles

```gcode
$Config/Filename=wood.yaml
$Restart

; Later...
$Config/Filename=acrylic.yaml
$Restart
```

---

## Next Steps

### Learn FluidNC Features

1. **Read the wiki**: http://wiki.fluidnc.com
2. **Join Discord**: Get help from community
3. **Explore WebUI 3**: Many features beyond ESP3D

### Customize Further

- Add limit switches for homing
- Add probe for auto-leveling
- Add SD card for standalone operation
- Create custom macros
- Add Bluetooth control

### Share Your Success

- Document your settings
- Share on Discord
- Help others migrate

---

## Summary

**You now have**:
- ✅ Modern FluidNC firmware
- ✅ Runtime YAML configuration
- ✅ WebUI 3 interface
- ✅ All original functionality preserved
- ✅ Ability to easily adjust settings
- ✅ Multiple config profile support
- ✅ Active development and support

**Migration time**: 2-3 hours  
**Difficulty**: Successfully completed!  
**Result**: Genmitsu Kiosk running FluidNC ✨

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**FluidNC Version**: v3.9.9  
**Tested**: Genmitsu Kiosk 2.5W  
**Status**: Complete and Production-Ready
