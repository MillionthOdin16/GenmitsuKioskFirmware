# Analysis Scripts

This directory contains Python scripts for analyzing ESP32 firmware binaries.

## Scripts Overview

### 1. analyze_firmware.py
**Purpose**: Comprehensive firmware analysis tool

**Features**:
- Calculates MD5, SHA1, and SHA256 hashes
- Analyzes ESP32 image header
- Identifies flash configuration
- Locates and parses partition table
- Extracts strings with categorization
- Performs entropy analysis to detect encryption/compression
- Generates analysis report

**Usage**:
```bash
python3 analyze_firmware.py <firmware.bin>

# Example:
python3 analyze_firmware.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin
```

**Output**: 
- Console: Detailed analysis output
- File: `analysis/<filename>_analysis.txt`

---

### 2. extract_strings.py
**Purpose**: Extract and categorize strings from firmware

**Features**:
- Extracts ASCII strings (min length 4)
- Extracts UTF-16 wide strings
- Categorizes strings by type:
  - URLs
  - IP Addresses
  - Email addresses
  - File paths
  - WiFi/Network keywords
  - Hardware/GPIO references
  - Laser control strings
  - Version/Build info
  - Error messages
  - Debug/Log messages
  - ESP32 specific strings

**Usage**:
```bash
python3 extract_strings.py <firmware.bin>

# Example:
python3 extract_strings.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin
```

**Output**:
- Console: Categorized string summary
- File: `analysis/<filename>_strings.txt`

---

### 3. parse_partitions.py
**Purpose**: Parse ESP32 partition table and extract partitions

**Features**:
- Locates partition table (checks common offsets)
- Parses partition entries
- Displays partition layout
- Optionally extracts partitions to separate files
- Validates MD5 checksum

**Usage**:
```bash
# Parse only (display partition table)
python3 parse_partitions.py <firmware.bin>

# Parse and extract partitions
python3 parse_partitions.py <firmware.bin> --extract

# Example:
python3 parse_partitions.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin --extract
```

**Output**:
- Console: Partition table display
- Files: `analysis/partitions/<partition_name>.bin` (if --extract used)

---

### 4. analyze_app_partition.py
**Purpose**: Detailed analysis of ESP32 application partition

**Features**:
- Parses ESP32 application image header
- Maps memory segments (IRAM, DRAM, Flash)
- Identifies entry point
- Estimates function count
- Analyzes SPI configuration

**Usage**:
```bash
python3 analyze_app_partition.py <app_partition.bin>

# Example:
python3 analyze_app_partition.py analysis/partitions/app0.bin
```

**Output**:
- Memory segment mapping
- Entry point address
- Load addresses for Ghidra
- Function count estimate

---

### 5. compare_with_grbl.py
**Purpose**: Compare firmware with stock Grbl_ESP32

**Features**:
- Clones Grbl_ESP32 repository
- Compares strings to identify customizations
- Analyzes source code structure
- Determines what's stock vs custom

**Usage**:
```bash
python3 compare_with_grbl.py <firmware.bin>

# Example:
python3 compare_with_grbl.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin
```

**Output**:
- Customization percentage
- List of custom vs stock features
- Comparison report

---

### 6. advanced_gpio_analysis.py
**Purpose**: Analyze GPIO pin usage patterns

**Features**:
- Scans for GPIO number references
- Counts occurrences per pin
- Identifies likely pin assignments
- Maps I2S, PWM, and control pins

**Usage**:
```bash
python3 advanced_gpio_analysis.py <firmware.bin>

# Example:
python3 advanced_gpio_analysis.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin
```

**Output**:
- GPIO reference counts
- Pin assignment candidates
- I2S pin mapping

---

### 7. run_full_analysis.py
**Purpose**: Run complete analysis workflow

**Features**:
- Runs all analysis scripts in sequence
- Provides comprehensive firmware analysis
- Single command for complete reverse engineering

**Usage**:
```bash
python3 run_full_analysis.py <firmware.bin>

# Example:
python3 run_full_analysis.py firmware/Kiosk\ Firmware\ \(C07-251021\).bin
```

**Output**:
- All analysis outputs from individual scripts
- Complete analysis suite in one run

---

### 8. validate_firmware.py
**Purpose**: Validate rebuilt firmware matches original

**Features**:
- Compares binary sizes
- Checks partition structures
- Validates key strings present
- Reports differences

**Usage**:
```bash
python3 validate_firmware.py <original.bin> <rebuilt.bin>

# Example (after rebuilding):
python3 validate_firmware.py firmware/original.bin .pio/build/genmitsu_kiosk/firmware.bin
```

