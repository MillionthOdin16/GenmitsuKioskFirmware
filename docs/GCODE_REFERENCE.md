# G-Code Command Reference for Genmitsu Kiosk

This document details the G-code commands supported by the Genmitsu Kiosk 2.5W laser engraver firmware (based on Grbl_ESP32).

## Overview

The Genmitsu Kiosk implements the GRBL G-code dialect with laser-specific extensions. GRBL is a widely-used open-source CNC controller firmware that interprets standard G-code commands for motion control.

## Command Categories

### Motion Commands (G-codes)

#### G0 - Rapid Linear Move
```gcode
G0 X10 Y20
```
- Moves at maximum speed to specified coordinates
- Used for non-cutting moves
- In laser mode, laser is automatically turned off during G0

#### G1 - Linear Move (Feed Rate)
```gcode
G1 X10 Y20 F500
```
- Linear interpolation at specified feed rate
- F parameter sets feed rate in mm/min
- In laser mode with M3, power is constant
- In laser mode with M4, power varies with speed

#### G2 - Clockwise Arc
```gcode
G2 X10 Y10 I5 J5 F500
```
- Circular interpolation (clockwise)
- I, J specify arc center offset from current position
- Can also use R for radius mode: `G2 X10 Y10 R5`

#### G3 - Counter-Clockwise Arc
```gcode
G3 X10 Y10 I5 J5 F500
```
- Circular interpolation (counter-clockwise)
- Same parameters as G2

### Coordinate System Commands

#### G17, G18, G19 - Plane Selection
```gcode
G17  ; XY plane (default for laser)
G18  ; ZX plane
G19  ; YZ plane
```

#### G20, G21 - Units
```gcode
G20  ; Inches
G21  ; Millimeters (default)
```

#### G28 - Go to Predefined Position
```gcode
G28      ; Return to G28 stored position
G28.1    ; Store current position as G28
```

#### G30 - Go to Predefined Position
```gcode
G30      ; Return to G30 stored position
G30.1    ; Store current position as G30
```

#### G53 - Move in Machine Coordinates
```gcode
G53 G0 X0 Y0  ; Move to machine zero
```
- Temporarily use machine coordinates
- Bypasses work coordinate offsets
- Error: "Gcode G53 invalid motion mode"

#### G54-G59 - Work Coordinate Systems
```gcode
G54  ; Use coordinate system 1 (default)
G55  ; Use coordinate system 2
G56  ; Use coordinate system 3
G57  ; Use coordinate system 4
G58  ; Use coordinate system 5
G59  ; Use coordinate system 6
```

#### G90, G91 - Distance Mode
```gcode
G90  ; Absolute positioning (default)
G91  ; Incremental/relative positioning
```

#### G92 - Set Position
```gcode
G92 X0 Y0  ; Set current position as 0,0
G92.1      ; Clear G92 offset
```

### Spindle/Laser Control Commands

#### M3 - Spindle/Laser ON (Constant Power)
```gcode
M3 S500    ; Turn on at power level 500
```
- In laser mode: Constant power regardless of speed
- S parameter: Power level (0-1000 or 0-100 depending on $GCode/MaxS)
- Laser stays on during motion, off during rapids (G0)

#### M4 - Spindle/Laser ON (Dynamic Power)
```gcode
M4 S800    ; Turn on at power level 800
```
- **Laser Mode Only**: Power varies with feed rate
- Ideal for engraving - darker at slower speeds
- Error if not in laser mode: "M4 requires laser mode or a reversible spindle"
- Automatically adjusts power to maintain consistent material removal

#### M5 - Spindle/Laser OFF
```gcode
M5
```
- Turns off laser/spindle
- Safe command, always available

### Program Control

#### M0, M1 - Program Pause
```gcode
M0   ; Pause (wait for cycle start)
M1   ; Optional pause
```

#### M2, M30 - Program End
```gcode
M2   ; Program end
M30  ; Program end with return to start
```

### Coolant Control (Typically Unused for Laser)

#### M7, M8, M9 - Coolant
```gcode
M7   ; Mist coolant on
M8   ; Flood coolant on
M9   ; Coolant off
```

## GRBL Special Commands ($ Commands)

### System Commands

#### $$ - View Settings
```gcode
$$
```
- Displays all configuration settings
- Shows current values for all $ parameters

#### $# - View Coordinate Offsets
```gcode
$#
```
- Shows all work coordinate offsets (G54-G59)
- Shows G28 and G30 positions
- Shows tool length offsets

#### $G - View Parser State
```gcode
$G
```
- Shows active G-code modes
- Example output: `[GC:G0 G54 G17 G21 G90 G94 M5 M9 T0 F0 S0]`

#### $I - View Build Info
```gcode
$I
```
- Shows firmware version and build date
- Format: `Grbl_ESP32 Ver <version> Date <date>`

#### $N - View Startup Blocks
```gcode
$N
```
- Shows startup G-code lines (auto-run on boot)

#### $X - Kill Alarm Lock
```gcode
$X
```
- Clears alarm state
- Allows motion after alarm
- Use carefully - ensure machine is in safe state

#### $H - Run Homing Cycle
```gcode
$H
```
- Executes homing sequence
- Finds limit switches and sets machine zero
- Required before motion if homing is enabled

### Jogging Commands

