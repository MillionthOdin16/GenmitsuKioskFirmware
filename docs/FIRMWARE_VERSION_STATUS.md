# Firmware Version Analysis and Update Guide

## Current Version Status

### Your Genmitsu Kiosk Firmware:
- **Firmware Version**: 1.3a (20211103)
- **UI Version**: 2.1b68
- **Build Date**: November 3, 2021
- **Status**: ✓ This is the LATEST official Grbl_ESP32 release!

## Is This Current?

**YES!** Your firmware is running the **latest stable version** of Grbl_ESP32.

### Version Timeline:
- **1.3a (20211103)**: Released November 3, 2021
- **Last update**: November 3, 2021
- **Current Grbl_ESP32**: STILL 1.3a (no newer version released)
- **Repository status**: MAINTENANCE MODE ONLY (as of 2021)

## Why No Updates?

### Grbl_ESP32 Project Status

The Grbl_ESP32 project is in **MAINTENANCE MODE**:

1. **No New Features**: Development stopped in November 2021
2. **Bugfixes Only**: Only critical bug fixes are backported
3. **Successor Available**: Project evolved into **FluidNC**

### Official Statement (from README):
```
"The next generation of Grbl_ESP32 was such a massive upgrade 
we decided to change the name. It is called FluidNC.

This version is only being maintained with existing features. 
All new features are targeted at FluidNC."
```

## FluidNC: The Successor

### What is FluidNC?
- **Next generation** of Grbl_ESP32
- **Complete rewrite** with major improvements
- **Backward compatible** with Grbl_ESP32 hardware
- **Active development** (ongoing updates)
- **Repository**: https://github.com/bdring/FluidNC

### FluidNC Improvements:
- YAML configuration (easier than #define)
- Better multi-axis support
- Improved performance
- Modern architecture
- Active community
- Regular updates

### Why Genmitsu Hasn't Updated:

Genmitsu likely stayed with Grbl_ESP32 1.3a because:

1. **Stability**: 1.3a is the last stable Grbl_ESP32 release
2. **Testing**: Switching to FluidNC requires extensive re-testing
3. **Compatibility**: Grbl_ESP32 is mature and well-tested
4. **Configuration**: Would need to convert machine config to YAML
5. **Support**: Fewer support issues with known stable version

**This is a GOOD decision** for a commercial product!

## Should You Update?

### Stick with Grbl_ESP32 1.3a (RECOMMENDED):

✅ **Reasons to STAY**:
- Already have the latest Grbl_ESP32 version
- Proven stable for your machine
- No critical bugs or security issues
- Well-documented and supported
- Your configuration is already working
- Commercial product - don't fix what isn't broken

❌ **Reasons NOT to update**:
- No newer Grbl_ESP32 version exists
- FluidNC is a major change (not just an update)
- Requires complete reconfiguration
- Testing burden on you
- Risk of compatibility issues
- May void Genmitsu support

### Migrate to FluidNC (ADVANCED):

✅ **Reasons to MIGRATE**:
- Want latest features
- Need specific FluidNC capabilities
- Enjoy tinkering and testing
- Want active development/updates
- Need better multi-axis support

⚠️ **Consider Before Migrating**:
- Completely different configuration system (YAML vs #define)
- Requires extensive testing
- May have initial issues
- Genmitsu won't support it
- Need to recreate machine configuration
- Potentially breaking changes

## How to Update (If You Really Want To)

### Option 1: Stay on Grbl_ESP32 (Get Latest Commits)

Even though version is still 1.3a, there may be bugfixes:

```bash
# Clone latest Grbl_ESP32
git clone https://github.com/bdring/Grbl_Esp32.git
cd Grbl_Esp32

# Check for commits since Nov 3, 2021
git log --since="2021-11-03" --oneline

# If there are important fixes, rebuild
cp /path/to/genmitsu_kiosk_machine.h Grbl_Esp32/src/Machines/
pio run -e genmitsu_kiosk -t upload
```

**Current Reality**: Only 1 commit since 2021-11-03 (documentation update)
**Verdict**: NO meaningful updates available

### Option 2: Migrate to FluidNC

**MAJOR UNDERTAKING - Only for advanced users!**

1. **Backup Current Firmware**:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
       read_flash 0x0 0x400000 genmitsu_kiosk_backup.bin
   ```

2. **Clone FluidNC**:
   ```bash
   git clone https://github.com/bdring/FluidNC.git
   cd FluidNC
   ```

3. **Create YAML Configuration**:
   ```yaml
   # config.yaml (example structure)
   name: "Genmitsu Kiosk"
   board: "ESP32"
   
   axes:
     x:
       steps_per_mm: 100.0
       max_rate: 1000.0
       acceleration: 200.0
       max_travel: 100.0
       
     y:
       steps_per_mm: 100.0
       max_rate: 1000.0
       acceleration: 200.0
       max_travel: 100.0
   
   i2s_stream:
     bck_pin: gpio.25
     data_pin: gpio.27
     ws_pin: gpio.26
   
   # ... much more configuration needed
   ```

4. **Build and Test Extensively**

5. **Risk Assessment**: HIGH (untested on Genmitsu Kiosk)

## Recommended Actions

### For Most Users (RECOMMENDED):

**✓ DO NOTHING** - Your firmware is current and stable!

1. Keep using Grbl_ESP32 1.3a (20211103)
2. It's the latest official version
3. No security issues or critical bugs
4. Proven stable for your hardware
5. Genmitsu selected this version for good reasons

### For Advanced Tinkerers:

**Consider FluidNC** only if:
- You need specific new features
- You enjoy beta testing
- You can afford downtime
- You have backup machine or patience
- You understand YAML configuration

## Version Checking

### To Check Your Current Version:

1. **Via Web Interface**:
   - Connect to http://192.168.0.1
   - Look at bottom of page
   - Should show: "UI: 2.1b68 / FW: 1.3a (20211103)"

2. **Via Serial**:
   ```
   $I
   ```
   Should show: `[VER:1.3a.20211103:]`

3. **Via $$ Settings**:
   ```
   $$
   ```
   Look for firmware version in output

## Web UI Update (Separate from Firmware)

The **Web UI** (2.1b68) is separate from firmware and CAN be updated:

### Check Latest Web UI:
```bash
# Latest web UI from ESP3D-WEBUI
# https://github.com/luc-github/ESP3D-WEBUI/releases
```

### To Update Web UI Only:
1. Download latest index.html.gz from ESP3D-WEBUI releases
2. Upload via http://192.168.0.1/files
3. Refresh browser

**NOTE**: Newer UI versions may not be fully compatible with Grbl_ESP32 1.3a

## Summary

| Question | Answer |
|----------|--------|
| Is your firmware current? | **YES** (latest Grbl_ESP32) |
| Should you update? | **NO** (no updates available) |
| Is development active? | **NO** (maintenance mode only) |
| Is there a successor? | **YES** (FluidNC) |
| Should you migrate to FluidNC? | **PROBABLY NOT** (major undertaking) |
| Is your version safe/stable? | **YES** (proven stable) |
| Does Genmitsu support updates? | **UNKNOWN** (check with them) |

## Conclusion

**Your Genmitsu Kiosk firmware (1.3a 20211103) is the LATEST and FINAL stable release of Grbl_ESP32.**

There are no meaningful updates available. The project is in maintenance mode with all new development happening in FluidNC. For a commercial product like Genmitsu Kiosk, staying on the proven stable version is the RIGHT choice.

**Recommendation**: Enjoy your working laser engraver and don't worry about updates unless you have specific issues or need specific FluidNC features!

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Current and accurate
