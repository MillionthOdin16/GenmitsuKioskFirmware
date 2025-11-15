# Analysis Summary - Genmitsu Kiosk Firmware

## Executive Summary

This document provides a high-level summary of the reverse engineering analysis performed on the Genmitsu Kiosk 2.5W laser engraver firmware.

### Firmware Identification

- **File**: Kiosk Firmware (C07-251021).bin
- **Size**: 1.24 MB (1,303,728 bytes)
- **MD5**: 073206d72007eb0360e9c6330c7f0aab
- **Platform**: ESP32 microcontroller
- **Base Firmware**: Grbl_ESP32 (open-source CNC/laser controller)
- **SDK**: ESP-IDF v3.2.3

### Architecture Overview

```
ESP32 Firmware Architecture
├── Bootloader (0x1000) - Not included in image
├── Partition Table (0x8000)
├── NVS Storage (0x9000) - WiFi, settings
├── OTA Data (0xE000) - Active app selector
├── App0 (0x10000) - Main firmware [ACTIVE]
│   ├── Grbl_ESP32 Core
│   ├── WiFi Manager (STA + AP modes)
│   ├── HTTP Server + WebSocket
│   ├── SSDP/UPnP Discovery
│   ├── mDNS (.local hostname)
│   ├── I2S Stepper Driver
│   ├── PWM Laser Control
│   └── Settings Manager
├── App1 (0x1F0000) - OTA backup [EMPTY]
└── SPIFFS (0x3D0000) - Web files [EMPTY]
```

### Key Features

1. **Wireless Control**
   - WiFi AP mode (default SSID: `Genmitsu_Kiosk_C_V07`)
   - WiFi Station mode (connect to existing network)
   - Default AP IP: 192.168.0.1
   - Web-based control interface
   - WebSocket for real-time G-code streaming

2. **Laser Control**
   - PWM-based variable power control
   - Configurable frequency and resolution
   - Laser mode for dynamic power (M4 command)
   - Safety validation and limits
   - Min/Max/Off power settings

3. **Motion Control**
   - Full GRBL G-code support
   - I2S-based stepper control (high precision)
   - Configurable acceleration and jerk
   - Soft limits and homing
   - Multi-axis support

4. **Network Features**
   - HTTP web server
   - WebSocket real-time communication
   - SSDP/UPnP device discovery
   - mDNS (.local hostname resolution)
   - OTA firmware updates

### Security Assessment

#### Strengths
- Open-source base (Grbl_ESP32) - community reviewed
- Modular architecture
- Standard ESP32 security features available

#### Weaknesses
- ⚠️ No flash encryption enabled
- ⚠️ No secure boot enabled
- ⚠️ Firmware is completely readable
- ⚠️ WiFi credentials stored in plaintext (NVS)
- ⚠️ Web interface may lack authentication by default
- ⚠️ HTTP (not HTTPS) for web interface

#### Recommendations
1. Enable flash encryption for production
2. Implement secure boot
3. Add web interface authentication
4. Use HTTPS/WSS instead of HTTP/WS
5. Encrypt WiFi credentials in NVS
6. Regular firmware updates for security patches

### Customization Opportunities

The firmware can be easily customized due to its open-source base:

1. **Enhanced Features**
   - Camera integration for job monitoring
   - Advanced material profiles
   - Cloud connectivity
   - Multi-language support
   - Job queue management

2. **Safety Improvements**
   - Additional interlock switches
   - Power monitoring
   - Fume detection integration
   - Automatic shutdown timers

3. **Performance Enhancements**
   - Optimized motion planning
   - Custom acceleration profiles
   - Advanced laser power algorithms
   - Improved web interface

### Technical Details

#### G-Code Support
Standard GRBL commands supported:
- G0/G1 (linear motion)
- G2/G3 (arc motion)
- M3/M4/M5 (laser control)
- $ commands (settings)
- Real-time commands (?, !, ~, etc.)

#### Communication
- **Serial**: UART for direct G-code input (likely 115200 baud)
- **WiFi**: 2.4GHz 802.11 b/g/n
- **HTTP**: Web interface and file upload
- **WebSocket**: Real-time bidirectional communication

#### Hardware Interfaces
- **GPIO**: Laser PWM, enable pins, limit switches
- **I2S**: High-speed stepper motor control
- **UART**: Serial communication
- **SPI**: Flash memory access
- **DAC**: Optional spindle control (GPIO 25/26)

### Development Resources

- **Source Code**: https://github.com/bdring/Grbl_Esp32
- **Documentation**: Grbl_ESP32 Wiki
- **Community**: Active Discord and GitHub discussions
- **Tools**: ESP-IDF, Arduino IDE, PlatformIO

### Risk Analysis

#### Physical Safety Risks
- Laser can cause eye damage or fire
- Improper modifications could disable safety features
- Test all changes at low power first

#### Cybersecurity Risks
- Unencrypted firmware can be modified by attackers
- Network services exposed without authentication
- WiFi credentials extractable from flash dump

#### Operational Risks
- Firmware updates could brick device if interrupted
- Incorrect settings could damage mechanics
- Motion planning changes could cause collisions

### Conclusion

The Genmitsu Kiosk firmware is based on the well-established Grbl_ESP32 platform, providing a solid foundation for laser engraving operations. The firmware is feature-rich with WiFi connectivity and web-based control, but lacks encryption and some modern security features.

The open-source nature of the base platform makes customization straightforward for developers familiar with ESP32 and embedded systems. However, any modifications should be thoroughly tested, especially those affecting laser power control or motion safety.

For detailed technical findings, refer to `docs/FINDINGS.md`.

---

**Analysis Date**: November 15, 2025  
**Analysis Method**: Static analysis, string extraction, partition parsing  
**Tools Used**: Custom Python scripts, hexdump, binary analysis  
**Confidence Level**: High (based on extensive string analysis and known Grbl_ESP32 architecture)