#### $J - Jog Command
```gcode
$J=G21 G91 X10 F500   ; Jog 10mm in X at 500mm/min
```
- Special jogging mode
- Always in incremental mode (G91)
- Can be cancelled with feed hold or jog cancel
- Error: "Invalid jog command"

### Settings Commands

#### $<setting>=<value> - Set Configuration
```gcode
$100=800.0        ; Set X steps/mm
$GCode/MaxS=1000  ; Set max spindle/laser power
$Laser/FullPower=1000  ; Set laser full power value
```

Common settings:
- `$0-$999`: Numeric settings
- `$GCode/LaserMode`: Enable/disable laser mode
- `$GCode/MaxS`: Maximum S value (power)
- `$GCode/MinS`: Minimum S value
- `$Laser/FullPower`: Full power PWM value

### Real-Time Commands

These are single characters sent without waiting:

#### ? - Status Query
```
?
```
- Returns current machine state
- Format: `<Idle|MPos:0.000,0.000,0.000|FS:0,0>`

#### ~ - Cycle Start/Resume
```
~
```
- Start/resume from pause or feed hold

#### ! - Feed Hold
```
!
```
- Pause motion immediately
- Can be resumed with ~

#### Ctrl-X - Reset
```
0x18 (Ctrl-X)
```
- Software reset
- Stops all motion
- Clears buffers

## Laser-Specific Features

### Laser Mode ($GCode/LaserMode)

When enabled:
- G0 (rapids) automatically turn laser off
- M4 enables dynamic power (varies with speed)
- Safety features prevent accidental firing

```gcode
$GCode/LaserMode=On    ; Enable laser mode
$GCode/LaserMode=Off   ; Disable (for spindle mode)
```

### Power Scaling

Laser power is scaled based on settings:
```gcode
$GCode/MinS=0          ; Minimum S value
$GCode/MaxS=1000       ; Maximum S value (typical)
$Laser/FullPower=1000  ; PWM value for full power
```

If `$GCode/MaxS=1000`:
- `S0` = laser off
- `S500` = 50% power
- `S1000` = 100% power

If `$GCode/MaxS=100`:
- `S0` = laser off
- `S50` = 50% power
- `S100` = 100% power

### Example Laser Operations

#### Simple Engraving
```gcode
G21              ; Millimeters
G90              ; Absolute positioning
G17              ; XY plane
M4 S800          ; Laser on at 80% power (dynamic)
G1 X10 Y0 F1000  ; Engrave line
G1 X10 Y10       ; Engrave line
G1 X0 Y10        ; Engrave line
G1 X0 Y0         ; Engrave line
M5               ; Laser off
```

#### Cutting Operation
```gcode
G21              ; Millimeters
G90              ; Absolute positioning
M3 S1000         ; Laser on at 100% (constant power)
G1 X50 Y0 F300   ; Cut slowly
G1 X50 Y50       ; Cut
G1 X0 Y50        ; Cut
G1 X0 Y0         ; Cut
M5               ; Laser off
```

## Error Messages

From firmware analysis, common G-code errors:

- `Expected GCode command letter` - Missing G or M
- `Bad GCode number format` - Invalid number
- `Gcode modal group violation` - Conflicting commands
- `Gcode undefined feed rate` - F parameter not set
- `Gcode invalid target` - Invalid coordinates
- `Gcode arc radius error` - Arc parameters don't match
- `Gcode G43 dynamic axis error` - Tool length offset error
- `Gcode max value exceeded` - Value out of range
- `Unsupported GCode command` - Command not implemented

## Safety Notes

### Before Operating

1. **Enable Laser Mode**:
   ```gcode
   $GCode/LaserMode=On
   ```

2. **Set Safe Power Limits**:
   ```gcode
   $GCode/MinS=0
   $GCode/MaxS=1000
   $Laser/FullPower=1000
   ```

3. **Test at Low Power**:
   ```gcode
   M4 S100   ; 10% power for alignment
   ```

### Emergency Stop

- Press **RESET** button on device
- Send `Ctrl-X` via serial
- Cut power to laser
- Use physical E-stop if available

### Best Practices

1. Always test G-code with laser off first (M5)
2. Use M4 (dynamic power) for engraving
3. Use M3 (constant power) for cutting
4. Never leave laser unattended
5. Always wear proper eye protection
6. Keep work area clear of flammable materials

## Web Interface Commands

Via HTTP/WebSocket:
```
/command?cmd=<gcode>          ; Execute G-code
/command_silent?cmd=<gcode>   ; Execute without echo
$name                         ; Show setting
$name=value                   ; Set value
```

## Coordinate Systems Summary

| System | Command | Purpose |
|--------|---------|---------|
| Machine | G53 | Absolute machine coordinates |
| Work 1 | G54 | Default work coordinate system |
| Work 2 | G55 | Additional work offset |
| Work 3 | G56 | Additional work offset |
| Work 4 | G57 | Additional work offset |
| Work 5 | G58 | Additional work offset |
| Work 6 | G59 | Additional work offset |
| G28 | G28 | Predefined position 1 |
| G30 | G30 | Predefined position 2 |

## Reference

- GRBL Documentation: https://github.com/gnea/grbl/wiki
- Grbl_ESP32 Wiki: https://github.com/bdring/Grbl_Esp32/wiki
- G-code Standard: ISO 6983

---

**Based on**: Genmitsu Kiosk Firmware (C07-251021)  
**Firmware**: Grbl_ESP32  
**Compatibility**: Standard GRBL 1.1+ with ESP32 extensions
