# Reverse Engineering Workflow

This document provides a step-by-step guide for analyzing the Genmitsu Kiosk firmware.

## Prerequisites

Before starting, ensure you have:
- Python 3.7 or higher
- Basic understanding of embedded systems
- Familiarity with command-line tools
- (Optional) Ghidra or radare2 installed

## Step-by-Step Analysis

### Step 1: Initial Setup

1. Clone this repository
2. Place the firmware `.bin` file in the `firmware/` directory
3. Verify Python is installed: `python3 --version`

### Step 2: Run Automated Analysis

Run the complete analysis suite:

```bash
python3 scripts/run_full_analysis.py firmware/your_firmware.bin
```

This will automatically:
- Analyze firmware structure
- Extract strings
- Parse and extract partitions
- Generate reports in `analysis/` directory

### Step 3: Manual Analysis

#### 3.1 Firmware Structure

```bash
# Analyze header and basic structure
python3 scripts/analyze_firmware.py firmware/your_firmware.bin

# Review output for:
# - ESP32 chip type
# - Flash configuration
# - Entry points
# - Segment information
```

#### 3.2 String Extraction

```bash
# Extract and categorize strings
python3 scripts/extract_strings.py firmware/your_firmware.bin

# Review analysis/your_firmware_strings.txt for:
# - WiFi credentials or SSIDs
# - API endpoints or URLs
# - Version information
# - Debug messages
# - Error messages
# - Configuration parameters
```

**Key things to look for**:
- `ssid`, `password`, `wifi` → Network configuration
- `http://`, `https://` → Web services
- `mqtt://` → MQTT broker
- Version strings → Firmware version
- GPIO pins → Hardware configuration
- Laser-related strings → Control parameters

#### 3.3 Partition Analysis

```bash
# Parse partition table
python3 scripts/parse_partitions.py firmware/your_firmware.bin --extract

# This extracts partitions to analysis/partitions/
# Common partitions:
# - nvs.bin → Settings and WiFi credentials
# - factory.bin → Main application
# - ota_0.bin / ota_1.bin → OTA partitions
# - spiffs.bin / fat.bin → File systems
```

### Step 4: Deep Analysis with External Tools

#### 4.1 Using Ghidra

1. **Launch Ghidra**:
   ```bash
   ghidraRun
   ```

2. **Create New Project**:
   - File → New Project
   - Name: "GenmitsuKiosk"

3. **Import Firmware**:
   - File → Import File
   - Select `analysis/partitions/factory.bin`
   - Language: **Xtensa:LE:32:default**
   - Load Address: `0x3F400000` (Flash mapping)

4. **Analyze**:
   - Analysis → Auto Analyze
   - Wait for analysis to complete
   - Browse functions in Symbol Tree

5. **Find Key Functions**:
   - Search for strings (WiFi, laser, etc.)
   - Follow references to find related code
   - Look for `app_main` function
   - Examine interrupt handlers

#### 4.2 Using binwalk

```bash
# Analyze firmware structure
binwalk firmware/your_firmware.bin

# Extract embedded files
binwalk -e firmware/your_firmware.bin

# Entropy analysis (detect encryption)
binwalk -E firmware/your_firmware.bin
```

#### 4.3 Using strings utility

```bash
# Extract all strings
strings firmware/your_firmware.bin > all_strings.txt

# Search for specific patterns
strings firmware/your_firmware.bin | grep -i "wifi"
strings firmware/your_firmware.bin | grep -i "laser"
strings firmware/your_firmware.bin | grep -E "v[0-9]+\.[0-9]+"
```

### Step 5: Analyze NVS Partition

The NVS (Non-Volatile Storage) partition contains settings:

```bash
# If NVS partition was extracted
# Look for configuration data
hexdump -C analysis/partitions/nvs.bin | less

# Search for WiFi credentials (usually stored here)
strings analysis/partitions/nvs.bin | grep -i ssid
```

