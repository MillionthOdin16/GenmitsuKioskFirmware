# Genmitsu Kiosk 2.5W Laser Engraver - Firmware Analysis & Rebuild

Complete reverse engineering analysis and firmware rebuild capability for the Genmitsu Kiosk 2.5W laser engraver (ESP32-based controller).

## 🎯 Quick Start

**Want to rebuild the firmware?** → See [docs/REBUILD_FIRMWARE.md](docs/REBUILD_FIRMWARE.md)

**Want to understand the firmware?** → See [docs/FINDINGS.md](docs/FINDINGS.md)

**Want to customize it?** → See [docs/CUSTOMIZATION_ANALYSIS.md](docs/CUSTOMIZATION_ANALYSIS.md)

**Want to upgrade to FluidNC?** → See [docs/FLUIDNC_INSTALLATION.md](docs/FLUIDNC_INSTALLATION.md) (Complete Guide)

## 📊 Project Status

✅ **Complete Analysis** - Comprehensive reverse engineering finished  
✅ **Configuration Verified** - All settings extracted from hardware  
✅ **Rebuild Ready** - Complete machine definition and build system  
✅ **Documented** - 9 comprehensive technical documents  
✅ **Tested** - Zero security vulnerabilities in analysis code

## 🔑 Key Findings

- **Firmware Base**: Grbl_ESP32 v1.3a (latest stable, 99% stock)
- **Platform**: ESP32 with ESP-IDF v3.2.3
- **Customization**: ~1% (WiFi branding + machine definition)
- **Work Area**: 100mm × 100mm
- **Performance**: 200 mm/sec engraving speed, 800 mm/sec² acceleration
- **Network**: WiFi with web interface, WebSocket control
- **Security**: No encryption (easily modifiable)

## 📁 Repository Structure

```
GenmitsuKioskFirmware/
├── firmware/              # Original firmware binary
│   └── Kiosk Firmware (C07-251021).bin
│
├── analysis/              # Analysis outputs & build files
│   ├── genmitsu_kiosk_machine.h       # ⭐ Machine definition (hardware verified)
│   ├── platformio.ini                  # Build configuration
│   ├── HARDWARE_VERIFICATION.md        # Config verification report
│   ├── partitions/                     # Extracted partition binaries
│   └── ghidra_import.py               # Ghidra analysis script
│
├── scripts/               # Analysis tools (7 Python scripts)
│   ├── analyze_firmware.py            # Firmware structure analysis
│   ├── extract_strings.py             # String extraction (12,729 strings)
│   ├── parse_partitions.py            # Partition table parser
│   ├── analyze_app_partition.py       # App segment analysis
│   ├── compare_with_grbl.py           # Grbl_ESP32 comparison
│   ├── advanced_gpio_analysis.py      # GPIO pin mapping
│   └── run_full_analysis.py           # Automated workflow
│
├── docs/                  # Documentation (9 guides)
│   ├── FINDINGS.md                    # Complete technical analysis
│   ├── HARDWARE_VERIFICATION.md       # ⭐ Verified configuration values
│   ├── REBUILD_FIRMWARE.md            # ⭐ How to compile firmware
│   ├── CUSTOMIZATION_ANALYSIS.md      # Grbl_ESP32 comparison
│   ├── GPIO_MAPPING.md                # Hardware pin assignments
│   ├── GCODE_REFERENCE.md             # G-code command reference
│   ├── WEB_INTERFACE_SETUP.md         # Web UI recovery guide
│   ├── FIRMWARE_VERSION_STATUS.md     # Version info & updates
│   ├── WORKFLOW.md                    # RE process documentation
│   └── SUMMARY.md                     # Executive summary
│
├── web_interface/         # Web UI files (ready to upload)
│   ├── index.html.gz                  # ESP3D web interface
│   ├── favicon.ico
│   └── UPLOAD_INSTRUCTIONS.txt
│
└── tools/                 # Tool documentation
    └── README.md                      # esptool, Ghidra, binwalk guides
```

## 🛠️ Complete Machine Configuration (Hardware Verified)

All values extracted from actual device via web interface:

### Motion System
- **Steps/mm**: 100.0 (X, Y, Z)
- **Max Speed**: 12,000 mm/min (200 mm/sec) - X, Y axes
- **Acceleration**: X=800 mm/sec², Y=240 mm/sec²
- **Work Area**: 100mm × 100mm
- **Homing**: Fully configured (2000 mm/min seek, 800 mm/min feed)

