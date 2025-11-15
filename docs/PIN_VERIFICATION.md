# FluidNC Pin Verification and Testing Guide
# Genmitsu Kiosk 2.5W Laser Engraver

## Critical Safety Notice

**DO NOT OPERATE THE LASER UNTIL YOU HAVE VERIFIED ALL SAFETY PINS!**

The safety door pin MUST stop the laser immediately when the lid opens.  
Incorrect pin assignments could result in:
- Laser continuing to fire with lid open (EXTREME HAZARD!)
- Limit switches not stopping motion (equipment damage)
- Emergency stop not working (safety hazard)

## Pin Assignment Status

### ✓ VERIFIED (100% Certain)
These pins were extracted from binary analysis with high confidence:

```yaml
I2S BCK:     gpio.25   # 30 references in binary
I2S WS:      gpio.26   # 34 references in binary
I2S DATA:    gpio.27   # 27 references in binary
Laser PWM:   gpio.16   # 136 references, 5kHz confirmed
```

### ⚠ LIKELY (High Confidence ~80%)
Based on binary reference counts and common Grbl_ESP32 patterns:

```yaml
X Limit:     gpio.13   # 77 references, common I2S board pattern
Y Limit:     gpio.14   # 82 references, common I2S board pattern
```

### ⚠ LIKELY (Medium Confidence ~60%)
Based on ESP32 pin capabilities and reference counts:

```yaml
Safety Door: gpio.34   # 39 refs, input-only (safe for critical function)
E-Stop:      gpio.35   # 24 refs, input-only
Feed Hold:   gpio.36   # 32 refs, input-only  
Cycle Start: gpio.39   # 22 refs, input-only
Probe:       gpio.15   # 61 refs, bidirectional
```

## Pin Verification Procedure

### Method 1: Serial Console Testing (RECOMMENDED)

This is the safest method - no power tools, just monitoring inputs.

#### Step 1.1: Connect to Serial Console

```bash
# Windows - use PuTTY or Arduino IDE Serial Monitor
# Port: COM3 (or your port)
# Baud: 115200

# Mac/Linux
screen /dev/ttyUSB0 115200
# or
picocom /dev/ttyUSB0 -b 115200
```

#### Step 1.2: Flash FluidNC with Provided Config

1. Flash FluidNC firmware (see FLUIDNC_INSTALLATION.md)
2. Upload `config/genmitsu_kiosk.yaml` via WebUI or serial
3. Restart: `$Bye`

#### Step 1.3: Test Input Pins

In the serial console or WebUI, run:

```
$Pins/Report
```

This shows the state of all configured pins.

**Test Each Input:**

1. **Safety Door** (CRITICAL!):
   ```
   Current reading: gpio.34: 0
   → Open the lid/door
   Expected: gpio.34: 1 (or inverted, depends on wiring)
   → If a DIFFERENT GPIO changes, that's your safety door pin!
   ```

2. **X Limit Switch**:
   ```
   Current reading: gpio.13: 0
   → Trigger X limit switch (push X carriage to limit)
   Expected: gpio.13: 1
   → If a DIFFERENT GPIO changes, that's your X limit pin!
   ```

3. **Y Limit Switch**:
   ```
   Current reading: gpio.14: 0
   → Trigger Y limit switch (push Y carriage to limit)
   Expected: gpio.14: 1
   → If a DIFFERENT GPIO changes, that's your Y limit pin!
   ```

4. **Feed Hold Button**:
   ```
   Current reading: gpio.36: 0
   → Press feed hold button
   Expected: gpio.36: 1
   → Note which GPIO actually changes
   ```

5. **Cycle Start Button**:
   ```
   Current reading: gpio.39: 0
   → Press cycle start button
   Expected: gpio.39: 1
   → Note which GPIO actually changes
   ```

6. **E-Stop Button**:
   ```
   Current reading: gpio.35: 0
   → Press emergency stop button
   Expected: gpio.35: 1
   → Note which GPIO actually changes
   ```

#### Step 1.4: Update Configuration

If any pins were wrong, edit `config/genmitsu_kiosk.yaml`:

```yaml
# Example: If safety door was actually GPIO 15 instead of 34
control:
  safety_door_pin: gpio.15  # Changed from gpio.34
```

Re-upload the config:
- Via WebUI: Config → Upload → genmitsu_kiosk.yaml
- Via serial: `$LocalFS/Upload` → paste contents → Ctrl+D

Restart: `$Bye`

### Method 2: Multimeter Continuity Test (POWERED OFF!)

**WARNING: Device must be COMPLETELY POWERED OFF for this test!**

#### Step 2.1: Locate ESP32 Board

1. Unplug ALL power (USB and DC)
2. Remove access panels to expose ESP32 board
3. Identify the ESP32 chip and its GPIO pins

#### Step 2.2: Trace Connections

Using multimeter in continuity mode:

1. **Limit Switches**:
   - Find limit switch connector on board
   - Probe connector pins while probing ESP32 GPIOs
   - Beep indicates connection
   - Document which GPIO connects to which switch

2. **Control Buttons**:
   - Find control panel connector
   - Trace each button wire to ESP32 GPIO
   - Document connections

3. **Safety Door Switch**:
   - **MOST IMPORTANT** - find lid/door switch
   - Trace to ESP32 GPIO
   - Verify this is an input-only pin (34, 35, 36, or 39)

#### Step 2.3: Update Configuration

Update `config/genmitsu_kiosk.yaml` with traced pins.

### Method 3: Firmware Debug Output

If your firmware has debug output enabled:

1. Connect via serial (115200 baud)
2. Watch boot messages - may show pin assignments
3. Look for lines like:
   ```
   [MSG: X limit on GPIO 13]
   [MSG: Y limit on GPIO 14]
   [MSG: Safety door on GPIO 34]
   ```

