#!/usr/bin/env python3
"""
ESP32 Firmware Analysis Script
Comprehensive analysis tool for ESP32 firmware binaries
"""

import sys
import os
import struct
import hashlib
from pathlib import Path

class ESP32FirmwareAnalyzer:
    """Analyzer for ESP32 firmware binaries"""
    
    # ESP32 magic numbers
    ESP_IMAGE_MAGIC = 0xE9
    ESP_CHECKSUM_MAGIC = 0xEF
    
    # Chip types
    CHIP_TYPES = {
        0x0000: "ESP32",
        0x0002: "ESP32-S2",
        0x0005: "ESP32-C3",
        0x0009: "ESP32-S3",
        0x000C: "ESP32-C2",
        0x000D: "ESP32-C6",
        0x0010: "ESP32-H2",
    }
    
    def __init__(self, firmware_path):
        self.firmware_path = Path(firmware_path)
        self.firmware_data = None
        self.file_size = 0
        
    def load_firmware(self):
        """Load firmware binary into memory"""
        if not self.firmware_path.exists():
            print(f"[ERROR] Firmware file not found: {self.firmware_path}")
            return False
            
        with open(self.firmware_path, 'rb') as f:
            self.firmware_data = f.read()
            self.file_size = len(self.firmware_data)
            
        print(f"[INFO] Loaded firmware: {self.firmware_path.name}")
        print(f"[INFO] File size: {self.file_size:,} bytes ({self.file_size / 1024:.2f} KB)")
        return True
        
    def calculate_hashes(self):
        """Calculate various hashes of the firmware"""
        print("\n=== File Hashes ===")
        
        md5_hash = hashlib.md5(self.firmware_data).hexdigest()
        sha1_hash = hashlib.sha1(self.firmware_data).hexdigest()
        sha256_hash = hashlib.sha256(self.firmware_data).hexdigest()
        
        print(f"MD5:    {md5_hash}")
        print(f"SHA1:   {sha1_hash}")
        print(f"SHA256: {sha256_hash}")
        
    def analyze_esp32_header(self):
        """Analyze ESP32 image header"""
        print("\n=== ESP32 Image Header Analysis ===")
        
        if len(self.firmware_data) < 24:
            print("[WARNING] File too small to contain ESP32 header")
            return
            
        # Check for ESP32 magic byte at offset 0
        magic = self.firmware_data[0]
        print(f"Magic byte: 0x{magic:02X}", end="")
        
        if magic == self.ESP_IMAGE_MAGIC:
            print(" ✓ (Valid ESP32 image)")
        else:
            print(" ✗ (Not a standard ESP32 image)")
            
        # Parse header (simplified)
        if magic == self.ESP_IMAGE_MAGIC and len(self.firmware_data) >= 24:
            segment_count = self.firmware_data[1]
            flash_mode = self.firmware_data[2]
            flash_size_freq = self.firmware_data[3]
            entry_addr = struct.unpack('<I', self.firmware_data[4:8])[0]
            
            print(f"Segments: {segment_count}")
            print(f"Flash mode: {self.get_flash_mode(flash_mode)}")
            print(f"Flash size: {self.get_flash_size(flash_size_freq & 0xF0)}")
            print(f"Flash freq: {self.get_flash_freq(flash_size_freq & 0x0F)}")
            print(f"Entry point: 0x{entry_addr:08X}")
            
    def get_flash_mode(self, mode):
        """Get flash mode string"""
        modes = {0: "QIO", 1: "QOUT", 2: "DIO", 3: "DOUT"}
        return modes.get(mode, f"Unknown (0x{mode:02X})")
        
    def get_flash_size(self, size):
        """Get flash size string"""
        sizes = {
            0x00: "1MB", 0x10: "2MB", 0x20: "4MB", 0x30: "8MB",
            0x40: "16MB", 0x50: "32MB", 0x60: "64MB", 0x70: "128MB"
        }
        return sizes.get(size, f"Unknown (0x{size:02X})")
        
    def get_flash_freq(self, freq):
        """Get flash frequency string"""
        freqs = {0: "40MHz", 1: "26MHz", 2: "20MHz", 0xF: "80MHz"}
        return freqs.get(freq, f"Unknown (0x{freq:02X})")
        
    def find_partition_table(self):
        """Search for ESP32 partition table"""
        print("\n=== Partition Table Search ===")
        
        # Partition table signature
        PT_MAGIC = b'\xAA\x50'
        
        # Common partition table offsets
        common_offsets = [0x8000, 0x9000, 0xA000, 0x10000]
        
        for offset in common_offsets:
            if offset + 2 <= len(self.firmware_data):
                if self.firmware_data[offset:offset+2] == PT_MAGIC:
                    print(f"[+] Partition table found at offset: 0x{offset:08X}")
                    self.parse_partition_table(offset)
                    return True
                    
        # Search entire file
        print("[INFO] Searching entire firmware for partition table...")
        for i in range(len(self.firmware_data) - 2):
            if self.firmware_data[i:i+2] == PT_MAGIC:
                print(f"[+] Possible partition table at offset: 0x{i:08X}")
                
        return False
        
    def parse_partition_table(self, offset):
        """Parse partition table entries"""
        print("\nPartition entries:")
        print(f"{'Name':<16} {'Type':<10} {'SubType':<10} {'Offset':<12} {'Size':<12}")
        print("-" * 70)
        
        entry_offset = offset
        max_entries = 95  # Maximum partition table entries
        
        for i in range(max_entries):
            if entry_offset + 32 > len(self.firmware_data):
                break
                
            entry = self.firmware_data[entry_offset:entry_offset+32]
            
            # Check for end of partition table (all 0xFF)
            if entry[0:2] == b'\xFF\xFF':
                break
                
            # Check for partition magic
            if entry[0:2] != b'\xAA\x50':
                break
                
            # Parse entry
            type_val = entry[2]
            subtype = entry[3]
            part_offset = struct.unpack('<I', entry[4:8])[0]
            part_size = struct.unpack('<I', entry[8:12])[0]
            name = entry[12:28].rstrip(b'\x00').decode('ascii', errors='ignore')
            
            type_str = self.get_partition_type(type_val)
            subtype_str = self.get_partition_subtype(type_val, subtype)
            
            print(f"{name:<16} {type_str:<10} {subtype_str:<10} 0x{part_offset:08X}   {part_size:>10} B")
            
            entry_offset += 32
            
    def get_partition_type(self, type_val):
        """Get partition type name"""
        types = {0x00: "app", 0x01: "data"}
        return types.get(type_val, f"0x{type_val:02X}")
        
    def get_partition_subtype(self, type_val, subtype):
        """Get partition subtype name"""
        if type_val == 0x00:  # app
            subtypes = {
                0x00: "factory",
                0x10: "ota_0",
                0x11: "ota_1",
                0x20: "test"
            }
        elif type_val == 0x01:  # data
            subtypes = {
                0x00: "ota",
                0x01: "phy",
                0x02: "nvs",
                0x03: "coredump",
                0x04: "nvs_keys",
                0x05: "efuse",
                0x80: "esphttpd",
                0x81: "fat",
                0x82: "spiffs"
            }
        else:
            subtypes = {}
            
        return subtypes.get(subtype, f"0x{subtype:02X}")
        
    def extract_strings(self, min_length=4):
        """Extract printable strings from firmware"""
        print("\n=== String Extraction ===")
        print(f"Extracting strings (min length: {min_length})...")
        
        strings_found = []
        current_string = []
        
        for byte in self.firmware_data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string.append(chr(byte))
            else:
                if len(current_string) >= min_length:
                    strings_found.append(''.join(current_string))
                current_string = []
                
        if len(current_string) >= min_length:
            strings_found.append(''.join(current_string))
            
        print(f"[INFO] Found {len(strings_found)} strings")
        
        # Show interesting strings
        interesting_keywords = [
            'esp', 'ESP', 'wifi', 'WIFI', 'http', 'MQTT', 'mqtt',
            'laser', 'Laser', 'LASER', 'genmitsu', 'Genmitsu',
            'serial', 'uart', 'gpio', 'i2c', 'spi',
            'version', 'firmware', 'boot', 'update'
        ]
        
        print("\nInteresting strings found:")
        shown = 0
        for s in strings_found:
            if any(keyword.lower() in s.lower() for keyword in interesting_keywords):
                print(f"  {s}")
                shown += 1
                if shown >= 50:
                    print(f"  ... ({len(strings_found) - shown} more)")
                    break
                    
        return strings_found
        
    def analyze_entropy(self, block_size=1024):
        """Analyze entropy to identify compressed/encrypted sections"""
        print("\n=== Entropy Analysis ===")
        
        import math
        from collections import Counter
        
        num_blocks = len(self.firmware_data) // block_size
        print(f"Analyzing {num_blocks} blocks of {block_size} bytes...")
        
        high_entropy_blocks = []
        
        for i in range(num_blocks):
            block = self.firmware_data[i*block_size:(i+1)*block_size]
            
            # Calculate Shannon entropy
            counter = Counter(block)
            entropy = 0
            for count in counter.values():
                p = count / len(block)
                entropy -= p * math.log2(p)
                
            # High entropy (> 7.0) suggests encryption or compression
            if entropy > 7.0:
                high_entropy_blocks.append((i * block_size, entropy))
                
        if high_entropy_blocks:
            print(f"[+] Found {len(high_entropy_blocks)} high-entropy blocks (possibly encrypted/compressed):")
            for offset, entropy in high_entropy_blocks[:10]:
                print(f"  Offset 0x{offset:08X}: entropy = {entropy:.2f}")
            if len(high_entropy_blocks) > 10:
                print(f"  ... and {len(high_entropy_blocks) - 10} more")
        else:
            print("[INFO] No high-entropy blocks detected")
            
    def save_analysis_report(self, output_dir):
        """Save analysis report to file"""
        output_path = Path(output_dir) / f"{self.firmware_path.stem}_analysis.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[INFO] Saving analysis report to: {output_path}")
        
        # The report would be written here
        # For now, just create a placeholder
        with open(output_path, 'w') as f:
            f.write(f"Analysis Report for {self.firmware_path.name}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"File size: {self.file_size:,} bytes\n")
            f.write(f"MD5: {hashlib.md5(self.firmware_data).hexdigest()}\n")
            f.write("\nFor detailed analysis, run this script again.\n")
            
    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 70)
        print("ESP32 Firmware Analysis Tool")
        print("=" * 70)
        
        if not self.load_firmware():
            return False
            
        self.calculate_hashes()
        self.analyze_esp32_header()
        self.find_partition_table()
        self.extract_strings()
        self.analyze_entropy()
        
        # Save report
        analysis_dir = Path(__file__).parent.parent / "analysis"
        self.save_analysis_report(analysis_dir)
        
        print("\n" + "=" * 70)
        print("Analysis complete!")
        print("=" * 70)
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_firmware.py <firmware.bin>")
        print("\nExample:")
        print("  python3 analyze_firmware.py firmware/genmitsu_kiosk.bin")
        sys.exit(1)
        
    firmware_path = sys.argv[1]
    
    analyzer = ESP32FirmwareAnalyzer(firmware_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