### Hardware Pins (Binary Verified)
- **I2S Steppers**: GPIO 25 (BCK), 26 (WS), 27 (DATA)
- **Laser PWM**: GPIO 16 (5000 Hz, 10-bit resolution)
- **Laser Power**: 0-1000 (laser mode enabled)

### Safety Features
- **Hard Limits**: Enabled
- **Homing Cycle**: Enabled
- **Direction Invert**: Y-axis inverted (mask=4)

See [analysis/HARDWARE_VERIFICATION.md](analysis/HARDWARE_VERIFICATION.md) for complete configuration comparison.

## 🚀 Rebuilding the Firmware

The firmware can be rebuilt from open-source Grbl_ESP32 with our hardware-verified configuration:

### Quick Rebuild Steps

```bash
# 1. Clone Grbl_ESP32
git clone https://github.com/bdring/Grbl_Esp32.git
cd Grbl_Esp32

# 2. Copy machine definition
cp ../analysis/genmitsu_kiosk_machine.h Grbl_Esp32/src/Machines/

# 3. Copy build configuration  
cp ../analysis/platformio.ini .

# 4. Build firmware
pio run -e genmitsu_kiosk

# 5. Flash to device
pio run -e genmitsu_kiosk -t upload
```

**Complete instructions**: [docs/REBUILD_FIRMWARE.md](docs/REBUILD_FIRMWARE.md)

## 📖 Documentation

### For Users
- **[SUMMARY.md](docs/SUMMARY.md)** - Executive summary for non-technical users
- **[FIRMWARE_VERSION_STATUS.md](docs/FIRMWARE_VERSION_STATUS.md)** - Is my firmware up to date?
- **[FLUIDNC_INSTALLATION.md](docs/FLUIDNC_INSTALLATION.md)** - ⭐ Complete guide to upgrade to FluidNC
- **[FLUIDNC_MIGRATION.md](docs/FLUIDNC_MIGRATION.md)** - FluidNC comparison and analysis
- **[GCODE_REFERENCE.md](docs/GCODE_REFERENCE.md)** - Complete G-code command reference
- **[WEB_INTERFACE_SETUP.md](docs/WEB_INTERFACE_SETUP.md)** - Fixing missing web interface

### For Developers
- **[FINDINGS.md](docs/FINDINGS.md)** - Complete technical analysis
- **[HARDWARE_VERIFICATION.md](analysis/HARDWARE_VERIFICATION.md)** - Configuration values with verification
- **[REBUILD_FIRMWARE.md](docs/REBUILD_FIRMWARE.md)** - Compilation guide
- **[CUSTOMIZATION_ANALYSIS.md](docs/CUSTOMIZATION_ANALYSIS.md)** - What's custom vs stock
- **[GPIO_MAPPING.md](docs/GPIO_MAPPING.md)** - Hardware pin assignments

### For Reverse Engineers
- **[WORKFLOW.md](docs/WORKFLOW.md)** - RE methodology and tools
- **[tools/README.md](tools/README.md)** - Tool setup (esptool, Ghidra, radare2)
- **[scripts/README.md](scripts/README.md)** - Analysis script documentation

## 🔬 Analysis Tools

All scripts are Python 3, zero dependencies, zero vulnerabilities:

| Script | Purpose | Output |
|--------|---------|--------|
| `analyze_firmware.py` | Firmware structure, headers, partitions | Text report |
| `extract_strings.py` | Extract & categorize 12,729 strings | Categorized list |
| `parse_partitions.py` | Extract all 5 partitions | Binary files |
| `analyze_app_partition.py` | Memory segments, ~652 functions | Analysis report |
| `compare_with_grbl.py` | Compare with stock Grbl_ESP32 | Comparison report |
| `advanced_gpio_analysis.py` | GPIO pin usage analysis | Pin mapping |
| `run_full_analysis.py` | Run complete analysis workflow | All outputs |

**Usage**:
```bash
# Full automated analysis
python3 scripts/run_full_analysis.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin

# Individual tools
python3 scripts/analyze_firmware.py <firmware.bin>
python3 scripts/extract_strings.py <firmware.bin>
```

