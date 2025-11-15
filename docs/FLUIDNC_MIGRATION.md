# FluidNC Migration Guide for Genmitsu Kiosk

## 🚀 Ready to Migrate?

**→ See [FLUIDNC_INSTALLATION.md](FLUIDNC_INSTALLATION.md) for the complete step-by-step installation guide.**

This document provides analysis and comparison. The installation guide provides actionable steps.

---

## Executive Summary

**Current Firmware**: Grbl_ESP32 v1.3a (2021-11-03) - Latest stable release  
**Next Generation**: FluidNC v3.9.9 (Active development, 2971+ commits)  
**Migration Status**: ✅ **POSSIBLE** - Hardware is compatible  
**Recommendation**: ⚠️ **Consider carefully** - See pros/cons below

**For Installation**: → [FLUIDNC_INSTALLATION.md](FLUIDNC_INSTALLATION.md)

---

## What is FluidNC?

FluidNC is the **next-generation successor** to Grbl_ESP32, completely rewritten from scratch by the same development team (Bart Dring and contributors).

### Key Differences

| Aspect | Grbl_ESP32 (Current) | FluidNC (Next Gen) |
|--------|---------------------|-------------------|
| **Status** | Maintenance mode (stable) | Active development |
| **Last Release** | v1.3a (Nov 2021) | v3.9.9 (Oct 2025) |
| **Total Commits** | ~500 | **2971+** |
| **Architecture** | Monolithic C | Object-oriented C++ |
| **Configuration** | Compile-time (C header) | **Runtime (YAML file)** |
| **Web UI** | ESP3D v2.1 | **WebUI 3 (modern)** |
| **ESP32 Support** | ESP32 only | ESP32, ESP32-S2, **ESP32-S3** |
| **Firmware Size** | ~1.2 MB | ~2.5-3 MB (larger) |
| **Features** | Core CNC/Laser | Core + **ATC, Plasma, Multi-tool** |
| **Updates** | Manual reflash | Runtime config changes |
| **Learning Curve** | Moderate | Higher (YAML config) |

---

## FluidNC Features vs Grbl_ESP32

### New Features in FluidNC

✅ **Runtime Configuration**
- No compilation needed - just edit YAML file
- Change settings via web or serial
- Multiple config files supported
- Live config switching

✅ **Advanced Machine Support**
- Automatic tool changers (ATC)
- Plasma cutters
- Multi-tool machines (laser + spindle)
- Tool length offsets (TLO)
- More complex kinematics

✅ **Modern Web UI (WebUI 3)**
- Responsive design (phone, tablet, desktop)
- Real-time visualizer
- Macro support in UI
- Work coordinate system (WCS) management
- Dark mode

✅ **Enhanced Safety**
- Probe hard limits
- Better error handling
- Improved homing reliability
- WPA3 WiFi security

✅ **Better Extensibility**
- Plugin architecture
- Hardware abstraction layer
- Easier to add custom features
- Better code organization

### Features Preserved from Grbl_ESP32

✅ 100% Grbl G-code compatibility  
✅ I2S stepper control  
✅ WiFi connectivity  
✅ Web interface  
✅ Laser mode (M3/M4)  
✅ Homing and limits  
✅ Real-time commands  
✅ OTA updates  

### What You Lose (vs Current Setup)

❌ **Simplicity** - YAML configuration is more complex than C header  
❌ **Stability** - Active development means more frequent changes  
❌ **Smaller footprint** - FluidNC is 2-3x larger  
❌ **Well-tested** - Grbl_ESP32 v1.3a is battle-tested for 4 years  

---

## Hardware Compatibility

### Genmitsu Kiosk Hardware Analysis

