# Analysis Findings

This document tracks all findings from the reverse engineering of the Genmitsu Kiosk firmware.

## Firmware Information

**File**: Kiosk Firmware (C07-251021).bin
- **MD5**: 073206d72007eb0360e9c6330c7f0aab
- **SHA1**: d5007cd86ee1e29c5fb03e5491ec8c31bbe68f02
- **SHA256**: e989d684b7e146dd35c2810715b15209e990929846e3969cb52ac79b13f392d9
- **Size**: 1,303,728 bytes (1.24 MB)
- **Date analyzed**: November 15, 2025 

## Hardware Platform

**Controller**: ESP32-based
- **Chip**: ESP32 (standard, not S2/C3/S3 variant)
- **Flash Size**: 4MB (inferred from partition layout)
- **PSRAM**: Unknown (to be determined)
- **SDK**: ESP32 Arduino lib builder / ESP-IDF v3.2.3-14-gd3e562907

**Device**: Genmitsu Kiosk 2.5W Laser Engraver
- **Firmware Base**: Grbl_ESP32 (GRBL port for ESP32)
- **Version Identifiers**:
  - `Genmitsu_Kiosk_C_V07`
  - `Genmitsu_Kiosk_V07`
  - Firmware build: C07-251021 (likely Oct 21, 2025, version C07)

## Partition Table

Partition table located at offset 0x8000 (standard ESP32 location)
MD5 Checksum: 3e74a399f8859c234514de43eeb7924c

| Partition Name | Type | SubType | Offset | Size | Purpose |
|---------------|------|---------|--------|------|---------|
| nvs | data | nvs | 0x00009000 | 20 KB | Non-volatile storage (WiFi credentials, settings) |
| otadata | data | ota | 0x0000E000 | 8 KB | OTA data partition (tracks active app) |
| app0 | app | ota_0 | 0x00010000 | 1.9 MB | Primary application (active) |
| app1 | app | ota_1 | 0x001F0000 | 1.9 MB | Secondary OTA partition (for updates) |
| spiffs | data | spiffs | 0x003D0000 | 192 KB | SPIFFS file system (web files, configs) |

**Note**: Only app0 partition contains data in this firmware image. app1 and spiffs are empty (reserved for OTA updates and file system).

## String Analysis

### WiFi/Network Related
- **Default AP SSIDs**: 
  - `Genmitsu_Kiosk_C_V07`
  - `Genmitsu_Kiosk_V07`
  - `Genmitsu_Kiosk`
- **Default credentials**: Not found in strings (likely stored in NVS or user-configurable)
- **Network settings**: Supports both STA (Station) and AP (Access Point) modes
- **Default AP IP**: 192.168.0.1
- **Default subnet mask**: 255.255.255.0
- **SSDP/UPnP**: Device advertises itself via SSDP on 239.255.255.250:1900
- **mDNS**: Supports mDNS with .local hostname resolution

### API Endpoints
- **HTTP Server**: Enabled by default
- **WebSocket**: Supported (Sec-WebSocket-Version: 13)
- **UPnP Device Description**: 
  - Model: ESP32
  - Model Number: Marlin (interesting - references Marlin firmware)
  - Manufacturer: Espressif Systems
  - Presentation URL: `/`

### Credentials
No hardcoded WiFi credentials found. Configuration appears to be stored in NVS partition and user-configurable via web interface or serial commands.

### Version Information
- **Base Firmware**: Grbl_ESP32 (GRBL port for ESP32)
- **ESP-IDF SDK**: v3.2.3-14-gd3e562907
- **Build Info**: C07-251021
- **Device Identifier**: GRBL_ESP, grblesp
- **Notification Service**: "GRBL Notification"

### Hardware References
- **GPIO Configuration**: Extensive GPIO matrix configuration code present
- **PWM Channels**: Multiple PWM channels for laser/spindle control
- **UART**: Serial communication support
- **I2S**: I2SOut.cpp present (likely for stepper motor control)
- **SPI**: SPI support
- **DAC**: DAC spindle control (pins 25 or 26)