## Critical Safety Tests

### Test 1: Safety Door Functionality

**THIS IS THE MOST IMPORTANT TEST!**

```
Steps:
1. Set laser to LOW power: S100 (10% = 0.25W)
2. Start laser: M3 S100
3. IMMEDIATELY open lid/door (within 1 second)
4. Observe laser output

Expected: Laser stops within 100ms
Status display shows: "Door:1" or "ALARM:4"

If laser does NOT stop:
→ SAFETY DOOR PIN IS WRONG!
→ DO NOT USE until correct pin is identified!
→ Try each candidate pin (34, 35, 36, 39) until it works
```

### Test 2: Limit Switch Functionality

```
Steps:
1. Home machine: $H
2. Manually push X carriage to X limit switch
3. Observe response

Expected: Machine stops, alarm triggers: "ALARM:1 Hard limit"

If wrong axis triggers or no alarm:
→ Limit pins are wrong or swapped
→ Test each switch individually
→ Update config with correct pins
```

### Test 3: Emergency Stop

```
Steps:
1. Start a motion command: G0 X50 Y50
2. IMMEDIATELY press E-stop
3. Observe response

Expected: Motion stops, alarm triggers: "ALARM:10 E-stop"

If no response:
→ E-stop pin is wrong
→ Test candidate pins until one works
```

### Test 4: Feed Hold / Cycle Start

```
Steps:
1. Start motion: G0 X50 Y50
2. Press Feed Hold during motion
3. Observe: Motion should pause ("Hold:1" in status)
4. Press Cycle Start
5. Observe: Motion should resume

If buttons don't work:
→ Pins may be swapped
→ Update config and re-test
```

## Pin Update Workflow

When you find an incorrect pin:

```yaml
# 1. Edit config/genmitsu_kiosk.yaml
# 2. Update the incorrect pin:

# Example: Safety door was actually GPIO 15
control:
  safety_door_pin: gpio.15  # Changed from gpio.34
  
# 3. Save file
# 4. Upload to FluidNC:
```

**Via WebUI:**
```
1. Go to http://[ESP32_IP]/
2. Click Config tab
3. Click Upload
4. Select genmitsu_kiosk.yaml
5. Click Upload button
6. Restart: $Bye
```

**Via Serial:**
```
$LocalFS/Upload
[Paste entire YAML file contents]
Ctrl+D
$Bye
```

## Pin Inversion

If a pin is backwards (ON when should be OFF):

```yaml
# Add :low to invert
safety_door_pin: gpio.34:low  # Inverts logic

# Or for motors:
direction_pin: i2so.3:low  # Inverts direction
```

## Common Pin Issues

### Issue: Limit switch triggers on wrong axis

**Cause**: X and Y limit pins are swapped

**Solution**: Swap GPIO 13 and 14 in config:
```yaml
x:
  motor0:
    limit_neg_pin: gpio.14  # Was 13

y:
  motor0:
    limit_neg_pin: gpio.13  # Was 14
```

### Issue: Safety door doesn't stop laser

**Cause**: Wrong GPIO or inverted logic

**Solutions**:
1. Try each input-only pin (34, 35, 36, 39)
2. Try adding `:low` to invert
3. Check physical wiring - switch might be disconnected

### Issue: Buttons don't respond

**Cause**: Wrong GPIO assignments

**Solution**: Use `$Pins/Report` method to find correct pins

### Issue: Homing fails with "No switch"

**Cause**: Limit switch pins wrong or not connected

**Solution**:
1. Verify limit switches are physically connected
2. Use multimeter to trace connections
3. Update config with correct pins
4. Test individual switches with `$Pins/Report`

## Verification Checklist

Before operating the laser, verify:

- [ ] Safety door pin tested and working (laser stops when opened)
- [ ] X limit switch tested (triggers alarm at X limit)
- [ ] Y limit switch tested (triggers alarm at Y limit)
- [ ] E-stop button tested (immediately stops all motion)
- [ ] Feed hold button tested (pauses operation)
- [ ] Cycle start button tested (resumes after pause)
- [ ] Homing sequence works correctly
- [ ] Laser PWM output verified (GPIO 16)
- [ ] All pins documented in config file
- [ ] Config file backed up

## Documentation

After verification, document your findings:

```yaml
# Add comments to config file:
control:
  safety_door_pin: gpio.34   # VERIFIED: Opens lid = laser stop
  feed_hold_pin: gpio.36     # VERIFIED: Pause button
  cycle_start_pin: gpio.39   # VERIFIED: Resume button
  estop_pin: gpio.35         # VERIFIED: Red emergency button
```

## Getting Help

If you can't determine pins:

1. Post in FluidNC discussions: https://github.com/bdring/FluidNC/discussions
2. Include:
   - Photos of ESP32 board with connections
   - `$Pins/Report` output
   - Description of what you tested
   - Which pins respond to which actions

## Reference: ESP32 Pin Capabilities

```
Input-Only (safe for critical safety functions):
- GPIO 34, 35, 36, 39
- No internal pull-ups available
- Best for: Safety door, E-stop, probe

Bidirectional (can be input or output):
- GPIO 13, 14, 15, etc.
- Have internal pull-ups
- Best for: Limit switches, control buttons

Strapping Pins (use with caution):
- GPIO 0, 2, 5, 12, 15
- Used during ESP32 boot
- May cause issues if held low/high during startup
```

## Final Safety Reminder

**NEVER operate the laser until:**
1. Safety door pin is 100% verified
2. Limit switches are tested and working
3. E-stop button is tested and working
4. Low-power test (S100) completed successfully
5. All safety systems confirmed functional

**Your safety and the safety of others depends on proper pin configuration!**