| Component | Grbl_ESP32 | FluidNC | Compatible? |
|-----------|------------|---------|-------------|
| **ESP32 Chip** | ESP32 (dual-core) | ESP32/S2/S3 | ✅ YES |
| **Flash** | 4MB | 4MB minimum | ✅ YES |
| **RAM** | 520KB | ~300KB used | ✅ YES |
| **I2S Steppers** | Supported | Supported | ✅ YES |
| **PWM Laser** | Supported | Laser spindle | ✅ YES |
| **WiFi** | 2.4GHz | 2.4GHz + WPA3 | ✅ YES (improved) |
| **GPIOs** | All available | All available | ✅ YES |

**Verdict**: ✅ **Genmitsu Kiosk CAN run FluidNC** - Hardware is fully compatible.

---

## Migration Process

### Phase 1: Preparation (Before Flashing)

1. **Backup Current Firmware**
   ```bash
   # Read entire 4MB flash
   esptool.py --port /dev/ttyUSB0 --baud 460800 read_flash 0 0x400000 genmitsu_backup_full.bin
   
   # Backup NVS partition (settings)
   esptool.py --port /dev/ttyUSB0 read_flash 0x9000 0x6000 genmitsu_nvs_backup.bin
   ```

2. **Document Current Settings**
   - Connect to web interface
   - Save all $$ settings to text file
   - Note WiFi credentials
   - Screenshot web dashboard

3. **Download FluidNC**
   ```bash
   git clone https://github.com/bdring/FluidNC.git
   cd FluidNC
   git checkout v3.9.9  # Latest stable tag
   ```

### Phase 2: Create Configuration File

FluidNC uses YAML instead of C headers. Here's the Genmitsu Kiosk config:

**File**: `genmitsu_kiosk.yaml`

```yaml
name: Genmitsu Kiosk 2.5W Laser
board: Custom ESP32

# Machine type and settings
stepping:
  engine: I2S_STREAM
  idle_ms: 25                    # Stepper idle delay (from $1)
  dir_delay_us: 1                # Direction setup delay
  pulse_us: 3                    # Step pulse width (from $0)
  disable_delay_us: 0

# I2S Configuration (GPIO 25, 26, 27)
i2s_stream:
  bck_pin: gpio.25               # I2S bit clock
  ws_pin: gpio.26                # I2S word select  
  data_pin: gpio.27              # I2S data

# Axes configuration
axes:
  shared_stepper_disable_pin: NO_PIN
  
  x:
    steps_per_mm: 100.000        # From $100
    max_rate_mm_per_min: 12000   # From $110 (VERIFIED from hardware)
    acceleration_mm_per_sec2: 800 # From $120 (VERIFIED from hardware)
    max_travel_mm: 100.000       # From $130 (work area)
    
    homing:
      cycle: 2                   # From $22 (enabled)
      mpos_mm: 0                 # Machine position after homing
      positive_direction: false  # From $23=7 (home negative)
      seek_mm_per_min: 2000      # From $25 (VERIFIED from hardware)
      feed_mm_per_min: 800       # From $24 (VERIFIED from hardware)
    
    motor0:
      limit_neg_pin: NO_PIN      # Configure if using limit switches
      limit_pos_pin: NO_PIN
      hard_limits: true          # From $21=1
      pulloff_mm: 2.000          # From $27 (VERIFIED from hardware)
      
      standard_stepper:
        step_pin: i2so.0         # I2S stream output bit 0
        direction_pin: i2so.1    # I2S stream output bit 1
        disable_pin: NO_PIN
  
  y:
    steps_per_mm: 100.000        # From $101
    max_rate_mm_per_min: 12000   # From $111 (VERIFIED from hardware)
    acceleration_mm_per_sec2: 240 # From $121 (VERIFIED - asymmetric!)
    max_travel_mm: 100.000       # From $131 (work area)
    
    homing:
      cycle: 2
      mpos_mm: 0
      positive_direction: false  # From $23=7
      seek_mm_per_min: 2000      # From $25
      feed_mm_per_min: 800       # From $24
    
    motor0:
      limit_neg_pin: NO_PIN
      limit_pos_pin: NO_PIN
      hard_limits: true
      pulloff_mm: 2.000
      
      standard_stepper:
        step_pin: i2so.2         # I2S stream output bit 2
        direction_pin: i2so.3:low # I2S bit 3, INVERTED (from $3=4)
        disable_pin: NO_PIN

# Laser spindle configuration
laser:
  pwm_hz: 5000                   # 5kHz PWM (VERIFIED from binary)
  output_pin: gpio.16            # Laser PWM pin (high confidence)
  enable_pin: NO_PIN             # Or configure if separate enable exists
  disable_with_s0: false
  s0_with_disable: true
  tool_num: 0
  speeds: 
    0=0.000%                     # From $31 (min speed)
    1000=100.000%                # From $30 (max speed)

# Motion control
start:
  must_home: false               # Set true if homing required
  deactivate_parking: true
  check_limits: false

# User interface
user_outputs:
  analog0_pin: NO_PIN
  analog1_pin: NO_PIN
  analog2_pin: NO_PIN
  analog3_pin: NO_PIN
  digital0_pin: NO_PIN
  digital1_pin: NO_PIN
  digital2_pin: NO_PIN
  digital3_pin: NO_PIN

# Control pins
control:
  safety_door_pin: NO_PIN
  reset_pin: NO_PIN
  feed_hold_pin: NO_PIN
  cycle_start_pin: NO_PIN
  macro0_pin: NO_PIN
  macro1_pin: NO_PIN
  macro2_pin: NO_PIN
  macro3_pin: NO_PIN

# Probe
probe:
  pin: NO_PIN
  check_mode_start: false
```