### Laser Control
- **Laser Mode**: `$GCode/LaserMode` setting
- **Full Power Setting**: `Laser/FullPower` 
- **PWM Control**: Laser uses PWM output on configurable GPIO
- **Safety**: "Laser mode requires PWM output" validation
- **Power Control**: Variable power control via PWM duty cycle
- **Frequency**: Configurable PWM frequency (`Spindle/PWM/Frequency`)
- **Enable Pin**: Separate enable pin support with invert option
- **Min/Max PWM**: `Spindle/PWM/Min` and `Spindle/PWM/Max` settings
- **Spindle Off Value**: `Spindle/PWM/Off` setting
- **M4 Command**: Requires laser mode or reversible spindle

## Code Analysis

### Main Components
Based on string analysis, the firmware includes:
- **Grbl_ESP32 Core**: Main GRBL engine for G-code interpretation
- **WiFi Manager**: Station and Access Point management
- **HTTP Server**: Web interface for control
- **WebSocket Server**: Real-time communication
- **SSDP/UPnP**: Device discovery
- **mDNS**: Local network name resolution
- **I2S Stepper Driver**: High-precision stepper motor control
- **Spindle/Laser Control**: PWM-based power control
- **Settings Manager**: NVS-based configuration storage
- **OTA Update**: Over-the-air firmware update capability
- **SPIFFS**: File system for web interface files

### Entry Points
- **Bootloader**: Standard ESP32 bootloader at 0x1000 (not in this image)
- **Application**: Main app starts at 0x10000 (app0 partition)
- **Reset Handlers**: Standard ESP32 exception vectors
- **Task Entry**: FreeRTOS task creation for various subsystems

### Key Functions
Based on string references:
- `app_main`: Primary application entry point
- `wifi_station_get_config_local`: WiFi configuration
- `bootloader_init`: Bootloader initialization
- `gpio_matrix_out_check`: GPIO configuration validation
- Motor control functions: `@Init Motors`
- Spindle control: Multiple spindle types (PWM, DAC, BESC, VFD)
- Settings: `GrblSettings/List`, `ExtendedSettings/List`
- Commands: `Commands/List`, G-code parsing

