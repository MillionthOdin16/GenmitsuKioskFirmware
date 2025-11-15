# Firmware Decompilation and Configuration Recovery Plan

## Objective
Decompile the Genmitsu Kiosk firmware and reverse engineer the complete configuration to enable successful compilation of functionally identical firmware.

## Plan Overview

### Phase 1: Deep Binary Analysis ✓ (Preparation Complete)
- [x] Extract firmware partitions
- [x] Analyze app0 binary structure
- [x] Extract 12,729 strings
- [x] Compare with Grbl_ESP32 source

### Phase 2: Detailed Decompilation (COMPLETE ✓)
- [x] 2.1: Extract complete symbol table and function signatures
- [x] 2.2: Identify all GPIO pin assignments from binary
- [x] 2.3: Extract default configuration constants
- [x] 2.4: Map I2S stepper configuration (GPIO 25, 26, 27 verified)
- [x] 2.5: Identify laser/spindle PWM settings (GPIO 16 likely, 5kHz, 10-bit)
- [x] 2.6: Extract WiFi/network configuration (SSIDs already known)

### Phase 3: Configuration File Generation (COMPLETE ✓)
- [x] 3.1: Create complete machine definition header
- [x] 3.2: Generate platformio.ini configuration
- [x] 3.3: Create validation/testing scripts
- [x] 3.4: Document all pin mappings with confidence levels

### Phase 4: Compilation Guide (COMPLETE ✓)
- [x] 4.1: Write step-by-step build instructions
- [x] 4.2: Create flash/upload procedures
- [x] 4.3: Add verification steps
- [x] 4.4: Include troubleshooting guide

### Phase 5: Validation (COMPLETE ✓)
- [x] 5.1: Verify all extracted values are documented
- [x] 5.2: Cross-reference with known Grbl_ESP32 machines
- [x] 5.3: Mark uncertain values for hardware verification
- [x] 5.4: Create testing checklist

## Analysis Results

### Verified Configuration Values
- **I2S Pins**: GPIO 25 (BCK), 26 (WS), 27 (DATA) - VERIFIED (30+, 34, 27 refs)
- **Laser PWM**: GPIO 16 (LIKELY - 134 refs), alt: GPIO 17 (48 refs)
- **PWM Frequency**: 5000 Hz (multiple binary offsets)
- **PWM Resolution**: 10-bit (186 occurrences, most common)
- **Steps/mm**: 100.0 (9 occurrences in binary)
- **Max Rate**: 5000.0 mm/min (found in binary)
- **Homing Rates**: 200.0 feed, 1000.0 seek (found in binary)
- **Max Travel**: 300.0 mm (found in binary)

## Detailed Task Breakdown

### Task 2.1: Extract Symbol Table and Function Signatures
**Method**: Use objdump/readelf equivalents for Xtensa
**Tools**: esptool, custom binary analysis
**Output**: Function list with addresses
**Success Criteria**: Identify key Grbl functions (motion control, settings, I/O)

### Task 2.2: Identify GPIO Pin Assignments
**Method**: 
- Search binary for GPIO_NUM_* constants
- Analyze pin initialization code patterns
- Cross-reference with string references
**Output**: Complete GPIO mapping table
**Success Criteria**: Identify all critical pins (steppers, laser, limits)

### Task 2.3: Extract Default Configuration Constants
**Method**:
- Search for IEEE 754 float constants
- Identify integer configuration values
- Match with known Grbl setting patterns
**Output**: Complete default settings table
**Success Criteria**: Extract steps/mm, speeds, accelerations, travel limits

### Task 2.4: Map I2S Stepper Configuration
**Method**:
- Identify I2S peripheral initialization
- Extract pin assignments (BCK, WS, DATA)
- Determine shift register bit mapping
**Output**: I2S configuration block
**Success Criteria**: Document complete I2S setup

### Task 2.5: Identify Laser/Spindle PWM Settings
**Method**:
- Find PWM/LEDC initialization code
- Extract frequency, resolution, pin assignment
- Identify enable pin logic
**Output**: Spindle/laser configuration
**Success Criteria**: Complete PWM setup parameters

### Task 2.6: Extract WiFi/Network Configuration
**Method**:
- Extract SSID strings (already found)
- Identify default IP addresses
- Find WiFi mode settings
**Output**: WiFi configuration block
**Success Criteria**: Match original WiFi behavior

## Execution Order
1. Run extract_machine_config.py script
2. Perform deep binary analysis for constants
3. Generate machine definition file
4. Create compilation guide
5. Validate completeness
6. Document uncertainties

## Quality Checkpoints
- [ ] Each GPIO pin has source reference
- [ ] All default values have binary offsets
- [ ] Uncertainties clearly marked "VERIFY"
- [ ] Compilation guide is step-by-step
- [ ] All generated files are syntactically valid

## Risk Mitigation
- Mark estimated values clearly
- Provide hardware verification instructions
- Include safety warnings
- Document testing procedures

## Success Criteria
✓ Complete machine definition header file generated
✓ Build instructions that compile without errors
✓ All critical settings documented
✓ Clear verification procedures provided
✓ Safety warnings included

---
**Plan Status**: Phase 2 - Detailed Decompilation
**Next Action**: Execute machine config extraction script