### Phase 3: Build and Flash FluidNC

```bash
# Install PlatformIO if needed
pip install platformio

# Build FluidNC
cd FluidNC
pio run -e wifi

# Flash to ESP32
pio run -e wifi -t upload

# Or use esptool directly
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x10000 .pio/build/wifi/firmware.bin
```

### Phase 4: Upload Configuration

**Method 1: Via Serial**
```bash
# Upload config file
python fluidterm/fluidterm.py /dev/ttyUSB0 --upload genmitsu_kiosk.yaml
```

**Method 2: Via Web UI**
1. Connect to `FluidNC` WiFi AP (default password: `12345678`)
2. Navigate to http://fluidnc.local or http://192.168.0.1
3. Go to Config tab
4. Upload `genmitsu_kiosk.yaml`
5. Reboot

**Method 3: Via SD Card** (if available)
1. Copy `genmitsu_kiosk.yaml` to SD card as `config.yaml`
2. Insert SD card
3. Reset ESP32
4. FluidNC loads config from SD

### Phase 5: Testing

1. **Connect and verify**
   ```bash
   # Check system responds
   echo "?" | nc fluidnc.local 23
   ```

2. **Test movements** (LOW POWER!)
   ```gcode
   $X              # Unlock
   G91             # Relative mode
   G0 X10 F1000    # Move X 10mm at low speed
   G0 Y10 F1000    # Move Y 10mm
   ```

3. **Test laser** (VERY LOW POWER!)
   ```gcode
   M3 S100         # Laser at 10% power
   M5              # Laser off
   ```

4. **Test homing** (if limits connected)
   ```gcode
   $H              # Home all axes
   ```

---

## Comparison: Before & After

### Configuration Management

**Grbl_ESP32 (Current)**:
```
1. Edit genmitsu_kiosk_machine.h
2. Compile firmware (5-10 minutes)
3. Flash entire firmware (1-2 minutes)
4. Test changes
5. Repeat if wrong
```

**FluidNC (New)**:
```
1. Edit genmitsu_kiosk.yaml
2. Upload config file (5 seconds)
3. Reboot (5 seconds)
4. Test changes
5. Edit and upload again if needed
```

### Web Interface Comparison

**Grbl_ESP32 ESP3D v2.1**:
- Simple, functional interface
- Basic controls
- Real-time jog
- File upload
- Settings page

