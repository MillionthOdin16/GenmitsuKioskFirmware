#!/usr/bin/env python3
"""
String Extraction and Categorization Script
Extracts and categorizes strings from ESP32 firmware
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

class StringExtractor:
    """Extract and categorize strings from firmware"""
    
    def __init__(self, firmware_path):
        self.firmware_path = Path(firmware_path)
        self.firmware_data = None
        
    def load_firmware(self):
        """Load firmware binary"""
        if not self.firmware_path.exists():
            print(f"[ERROR] File not found: {self.firmware_path}")
            return False
            
        with open(self.firmware_path, 'rb') as f:
            self.firmware_data = f.read()
            
        print(f"[INFO] Loaded {len(self.firmware_data):,} bytes from {self.firmware_path.name}")
        return True
        
    def extract_ascii_strings(self, min_length=4):
        """Extract ASCII strings"""
        strings = []
        current_string = []
        offset = 0
        string_start = 0
        
        for i, byte in enumerate(self.firmware_data):
            if 32 <= byte <= 126:  # Printable ASCII
                if not current_string:
                    string_start = i
                current_string.append(chr(byte))
            else:
                if len(current_string) >= min_length:
                    strings.append({
                        'offset': string_start,
                        'string': ''.join(current_string),
                        'length': len(current_string)
                    })
                current_string = []
                
        if len(current_string) >= min_length:
            strings.append({
                'offset': string_start,
                'string': ''.join(current_string),
                'length': len(current_string)
            })
            
        return strings
        
    def extract_wide_strings(self, min_length=4):
        """Extract UTF-16 wide strings"""
        strings = []
        i = 0
        
        while i < len(self.firmware_data) - 1:
            current_string = []
            string_start = i
            
            while i < len(self.firmware_data) - 1:
                # Check for UTF-16 LE (null byte after printable)
                if self.firmware_data[i+1] == 0 and 32 <= self.firmware_data[i] <= 126:
                    current_string.append(chr(self.firmware_data[i]))
                    i += 2
                else:
                    break
                    
            if len(current_string) >= min_length:
                strings.append({
                    'offset': string_start,
                    'string': ''.join(current_string),
                    'length': len(current_string),
                    'encoding': 'UTF-16LE'
                })
                
            i += 1
            
        return strings
        
    def categorize_strings(self, strings):
        """Categorize strings by type"""
        categories = defaultdict(list)
        
        patterns = {
            'URLs': re.compile(r'https?://|ftp://|www\.'),
            'IP Addresses': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            'Email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'File Paths': re.compile(r'[/\\][a-zA-Z0-9_\-./\\]+'),
            'WiFi/Network': re.compile(r'wifi|ssid|wpa|network|mqtt|http|tcp|udp', re.IGNORECASE),
            'Hardware/GPIO': re.compile(r'gpio|pin|uart|i2c|spi|adc|pwm|led', re.IGNORECASE),
            'Laser Control': re.compile(r'laser|power|engrave|burn|intensity|speed', re.IGNORECASE),
            'Version/Build': re.compile(r'version|v\d+\.\d+|build|firmware|release', re.IGNORECASE),
            'Error Messages': re.compile(r'error|fail|invalid|warn|exception', re.IGNORECASE),
            'Debug/Log': re.compile(r'\[debug\]|\[info\]|\[error\]|printf|log', re.IGNORECASE),
            'ESP32 Specific': re.compile(r'esp32|esp-idf|espressif|xtensa', re.IGNORECASE),
        }
        
        for str_data in strings:
            s = str_data['string']
            categorized = False
            
            for category, pattern in patterns.items():
                if pattern.search(s):
                    categories[category].append(str_data)
                    categorized = True
                    
            if not categorized:
                categories['Uncategorized'].append(str_data)
                
        return categories
        
    def print_categories(self, categories):
        """Print categorized strings"""
        print("\n" + "=" * 70)
        print("STRING CATEGORIZATION")
        print("=" * 70)
        
        for category, strings in sorted(categories.items()):
            if not strings:
                continue
                
            print(f"\n### {category} ({len(strings)} strings)")
            print("-" * 70)
            
            # Show up to 20 strings per category
            for i, str_data in enumerate(strings[:20]):
                print(f"[0x{str_data['offset']:08X}] {str_data['string']}")
                
            if len(strings) > 20:
                print(f"... and {len(strings) - 20} more")
                
    def save_strings(self, strings, output_file):
        """Save all strings to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Strings extracted from: {self.firmware_path.name}\n")
            f.write(f"Total strings: {len(strings)}\n")
            f.write("=" * 70 + "\n\n")
            
            for str_data in strings:
                encoding = str_data.get('encoding', 'ASCII')
                f.write(f"[0x{str_data['offset']:08X}] [{encoding}] {str_data['string']}\n")
                
        print(f"\n[INFO] Saved {len(strings)} strings to: {output_path}")
        
    def run(self):
        """Run string extraction"""
        if not self.load_firmware():
            return False
            
        print("\n[INFO] Extracting ASCII strings...")
        ascii_strings = self.extract_ascii_strings(min_length=4)
        print(f"[+] Found {len(ascii_strings)} ASCII strings")
        
        print("\n[INFO] Extracting wide strings...")
        wide_strings = self.extract_wide_strings(min_length=4)
        print(f"[+] Found {len(wide_strings)} wide strings")
        
        # Combine all strings
        all_strings = ascii_strings + wide_strings
        
        # Categorize
        categories = self.categorize_strings(all_strings)
        self.print_categories(categories)
        
        # Save to file
        analysis_dir = Path(__file__).parent.parent / "analysis"
        output_file = analysis_dir / f"{self.firmware_path.stem}_strings.txt"
        self.save_strings(all_strings, output_file)
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_strings.py <firmware.bin>")
        print("\nExample:")
        print("  python3 extract_strings.py firmware/genmitsu_kiosk.bin")
        sys.exit(1)
        
    firmware_path = sys.argv[1]
    
    extractor = StringExtractor(firmware_path)
    extractor.run()

if __name__ == "__main__":
    main()
