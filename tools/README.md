# Reverse Engineering Tools Guide

This document describes the tools and methods used for ESP32 firmware reverse engineering.

## Essential Tools

### 1. esptool.py (ESP32 Flash Tool)

**Purpose**: Official Espressif tool for flashing and analyzing ESP32 firmware

**Installation**:
```bash
pip install esptool
```

**Common Commands**:
```bash
# Read flash memory
esptool.py --port /dev/ttyUSB0 read_flash 0 0x400000 flash_dump.bin

# Get chip info
esptool.py --port /dev/ttyUSB0 chip_id
esptool.py --port /dev/ttyUSB0 flash_id

# Parse image header
esptool.py image_info firmware.bin

# Merge binaries
esptool.py --chip esp32 merge_bin -o merged.bin --flash_mode dio --flash_size 4MB \
  0x1000 bootloader.bin \
  0x8000 partition-table.bin \
  0x10000 app.bin
```

### 2. binwalk (Firmware Analysis)

**Purpose**: Analyze and extract embedded files from firmware

**Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install binwalk

# Or from source
git clone https://github.com/ReFirmLabs/binwalk.git
cd binwalk
sudo python3 setup.py install
```

**Common Commands**:
```bash
# Analyze firmware structure
binwalk firmware.bin

# Extract embedded files
binwalk -e firmware.bin

# Entropy analysis (detect encryption/compression)
binwalk -E firmware.bin

# Search for signatures
binwalk --signature firmware.bin
```

### 3. Ghidra (Decompiler)

**Purpose**: Advanced reverse engineering and decompilation

**Installation**:
1. Download from https://ghidra-sre.org/
2. Extract and run: `./ghidraRun`

**Usage for ESP32**:
1. Create new project
2. Import firmware binary
3. Select processor: **Xtensa** (ESP32 uses Xtensa LX6)
4. Analyze with default options
5. Browse decompiled code

**ESP32 Specific Settings**:
- Language: Xtensa:LE:32:default
- Load address: 0x40000000 (IRAM) or 0x3F400000 (Flash cache)

### 4. radare2 (Binary Analysis)

**Purpose**: Open-source reverse engineering framework

**Installation**:
```bash
git clone https://github.com/radareorg/radare2
cd radare2
sys/install.sh
```

**Common Commands**:
```bash
# Open firmware
r2 firmware.bin

# Analyze
aaa

# List functions
afl

# Disassemble
pdf @ main

# Search for strings
iz

# Search for hex pattern
/x 504b0304
```

### 5. strings (String Extraction)

**Purpose**: Extract printable strings from binaries

**Installation**: Usually pre-installed on Linux

**Common Commands**:
```bash
# Extract all strings
strings firmware.bin > strings.txt

# Minimum length 10
strings -n 10 firmware.bin

# Include file offset
strings -t x firmware.bin

# Search for specific patterns
strings firmware.bin | grep -i wifi
strings firmware.bin | grep -i "http://"
```

### 6. objdump (Disassembler)

**Purpose**: Display information about object files

**Installation**:
```bash
# Install xtensa toolchain for ESP32
# Download from https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/tools/idf-tools.html
```

**Common Commands**:
```bash
# Disassemble (with xtensa toolchain)
xtensa-esp32-elf-objdump -d -m xtensa firmware.elf

# Display headers
xtensa-esp32-elf-objdump -h firmware.elf

# Display symbols
xtensa-esp32-elf-objdump -t firmware.elf
```

## Analysis Workflow

### Phase 1: Initial Analysis
1. **File identification**: `file firmware.bin`
2. **Entropy analysis**: `binwalk -E firmware.bin`
3. **Structure analysis**: `binwalk firmware.bin`
4. **Hash calculation**: `md5sum firmware.bin`

### Phase 2: Partition Analysis
1. **Parse partition table**: `python3 scripts/parse_partitions.py firmware.bin`
2. **Extract partitions**: `python3 scripts/parse_partitions.py firmware.bin --extract`
3. **Analyze each partition** individually

### Phase 3: String Analysis
1. **Extract strings**: `python3 scripts/extract_strings.py firmware.bin`
2. **Search for keywords**: WiFi, SSID, password, API, URL, etc.
3. **Identify configuration**: Look for JSON, XML, or config formats

### Phase 4: Disassembly
1. **Load in Ghidra**: Set processor to Xtensa
2. **Auto-analyze**: Let Ghidra identify functions
3. **Find entry points**: Look for `app_main`, interrupt vectors
4. **Decompile functions**: Focus on interesting areas

### Phase 5: Dynamic Analysis (with hardware)
1. **Connect UART**: Monitor serial output during boot
2. **Flash modified firmware**: Test changes
3. **Monitor WiFi**: Capture network traffic
4. **Debug**: Use JTAG if available

## ESP32 Specific Information

### Memory Map
```
0x40000000 - 0x40400000: Internal ROM (448 KB)
0x3FF00000 - 0x3FF80000: Internal SRAM (512 KB)
0x3F400000 - 0x3F800000: External Flash mapping (4 MB)
0x50000000 - 0x50002000: RTC FAST Memory (8 KB)
```

### Partition Table Structure
- Location: Usually at 0x8000
- Entry size: 32 bytes
- Magic: 0xAA50
- Fields: type, subtype, offset, size, name, flags

### Common Partitions
- **nvs**: Non-volatile storage (settings, WiFi credentials)
- **phy_init**: RF calibration data
- **factory**: Main application
- **ota_0/ota_1**: OTA update partitions
- **spiffs/fatfs**: File system partitions

### Boot Process
1. First-stage bootloader (ROM)
2. Second-stage bootloader (0x1000)
3. Partition table (0x8000)
4. Application (0x10000+)

## Advanced Techniques

### Firmware Modification
```bash
# Extract partition
dd if=firmware.bin of=app.bin bs=1 skip=$((0x10000)) count=$((0x100000))

# Modify and merge back
# (requires careful offset calculation)
```

### Encryption Detection
- Check entropy: High entropy (>7.5) suggests encryption
- Look for crypto libraries: mbedtls, OpenSSL
- Search for keys: AES, RSA patterns

### Hardware Analysis
- Identify UART pins: TX, RX, GND
- Monitor boot logs: Look for debug output
- JTAG debugging: If exposed

## Resources

- [ESP32 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)
- [ESP-IDF Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [Ghidra ESP32 Loader](https://github.com/Ebiroll/ghidra-xtensa)
- [radare2 ESP32 Support](https://github.com/radareorg/radare2-extras)

## Safety Notes

⚠️ **Warning**: 
- Always work on copies of firmware
- Flashing modified firmware can brick devices
- Ensure proper authorization before reverse engineering
- Be aware of legal restrictions in your jurisdiction