**FluidNC WebUI 3**:
- Modern responsive design
- 3D visualizer
- Macro buttons
- WCS management  
- Tablet-optimized
- Dark mode
- Better mobile support

### Performance Impact

| Metric | Grbl_ESP32 | FluidNC | Impact |
|--------|------------|---------|--------|
| Boot time | ~2 sec | ~3-4 sec | Slightly slower |
| RAM usage | ~120 KB | ~280 KB | Higher but OK |
| Flash usage | 1.24 MB | 2.5-3 MB | Still fits in 4MB |
| Motion performance | Excellent | Excellent | Same |
| Web response | Good | Better | Improved |

---

## Pros and Cons

### Advantages of Migrating to FluidNC

✅ **No recompilation needed** - Edit YAML, upload, done  
✅ **Better web interface** - Modern, responsive, feature-rich  
✅ **Active development** - Bug fixes, new features  
✅ **Better documentation** - Comprehensive wiki  
✅ **Future-proof** - ESP32-S3 support for future hardware  
✅ **More flexible** - Easy to try different settings  
✅ **Better error messages** - More helpful diagnostics  
✅ **WPA3 support** - Better WiFi security  

### Disadvantages of Migrating to FluidNC

❌ **Learning curve** - YAML syntax, new concepts  
❌ **Less stable** - Active development = occasional bugs  
❌ **Larger firmware** - 2x size (but still fits)  
❌ **More complex** - More features = more to understand  
❌ **Migration effort** - Takes time to convert config  
❌ **Risk** - Could brick device if done incorrectly  
❌ **Unnecessary** - Current firmware works perfectly  

---

## Recommendations

### For Most Users: ❌ **DO NOT MIGRATE**

**Reasons**:
1. **Current firmware is perfect** - v1.3a is stable, tested, works
2. **No critical bugs** - Nothing broken that needs fixing
3. **All features work** - Laser, WiFi, homing, web UI
4. **Risk vs reward** - Small gains, potential for problems
5. **Time investment** - Hours to migrate and test

**Stick with Grbl_ESP32 v1.3a if**:
- Machine works perfectly now
- You use it for production work
- You don't need advanced features
- You value stability over new features

### For Advanced Users: ⚠️ **CONSIDER MIGRATION**

**You might want FluidNC if**:
- You frequently tweak machine parameters
- You want the latest web interface
- You plan to add features (tool changer, etc.)
- You enjoy experimenting
- You have a backup machine for production
- You're comfortable troubleshooting

### For Developers: ✅ **MIGRATE**

**FluidNC is better if**:
- You're developing custom firmware
- You need rapid iteration on config
- You want to contribute to open source
- You need multi-tool support
- You're building a new machine from scratch

---

## Migration Risks

### Risk Level: **MEDIUM**

**What Could Go Wrong**:
1. **Incorrect YAML** - Machine doesn't move or moves wrong
2. **GPIO mismatch** - Could damage hardware if pins wrong
3. **Settings loss** - Lose all calibration if not documented
4. **Bricked device** - Incorrect flash could require recovery
5. **Web UI issues** - Different interface, learning curve
6. **Incompatibility** - Existing G-code senders might need updates

### Risk Mitigation

✅ **MUST DO before migration**:
1. ✅ Backup entire flash (4MB dump)
2. ✅ Document all $$ settings
3. ✅ Save WiFi credentials
4. ✅ Test configuration in simulation first
5. ✅ Have esptool ready for recovery
6. ✅ Set aside 2-4 hours for migration
7. ✅ Test at LOW laser power initially

---

## Recovery Plan

If migration fails:

### Emergency Recovery Steps

```bash
# 1. Flash bootloader
esptool.py --port /dev/ttyUSB0 write_flash 0x1000 bootloader.bin

# 2. Restore original firmware
esptool.py --port /dev/ttyUSB0 write_flash 0 genmitsu_backup_full.bin

# 3. Restore NVS (settings)
esptool.py --port /dev/ttyUSB0 write_flash 0x9000 genmitsu_nvs_backup.bin

# 4. Verify
esptool.py --port /dev/ttyUSB0 verify_flash 0 genmitsu_backup_full.bin
```

