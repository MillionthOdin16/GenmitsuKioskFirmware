# GenmitsuKioskFirmware

Reverse engineering project for the Genmitsu Kiosk 2.5W laser engraver firmware (ESP32-based controller).

## Project Overview

This repository contains tools, scripts, and analysis for reverse engineering the ESP32-based firmware of the Genmitsu Kiosk 2.5W laser engraver.

## Directory Structure

```
.
├── firmware/           # Firmware binary files (.bin)
├── tools/             # Reverse engineering tools and utilities
├── scripts/           # Analysis and extraction scripts
├── docs/              # Documentation and analysis reports
└── analysis/          # Analysis output and decompiled code
```

## Prerequisites

The following tools are used for firmware analysis:

- **esptool.py** - ESP32 firmware manipulation tool
- **binwalk** - Firmware analysis and extraction
- **Ghidra** - Advanced decompilation and analysis
- **strings** - String extraction from binaries
- **radare2** - Binary analysis framework
- **objdump** - Disassembly tool

## Quick Start

### 1. Place Firmware Binary

Place your firmware `.bin` file in the `firmware/` directory.

### 2. Run Analysis

```bash
# Analyze firmware structure
python3 scripts/analyze_firmware.py firmware/your_firmware.bin

# Extract strings
python3 scripts/extract_strings.py firmware/your_firmware.bin

# Parse partitions
python3 scripts/parse_partitions.py firmware/your_firmware.bin
```

### 3. View Results

Analysis results will be saved in the `analysis/` directory.

## Workflow

1. **Initial Analysis**: Use `binwalk` and `esptool.py` to identify firmware structure
2. **Partition Extraction**: Extract individual partitions (bootloader, app, etc.)
3. **String Analysis**: Extract and analyze readable strings
4. **Disassembly**: Disassemble executable sections with Ghidra/radare2
5. **Documentation**: Document findings in `docs/`

## Analysis Scripts

- `analyze_firmware.py` - Main analysis script with comprehensive checks
- `extract_strings.py` - Extract and categorize strings from firmware
- `parse_partitions.py` - Parse ESP32 partition table
- `extract_partitions.py` - Extract individual partitions from firmware

## Tools Setup

See `tools/README.md` for detailed setup instructions.

## Contributing

When analyzing the firmware:
1. Document all findings in `docs/FINDINGS.md`
2. Save decompiled code in `analysis/decompiled/`
3. Update this README with new discoveries

## Security Notice

This project is for educational and research purposes. Ensure you have proper authorization before reverse engineering any firmware.

## License

Research and educational use only.