**Output**:
- Validation report
- List of differences
- Pass/fail status

---

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
All scripts use only Python standard library - no additional packages required!

Standard library modules used:
- `sys`, `os`, `struct`, `hashlib`
- `pathlib`, `subprocess`
- `re`, `collections`

---

## Output Files

All analysis outputs are saved to the `analysis/` directory:

```
analysis/
├── <firmware>_analysis.txt      # Comprehensive firmware analysis
├── <firmware>_strings.txt       # All extracted strings with offsets
└── partitions/                  # Extracted partition binaries
    ├── nvs.bin                  # Non-volatile storage
    ├── otadata.bin              # OTA data
    ├── app0.bin                 # Main application
    ├── app1.bin                 # OTA backup (may be empty)
    └── spiffs.bin               # File system (may be empty)
```

---

## Examples

### Quick Analysis
```bash
# Get basic info
python3 analyze_firmware.py firmware/my_firmware.bin
```

### Find WiFi Credentials
```bash
# Extract strings and search for WiFi info
python3 extract_strings.py firmware/my_firmware.bin
grep -i "ssid\|password\|wifi" analysis/my_firmware_strings.txt
```

### Extract for Ghidra Analysis
```bash
# Extract app partition for reverse engineering
python3 parse_partitions.py firmware/my_firmware.bin --extract

# Then load analysis/partitions/app0.bin in Ghidra
# Processor: Xtensa:LE:32:default
# Load address: 0x3F400000
```

### Complete Analysis Pipeline
```bash
# One command for everything
python3 run_full_analysis.py firmware/my_firmware.bin
```

---

## Advanced Usage

### Analyzing Specific Partitions

After extracting partitions, you can analyze them individually:

```bash
# Analyze NVS partition
hexdump -C analysis/partitions/nvs.bin | less

# Extract strings from app partition
strings analysis/partitions/app0.bin > app_strings.txt

# Check for compression/encryption
file analysis/partitions/app0.bin
```

### Integration with Other Tools

These scripts work well with external tools:

```bash
# Use with binwalk
binwalk analysis/partitions/app0.bin

# Use with radare2
r2 analysis/partitions/app0.bin

# Use with esptool
esptool.py image_info analysis/partitions/app0.bin
```

---

## Script Architecture

### analyze_firmware.py
```
ESP32FirmwareAnalyzer
├── load_firmware()          # Load binary into memory
├── calculate_hashes()       # MD5, SHA1, SHA256
├── analyze_esp32_header()   # Parse ESP32 header
├── find_partition_table()   # Locate partition table
├── parse_partition_table()  # Parse all partitions
├── extract_strings()        # Extract ASCII strings
├── analyze_entropy()        # Detect encryption
└── save_analysis_report()   # Save results
```

### extract_strings.py
```
StringExtractor
├── load_firmware()              # Load binary
├── extract_ascii_strings()      # Get ASCII strings
├── extract_wide_strings()       # Get UTF-16 strings
├── categorize_strings()         # Sort by category
├── print_categories()           # Display results
└── save_strings()               # Save to file
```

### parse_partitions.py
```
PartitionParser
├── load_firmware()              # Load binary
├── find_partition_table()       # Locate table
├── parse_partition_entry()      # Parse single entry
├── parse_partition_table()      # Parse all entries
├── extract_partition()          # Extract one partition
└── extract_all_partitions()     # Extract all partitions
```

---

## Troubleshooting

### "File not found" Error
- Check file path is correct
- Use quotes for filenames with spaces: `"Kiosk Firmware (C07-251021).bin"`

### No Partition Table Found
- Firmware may be encrypted
- May be a partial dump
- Try manual offset search in the script output

### Empty Partitions Extracted
- This is normal for OTA backup partitions
- SPIFFS may be empty in factory firmware
- Only active partitions contain data

### Script Hangs or Slow
- Large firmware files take time
- Entropy analysis is CPU-intensive
- Use smaller block sizes if needed

---

## Contributing

To add new analysis features:

1. Follow existing code structure
2. Add new analysis methods to appropriate class
3. Update this README with new features
4. Test with multiple firmware images
5. Document output format

---

## License

These scripts are provided for educational and research purposes.
Ensure you have proper authorization before analyzing any firmware.

---

**Created**: November 2025  
**Maintainer**: GitHub Copilot Reverse Engineering Agent  
**Python Version**: 3.7+  
**Status**: Production Ready