**Recovery Time**: 5-10 minutes if backup available

---

## Example Use Cases

### When FluidNC Makes Sense

**Scenario 1: Multiple Materials**
- Need different settings for wood vs acrylic vs metal
- FluidNC: Switch between `wood.yaml`, `acrylic.yaml`, `metal.yaml`
- Grbl_ESP32: Recompile and flash each time

**Scenario 2: Experimentation**
- Testing optimal speeds/accelerations
- FluidNC: Edit YAML, upload (30 seconds), test
- Grbl_ESP32: Edit C, compile, flash (10 minutes), test

**Scenario 3: Field Updates**
- Remote machines that need config changes
- FluidNC: Send YAML file via WiFi
- Grbl_ESP32: Must physically access for firmware update

### When Grbl_ESP32 Is Better

**Scenario 1: Production**
- Machine runs same jobs daily
- Settings never change
- Grbl_ESP32: Stable, proven, no surprises

**Scenario 2: Critical Applications**
- Downtime is expensive
- Can't afford experimental firmware
- Grbl_ESP32: Battle-tested reliability

---

## Cost-Benefit Analysis

### Time Investment

| Activity | Grbl_ESP32 | FluidNC | Difference |
|----------|------------|---------|------------|
| **Initial Setup** | 2-4 hours | 4-6 hours | +2 hours |
| **Config Change** | 10-15 min | 30 seconds | **-10 min** |
| **Learning Curve** | Moderate | Higher | +4-8 hours |
| **Maintenance** | Low | Medium | +1-2 hours/year |

**Break-even**: ~20-30 configuration changes

### Feature Value

**High value for**:
- Multiple machine profiles
- Frequent parameter tuning
- Advanced features (ATC, plasma)
- Latest web UI features

**Low value for**:
- Set-and-forget operation
- Simple laser engraving
- Production environments
- Non-technical users

---

## Conclusion

### Summary

✅ **Hardware Compatible**: Genmitsu Kiosk CAN run FluidNC  
⚠️ **Not Necessary**: Current firmware (Grbl_ESP32 v1.3a) is excellent  
🎯 **Best For**: Advanced users who need flexibility  
❌ **Not For**: Production users who value stability  

### Final Recommendation

**For 90% of Genmitsu Kiosk users**: ✅ **KEEP Grbl_ESP32 v1.3a**

**Reasons**:
1. Current firmware is the latest stable Grbl_ESP32
2. All features work perfectly
3. Migration has risks with modest benefits
4. No critical bugs or security issues
5. Grbl_ESP32 is mature and proven

**For 10% of users who should migrate**: ✅ **Try FluidNC**

**If you are**:
- Developer experimenting with firmware
- Need frequent configuration changes
- Want cutting-edge features
- Have time to learn YAML configuration
- Can afford downtime if things go wrong

---

## Resources

### FluidNC Documentation
- **Wiki**: http://wiki.fluidnc.com
- **Repository**: https://github.com/bdring/FluidNC
- **Discord**: https://discord.gg/w3FBD9p (community support)
- **Config Examples**: https://github.com/bdring/FluidNC/tree/main/example_configs

### Grbl_ESP32 Documentation
- **Wiki**: https://github.com/bdring/Grbl_Esp32/wiki
- **Repository**: https://github.com/bdring/Grbl_Esp32
- **Current Version**: v1.3a (November 3, 2021)

### Community
- **Discord**: Both projects share same Discord server
- **GitHub Issues**: Report bugs, ask questions
- **YouTube**: Many tutorial videos available

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**FluidNC Version Analyzed**: v3.9.9  
**Recommendation**: Stay on Grbl_ESP32 for most users