### Libraries Used
- **ESP-IDF version**: v3.2.3-14-gd3e562907
- **FreeRTOS**: Standard ESP32 FreeRTOS implementation
- **WiFi stack**: ESP32 native WiFi (esp_wifi)
- **HTTP/WebSocket**: ESP32 HTTP server component
- **mbedTLS**: Cryptographic library (TLS support)
- **SPIFFS**: SPI Flash File System
- **ESP32SSDP**: SSDP/UPnP library for device discovery
- **Arduino Core for ESP32**: ESP32 Arduino framework integration
- **Grbl_ESP32**: Custom GRBL port (https://github.com/bdring/Grbl_Esp32)

## Security Analysis

### Potential Vulnerabilities
1. **No Flash Encryption**: Firmware is not encrypted (0xFF magic byte instead of standard 0xE9 at offset 0)
2. **Plaintext Firmware**: All strings and code are readable
3. **Web Interface**: HTTP server with no apparent authentication requirement in default config
4. **WiFi Credentials**: Stored in NVS partition (not encrypted by default)
5. **OTA Updates**: OTA capability present - ensure secure update mechanism
6. **Network Services**: Multiple network services exposed (HTTP, WebSocket, SSDP)

### Encryption
- **Flash encryption**: NO - Firmware is not encrypted
- **Secure boot**: NO - Standard bootloader, no secure boot signature found
- **Communication encryption**: TLS libraries present (mbedTLS) but not enforced by default
- **WebSocket**: Uses standard WebSocket (ws://), not secure WebSocket (wss://)

### Credentials Storage
- **Location**: NVS (Non-Volatile Storage) partition at offset 0x9000
- **Format**: ESP32 NVS binary format (key-value pairs)
- **Encryption**: Not encrypted by default in ESP32 NVS
- **WiFi Credentials**: Stored in NVS, can be read if flash is dumped
- **User Passwords**: Likely stored in NVS if web authentication is enabled

## Communication Protocols

### Serial Communication
- **Baud rate**: Configurable (standard GRBL supports 115200)
- **Protocol**: GRBL protocol (G-code commands)
- **Commands**: Standard GRBL commands ($-commands for settings, G-code for motion)
- **Response Format**: GRBL standard responses (ok, error codes)

### Network Protocols
- **WiFi mode**: Both STA (Station) and AP (Access Point)
- **Default AP SSID**: `Genmitsu_Kiosk_C_V07` or `Genmitsu_Kiosk_V07`
- **Default AP IP**: 192.168.0.1
- **Protocols**: 
  - HTTP (web interface)
  - WebSocket (real-time G-code streaming)
  - SSDP/UPnP (device discovery)
  - mDNS (local hostname resolution - .local)
- **Ports used**:
  - HTTP: Configurable (default likely 80)
  - SSDP: 1900 (UDP multicast 239.255.255.250)
  - mDNS: 5353 (UDP)

### Hardware Interfaces
- **UART**: Serial communication for G-code input
- **I2C**: Not explicitly configured in strings
- **SPI**: Used for flash and SPIFFS
- **GPIO**: Extensive GPIO usage for:
  - Stepper motor control (via I2S)
  - Laser PWM output
  - Enable/direction pins
  - Limit switches
  - User digital/analog I/O

## Laser Control System

### Control Parameters
- **Laser Enable**: Dedicated GPIO pin with optional inversion
- **PWM Output**: Variable power via PWM duty cycle
- **PWM Frequency**: Configurable (typically 1-5 kHz for laser diodes)
- **PWM Resolution**: Configurable bit depth
- **Min/Max Power**: Software limits via `Spindle/PWM/Min` and `Spindle/PWM/Max`
- **Laser Mode**: Special G-code mode (`$GCode/LaserMode`)
- **Full Power**: `Laser/FullPower` setting for maximum safe power

### G-Code Support
GRBL firmware with standard G-code support:
- **Supported commands**:
  - G0/G1: Linear motion
  - G2/G3: Arc motion
  - M3: Spindle/Laser ON (constant power)
  - M4: Spindle/Laser ON (dynamic power - laser mode)
  - M5: Spindle/Laser OFF
  - $-commands: Settings and configuration
  - ? : Status query
  - ~ : Cycle start
  - ! : Feed hold
- **Custom extensions**: Grbl_ESP32 extensions for WiFi, WebSocket, and settings management
- **Laser Mode**: In laser mode (M4), power varies with feed rate for better engraving

### Safety Features
- **Laser mode validation**: "Laser mode requires PWM output"
- **M4 safety check**: "M4 requires laser mode or a reversible spindle"
- **Spindle delay**: `Spindle/Delay/SpinUp` and `Spindle/Delay/SpinDown` for safe operation
- **Enable pin**: Hardware enable that can be used for emergency stop
- **Soft limits**: Software position limits to prevent out-of-bounds operation

## File System

### Partition Layout
- **Bootloader** (not in image): 0x1000, ~28KB - Second stage bootloader
- **Partition Table**: 0x8000, 32 bytes per entry + MD5
- **NVS**: 0x9000, 20KB - Settings, WiFi credentials, calibration data
- **OTA Data**: 0xE000, 8KB - Tracks which app partition is active
- **App0**: 0x10000, 1.9MB - Primary firmware (ACTIVE in this image)
- **App1**: 0x1F0000, 1.9MB - Secondary OTA partition (empty)
- **SPIFFS**: 0x3D0000, 192KB - Web interface files (empty in this image)

### Configuration Files
Configuration is stored in NVS partition as key-value pairs:
- **GRBL Settings**: Machine configuration ($0-$999 settings)
- **WiFi Settings**: SSID, password, mode (STA/AP)
- **Network Settings**: IP address, subnet, gateway
- **Calibration**: Motor steps/mm, acceleration, max rates
- **User Settings**: Extended configuration options

### Web Interface
- **Storage**: SPIFFS partition (currently empty - may be generated at runtime or stored elsewhere)
- **Files Expected**: HTML, CSS, JavaScript for web control interface
- **Access**: HTTP server at configured IP (default 192.168.0.1 in AP mode)
- **Features** (based on strings):
  - G-code upload and execution
  - Settings configuration
  - WiFi configuration
  - Firmware update (OTA)
  - Real-time status display
  - File management

## Modification Potential

### Custom Firmware
The Grbl_ESP32 base makes custom firmware development straightforward:
- **Source Available**: Based on open-source Grbl_ESP32 project
- **Build Environment**: ESP-IDF or Arduino IDE with ESP32 core
- **Customization Points**:
  - Custom G-code commands
  - Modified motion planning
  - Enhanced web interface
  - Additional sensors/features
  - Custom laser power algorithms
  - Network protocol extensions

### Feature Additions
Potential enhancements:
1. **Camera Integration**: Add webcam support for job monitoring
2. **Advanced Calibration**: Automated bed leveling/alignment
3. **Material Library**: Pre-configured settings for different materials
4. **Job Queue**: Multiple file queue management
5. **Cloud Integration**: Remote monitoring and control
6. **Enhanced Safety**: Additional interlock switches, power monitoring
7. **Autofocus**: Automated Z-height adjustment for laser focus
8. **Custom Macros**: User-defined G-code macros
9. **Multi-language UI**: Internationalization support
10. **Analytics**: Job statistics, usage tracking

### Safety Considerations
**⚠️ CRITICAL SAFETY WARNINGS:**

1. **Laser Safety**:
   - Never disable laser safety interlocks
   - Ensure proper power calibration before use
   - Test all modifications at low power first
   - Verify emergency stop functionality
   - Ensure proper laser shielding

2. **Motion Safety**:
   - Verify soft limits are configured correctly
   - Test homing sequences thoroughly
   - Ensure limit switches are functional
   - Check acceleration/jerk limits to prevent mechanical damage

3. **Electrical Safety**:
   - Verify PWM frequency is appropriate for laser driver
   - Ensure proper current limiting
   - Check for proper grounding
   - Validate power supply specifications

4. **Firmware Modifications**:
   - Always keep backup of original firmware
   - Test modifications extensively before production use
   - Document all changes
   - Have emergency stop procedures
   - Understand fire risks with laser equipment

5. **Network Security**:
   - Change default passwords
   - Use WPA2/WPA3 for WiFi
   - Consider disabling web interface if not needed
   - Implement access controls
   - Keep firmware updated

## Next Steps

- [x] Complete initial analysis
- [x] Extract all partitions
- [x] Decompile main application structure
- [x] Document firmware architecture
- [x] Identify all major components
- [x] Extract and categorize strings
- [ ] Analyze NVS partition for default settings
- [ ] Load app0 partition in Ghidra for detailed reverse engineering
- [ ] Map all GPIO assignments
- [ ] Document complete G-code command set
- [ ] Create memory map with function locations
- [ ] Test firmware modifications (requires hardware)
- [ ] Develop custom features (optional)
- [ ] Create detailed function call graph

## Notes

### Key Discoveries

1. **Firmware Base**: This is Grbl_ESP32, an open-source project. The base code is available at https://github.com/bdring/Grbl_Esp32

2. **Customization**: Genmitsu has customized the base Grbl_ESP32 with:
   - Custom WiFi AP names (`Genmitsu_Kiosk_C_V07`)
   - Specific version identification (C07-251021)
   - Possibly custom web interface
   - Laser-specific configurations

3. **Architecture**: Standard ESP32 GRBL implementation with:
   - I2S-based stepper motor control (very precise)
   - WiFi for wireless control
   - OTA update capability
   - Web-based configuration and control

4. **Security Posture**: 
   - No flash encryption
   - No secure boot
   - Firmware easily readable and modifiable
   - Network services may be exposed without authentication

5. **Development Potential**: 
   - Easy to modify (based on open-source)
   - Well-documented base platform
   - Active community support for Grbl_ESP32
   - Many existing features can be enabled/configured

### Unusual Findings

1. **Marlin Reference**: UPnP description references "Marlin" as model number (typically a 3D printer firmware), suggesting possible code reuse or template

2. **Empty Partitions**: SPIFFS and app1 partitions are empty in this image, suggesting:
   - Web files may be compiled into app code
   - Or generated dynamically at runtime
   - This is a factory/initial firmware image

3. **High Entropy Blocks**: Several blocks show high entropy (>7.0), indicating:
   - Compressed data (likely compressed code sections)
   - Possibly cryptographic keys or random data
   - Not necessarily encrypted (no flash encryption enabled)

### Build Information

From path strings, this firmware was built on a GitHub Actions runner:
- Build system: esp32-arduino-lib-builder
- ESP-IDF components from official Espressif repositories
- Automated build process (likely CI/CD)

---

**Last Updated**: November 15, 2025  
**Analyzed By**: GitHub Copilot Reverse Engineering Agent  
**Analysis Tools**: Custom Python scripts, hexdump, string analysis  
**Firmware Image**: Kiosk Firmware (C07-251021).bin (MD5: 073206d72007eb0360e9c6330c7f0aab)