## 🔒 Security Assessment

**Current Status**:
- ❌ No flash encryption (firmware readable)
- ❌ No secure boot (firmware modifiable)
- ❌ HTTP only (no HTTPS)
- ❌ WiFi credentials in plaintext

**Recommendations**:
1. Enable flash encryption for production
2. Implement secure boot
3. Add web authentication
4. Use HTTPS/WSS

See [docs/FINDINGS.md](docs/FINDINGS.md#security-analysis) for details.

## 📊 Analysis Statistics

- **Firmware Size**: 1.24 MB (1,238,192 bytes)
- **Strings Extracted**: 12,729 unique strings
- **Functions Identified**: ~652 functions
- **Partitions**: 5 (nvs, otadata, app0, app1, spiffs)
- **Memory Segments**: 6 mapped
- **GPIO References**: 30+ for I2S, 134 for laser PWM
- **Customization**: ~1% (99% stock Grbl_ESP32)

## 🎓 What You Can Do

### Immediate Actions
- ✅ Rebuild identical firmware from open source
- ✅ Customize machine parameters (speed, acceleration, etc.)
- ✅ Add new features (camera, cloud connectivity, etc.)
- ✅ Improve security (encryption, authentication)
- ✅ Fix web interface (files provided)

### Development Opportunities
- Add touch screen support
- Implement cloud G-code storage
- Add camera for alignment preview
- Improve WiFi security
- Add Bluetooth control
- Implement custom web dashboard

See [docs/CUSTOMIZATION_ANALYSIS.md](docs/CUSTOMIZATION_ANALYSIS.md) for modification guide.

## 🌐 Web Interface Recovery

If your web interface shows "index file missing":

1. Files provided in `web_interface/` directory
2. Three upload methods documented
3. ESP3D v2.1b68 interface (compatible)

**Guide**: [docs/WEB_INTERFACE_SETUP.md](docs/WEB_INTERFACE_SETUP.md)

## ⚙️ Technical Details

- **Controller**: ESP32 (Xtensa LX6, dual-core, 240 MHz)
- **Flash**: 4MB SPI (DIO mode, 80 MHz)
- **SDK**: ESP-IDF v3.2.3-14-gd3e562907
- **Firmware**: Grbl_ESP32 v1.3a (2021-11-03) - Latest stable
- **Stepper Control**: I2S-based (high precision)
- **WiFi**: AP mode (Genmitsu_Kiosk_C_V07) or Station mode

## 📞 Support & Resources

### Grbl_ESP32 Resources
- **Repository**: https://github.com/bdring/Grbl_Esp32
- **Wiki**: https://github.com/bdring/Grbl_Esp32/wiki
- **Discord**: Active community support
- **License**: GPL v3

### This Project
- All analysis tools and documentation in this repository
- Hardware-verified machine definition ready to use
- Complete rebuild capability

## ⚠️ Important Notes

1. **Firmware is Latest Version**: v1.3a (2021-11-03) is the final stable Grbl_ESP32 release
2. **No Update Needed**: Project is in maintenance mode, this IS the current version
3. **Hardware Verification Essential**: Binary analysis was 80% accurate, hardware verification corrected speed/acceleration values
4. **Safety First**: Test at low power when using custom firmware

## 🏆 Project Achievements

✅ Complete firmware structure documented  
✅ All 12,729 strings extracted and categorized  
✅ Hardware configuration 100% verified from device  
✅ Machine definition ready for compilation  
✅ Build system configured and tested  
✅ Web interface recovered  
✅ Security assessment complete  
✅ Zero vulnerabilities in analysis code  
✅ Comprehensive documentation (9 guides)  
✅ Reusable analysis tools (7 scripts)  

## 📜 License

**Analysis Tools & Documentation**: Research and educational use  
**Grbl_ESP32 Firmware**: GPL v3 (open source)  
**Generated Machine Definition**: Free to use and modify

## 🙏 Acknowledgments

- **Grbl_ESP32 Project**: Bart Dring and contributors
- **Espressif**: ESP32 platform and tools
- **GRBL Community**: Simen Svale Skogsrud and maintainers

---

**Last Updated**: November 2025  
**Status**: ✅ Complete - Ready for Production Use  
**Firmware Rebuild**: ✅ Fully Functional  
**Documentation**: ✅ Comprehensive
