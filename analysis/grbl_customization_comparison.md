# Genmitsu Kiosk Customization Analysis

Comparison of Genmitsu Kiosk firmware vs. stock Grbl_ESP32

## Summary

- Firmware strings analyzed: 12729
- Stock Grbl_ESP32 strings: 1638
- WiFi SSIDs customized: 3
- Version strings: 2
- Unique custom strings: 93
- Custom settings: 3

## WiFi Configuration Customizations

- `Genmitsu_Kiosk_C_V07`
- `Genmitsu_Kiosk_V07`
- `Genmitsu_Kiosk`

## Version/Build Customizations

- `Genmitsu_Kiosk_C_V07`
- `Genmitsu_Kiosk_V07`

## Custom Settings

- `Genmitsu_Kiosk_C_V07`
- `Genmitsu_Kiosk_V07`
- `Genmitsu_Kiosk`

## Analysis

### Customization Level

Approximately 0.7% of strings are unique to Genmitsu firmware.

### Main Customizations

1. **WiFi SSID Branding**: Genmitsu-specific SSID names
2. **Version Identification**: Custom build identifiers (C07-251021)
3. **Machine Name**: Genmitsu_Kiosk branding
4. **Hardware Configuration**: Custom GPIO pin assignments
5. **Default Settings**: Tuned for Genmitsu Kiosk hardware

### Conclusion

The Genmitsu Kiosk firmware is based on stock Grbl_ESP32 with:
- Custom machine definition (pin assignments)
- Branded WiFi configuration
- Tuned default settings for the specific hardware
- Standard Grbl_ESP32 core functionality intact
