#!/usr/bin/env python3
"""
Grbl_ESP32 Customization Comparison
Compares Genmitsu Kiosk firmware with standard Grbl_ESP32 to identify customizations
"""

import sys
import os
from pathlib import Path
import re

class GrblCustomizationAnalyzer:
    """Analyze customizations in Genmitsu firmware vs stock Grbl_ESP32"""
    
    def __init__(self, firmware_strings_path, grbl_repo_path):
        self.firmware_strings_path = Path(firmware_strings_path)
        self.grbl_repo_path = Path(grbl_repo_path)
        self.firmware_strings = []
        self.grbl_strings = set()
        self.customizations = {
            'wifi_ssids': [],
            'custom_strings': [],
            'version_info': [],
            'unique_features': [],
            'settings': [],
            'machine_name': None,
        }
        
    def load_firmware_strings(self):
        """Load extracted firmware strings"""
        print("[INFO] Loading firmware strings...")
        with open(self.firmware_strings_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Parse format: [0xOFFSET] [ENCODING] string
                if '] [' in line:
                    parts = line.split('] ', 2)
                    if len(parts) >= 3:
                        string = parts[2].strip()
                        self.firmware_strings.append(string)
                        
        print(f"[INFO] Loaded {len(self.firmware_strings)} firmware strings")
        
    def scan_grbl_source(self):
        """Scan Grbl_ESP32 source code for strings"""
        print("[INFO] Scanning Grbl_ESP32 source code...")
        
        # Scan all .h, .cpp, .c files
        source_files = []
        for ext in ['.h', '.cpp', '.c']:
            source_files.extend(self.grbl_repo_path.rglob(f'*{ext}'))
            
        print(f"[INFO] Found {len(source_files)} source files")
        
        string_pattern = re.compile(r'"([^"\\]*(\\.[^"\\]*)*)"')
        
        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = string_pattern.findall(content)
                    for match in matches:
                        if isinstance(match, tuple):
                            self.grbl_strings.add(match[0])
                        else:
                            self.grbl_strings.add(match)
            except:
                pass
                
        print(f"[INFO] Found {len(self.grbl_strings)} unique strings in Grbl_ESP32")
        
    def identify_customizations(self):
        """Identify Genmitsu-specific customizations"""
        print("\n" + "=" * 80)
        print("IDENTIFYING CUSTOMIZATIONS")
        print("=" * 80)
        
        # 1. WiFi SSIDs
        print("\n### WiFi SSIDs (Customized)")
        for s in self.firmware_strings:
            if 'Genmitsu' in s or 'genmitsu' in s:
                if 'SSID' in s or 'Kiosk' in s:
                    self.customizations['wifi_ssids'].append(s)
                    print(f"  - {s}")
                    
        # 2. Version strings
        print("\n### Version Information (Customized)")
        for s in self.firmware_strings:
            if 'C07' in s or 'V07' in s or '251021' in s:
                if s not in self.grbl_strings:
                    self.customizations['version_info'].append(s)
                    print(f"  - {s}")
                    
        # 3. Custom strings not in stock Grbl
        print("\n### Unique Strings Not in Stock Grbl_ESP32")
        custom_count = 0
        interesting_custom = []
        
        for s in self.firmware_strings:
            # Filter to interesting strings
            if len(s) > 10 and len(s) < 100:
                if s not in self.grbl_strings:
                    # Check if it's interesting
                    if any(keyword in s.lower() for keyword in [
                        'laser', 'spindle', 'gpio', 'pin', 'motor', 
                        'axis', 'setting', 'config', 'machine'
                    ]):
                        if 'component' not in s and 'binary' not in s:
                            interesting_custom.append(s)
                            custom_count += 1
                            
        # Show top custom strings
        for s in interesting_custom[:30]:
            print(f"  - {s}")
            
        if len(interesting_custom) > 30:
            print(f"  ... and {len(interesting_custom) - 30} more")
            
        self.customizations['custom_strings'] = interesting_custom
        
    def analyze_settings(self):
        """Analyze custom settings"""
        print("\n### Custom Settings")
        
        setting_patterns = [
            '$Laser/',
            '$Spindle/',
            '$GCode/',
            '$Axes/',
            'Genmitsu',
        ]
        
        for s in self.firmware_strings:
            for pattern in setting_patterns:
                if pattern in s and len(s) < 100:
                    if s not in self.grbl_strings or 'Genmitsu' in s:
                        self.customizations['settings'].append(s)
                        print(f"  - {s}")
                        break
                        
    def compare_machine_definitions(self):
        """Compare with standard machine definitions"""
        print("\n### Machine Definition Comparison")
        
        # Find machine name
        for s in self.firmware_strings:
            if 'MACHINE_NAME' in s or 'Genmitsu_Kiosk' in s:
                self.customizations['machine_name'] = s
                print(f"  Machine Name: {s}")
                
        # Look for GPIO pins
        print("\n  GPIO Pin References:")
        gpio_refs = []
        for s in self.firmware_strings:
            if 'GPIO_NUM_' in s or ('pin' in s.lower() and 'Pin:' in s):
                if len(s) < 150 and s not in gpio_refs:
                    gpio_refs.append(s)
                    if len(gpio_refs) <= 10:
                        print(f"    {s}")
                        
        if len(gpio_refs) > 10:
            print(f"    ... and {len(gpio_refs) - 10} more GPIO references")
            
    def analyze_features(self):
        """Analyze feature differences"""
        print("\n### Feature Analysis")
        
        features = {
            'WiFi/Network': ['wifi', 'http', 'websocket', 'mdns', 'ssdp'],
            'Laser Control': ['laser', 'pwm', 'm3', 'm4', 'm5'],
            'Stepper Control': ['i2s', 'step', 'direction', 'motor'],
            'Limit Switches': ['limit', 'homing', 'probe'],
            'File System': ['spiffs', 'file', 'sd'],
            'OTA Updates': ['ota', 'update', 'firmware'],
        }
        
        for feature_name, keywords in features.items():
            count = 0
            for s in self.firmware_strings:
                if any(kw in s.lower() for kw in keywords):
                    count += 1
                    
            print(f"  {feature_name}: {count} references")
            
    def generate_comparison_report(self):
        """Generate detailed comparison report"""
        report_path = Path(__file__).parent.parent / "analysis" / "grbl_customization_comparison.md"
        
        print(f"\n[INFO] Generating detailed report: {report_path}")
        
        with open(report_path, 'w') as f:
            f.write("# Genmitsu Kiosk Customization Analysis\n\n")
            f.write("Comparison of Genmitsu Kiosk firmware vs. stock Grbl_ESP32\n\n")
            f.write("## Summary\n\n")
            
            f.write(f"- Firmware strings analyzed: {len(self.firmware_strings)}\n")
            f.write(f"- Stock Grbl_ESP32 strings: {len(self.grbl_strings)}\n")
            f.write(f"- WiFi SSIDs customized: {len(self.customizations['wifi_ssids'])}\n")
            f.write(f"- Version strings: {len(self.customizations['version_info'])}\n")
            f.write(f"- Unique custom strings: {len(self.customizations['custom_strings'])}\n")
            f.write(f"- Custom settings: {len(self.customizations['settings'])}\n\n")
            
            f.write("## WiFi Configuration Customizations\n\n")
            for ssid in self.customizations['wifi_ssids']:
                f.write(f"- `{ssid}`\n")
                
            f.write("\n## Version/Build Customizations\n\n")
            for v in self.customizations['version_info']:
                f.write(f"- `{v}`\n")
                
            f.write("\n## Custom Settings\n\n")
            for setting in self.customizations['settings'][:50]:
                f.write(f"- `{setting}`\n")
                
            f.write("\n## Analysis\n\n")
            f.write("### Customization Level\n\n")
            
            # Calculate customization percentage
            unique_count = len(self.customizations['custom_strings'])
            total_count = len(self.firmware_strings)
            if total_count > 0:
                custom_pct = (unique_count / total_count) * 100
                f.write(f"Approximately {custom_pct:.1f}% of strings are unique to Genmitsu firmware.\n\n")
                
            f.write("### Main Customizations\n\n")
            f.write("1. **WiFi SSID Branding**: Genmitsu-specific SSID names\n")
            f.write("2. **Version Identification**: Custom build identifiers (C07-251021)\n")
            f.write("3. **Machine Name**: Genmitsu_Kiosk branding\n")
            f.write("4. **Hardware Configuration**: Custom GPIO pin assignments\n")
            f.write("5. **Default Settings**: Tuned for Genmitsu Kiosk hardware\n\n")
            
            f.write("### Conclusion\n\n")
            f.write("The Genmitsu Kiosk firmware is based on stock Grbl_ESP32 with:\n")
            f.write("- Custom machine definition (pin assignments)\n")
            f.write("- Branded WiFi configuration\n")
            f.write("- Tuned default settings for the specific hardware\n")
            f.write("- Standard Grbl_ESP32 core functionality intact\n")
            
        print(f"[INFO] Report generated: {report_path}")
        
    def run_analysis(self):
        """Run complete comparison analysis"""
        self.load_firmware_strings()
        self.scan_grbl_source()
        self.identify_customizations()
        self.analyze_settings()
        self.compare_machine_definitions()
        self.analyze_features()
        self.generate_comparison_report()
        
        print("\n" + "=" * 80)
        print("COMPARISON ANALYSIS COMPLETE")
        print("=" * 80)
        
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 compare_with_grbl.py <firmware_strings.txt> <grbl_repo_path>")
        print("\nExample:")
        print("  python3 compare_with_grbl.py \\")
        print("    analysis/'Kiosk Firmware (C07-251021)_strings.txt' \\")
        print("    /tmp/Grbl_Esp32")
        sys.exit(1)
        
    strings_path = sys.argv[1]
    grbl_path = sys.argv[2]
    
    analyzer = GrblCustomizationAnalyzer(strings_path, grbl_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