### Step 6: Document Findings

Update `docs/FINDINGS.md` with:

1. **Firmware metadata**: Hash, size, date
2. **Partition table**: Document all partitions
3. **String analysis**: Categorize interesting strings
4. **Function list**: Major components identified
5. **Security notes**: Encryption status, vulnerabilities
6. **Communication**: Protocols, endpoints
7. **Hardware config**: GPIO pins, interfaces

Template sections are already in `docs/FINDINGS.md`.

### Step 7: Advanced Analysis (Optional)

#### Static Analysis
- **Decompile functions** in Ghidra
- **Cross-reference analysis**: Find where functions are called
- **Data structure recovery**: Identify structs and classes
- **Control flow analysis**: Understand program logic

#### Dynamic Analysis (Requires Hardware)
- **UART monitoring**: Connect to serial port
- **Network capture**: Monitor WiFi traffic with Wireshark
- **Firmware modification**: Patch and reflash (CAUTION!)
- **JTAG debugging**: If JTAG is exposed

### Step 8: Create Documentation

Generate comprehensive documentation:

1. **Architecture diagram**: System components
2. **Memory map**: Flash layout
3. **Function call graph**: Major interactions
4. **Protocol documentation**: Communication formats
5. **Configuration guide**: Modifiable parameters

## Analysis Checklist

Use this checklist to track progress:

- [ ] Firmware file obtained and hashed
- [ ] Basic analysis completed (structure, strings, partitions)
- [ ] Partition table documented
- [ ] All partitions extracted
- [ ] Strings categorized and documented
- [ ] Main application loaded in Ghidra
- [ ] Key functions identified
- [ ] Entry point (`app_main`) found
- [ ] WiFi configuration analyzed
- [ ] Laser control mechanism understood
- [ ] Communication protocols documented
- [ ] Security features assessed
- [ ] Findings documented in FINDINGS.md
- [ ] (Optional) Hardware testing completed
- [ ] (Optional) Modified firmware tested

## Common Patterns to Look For

### WiFi Configuration
```c
// Look for these patterns in decompiled code
wifi_config_t wifi_config = {
    .sta = {
        .ssid = "...",
        .password = "...",
    },
};
```

### MQTT Configuration
```c
// MQTT broker settings
esp_mqtt_client_config_t mqtt_cfg = {
    .uri = "mqtt://...",
    .username = "...",
    .password = "...",
};
```

### Laser Control
```c
// PWM configuration for laser
ledc_channel_config_t ledc_channel = {
    .channel    = LEDC_CHANNEL_0,
    .duty       = 0,        // Laser power
    .gpio_num   = GPIO_NUM_X,
    .speed_mode = LEDC_HIGH_SPEED_MODE,
};
```

## Troubleshooting

### Script Errors
- Ensure Python 3.7+ is installed
- Check file paths are correct
- Verify firmware file is accessible

### Ghidra Issues
- Install correct Xtensa extension for ESP32
- Try different load addresses if analysis fails
- Manually define functions if auto-analysis misses them

### Missing Information
- Some data may be encrypted
- Certain partitions may be empty or unused
- Check for compression (LZMA, gzip)

## Safety Warnings

⚠️ **IMPORTANT**:
- Always work on copies of firmware
- Never flash untested firmware to device
- Laser safety: Understand power controls before modification
- Legal: Ensure you have authorization to reverse engineer
- Backup: Keep original firmware safe

## Next Steps After Analysis

Once analysis is complete:
1. Document all findings thoroughly
2. Create issue reports for vulnerabilities
3. Consider custom firmware possibilities
4. Share findings (if permitted)
5. Contribute improvements to this repo

## Resources

- See `tools/README.md` for detailed tool documentation
- See `docs/FINDINGS.md` template for documentation
- ESP32 documentation: https://docs.espressif.com/
- Ghidra: https://ghidra-sre.org/
