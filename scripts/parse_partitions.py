#!/usr/bin/env python3
"""
ESP32 Partition Parser
Parses and extracts ESP32 partition table
"""

import sys
import struct
from pathlib import Path

class PartitionParser:
    """Parse ESP32 partition table"""
    
    PARTITION_MAGIC = b'\xAA\x50'
    PARTITION_MAGIC_MD5 = b'\xEB\xEB'
    
    PARTITION_TYPES = {
        0x00: "app",
        0x01: "data",
    }
    
    APP_SUBTYPES = {
        0x00: "factory",
        0x10: "ota_0",
        0x11: "ota_1",
        0x12: "ota_2",
        0x13: "ota_3",
        0x14: "ota_4",
        0x15: "ota_5",
        0x16: "ota_6",
        0x17: "ota_7",
        0x18: "ota_8",
        0x19: "ota_9",
        0x1A: "ota_10",
        0x1B: "ota_11",
        0x1C: "ota_12",
        0x1D: "ota_13",
        0x1E: "ota_14",
        0x1F: "ota_15",
        0x20: "test",
    }
    
    DATA_SUBTYPES = {
        0x00: "ota",
        0x01: "phy",
        0x02: "nvs",
        0x03: "coredump",
        0x04: "nvs_keys",
        0x05: "efuse",
        0x80: "esphttpd",
        0x81: "fat",
        0x82: "spiffs",
    }
    
    def __init__(self, firmware_path):
        self.firmware_path = Path(firmware_path)
        self.firmware_data = None
        self.partitions = []
        
    def load_firmware(self):
        """Load firmware file"""
        if not self.firmware_path.exists():
            print(f"[ERROR] File not found: {self.firmware_path}")
            return False
            
        with open(self.firmware_path, 'rb') as f:
            self.firmware_data = f.read()
            
        print(f"[INFO] Loaded {len(self.firmware_data):,} bytes")
        return True
        
    def find_partition_table(self):
        """Find partition table in firmware"""
        # Common offsets for partition table
        common_offsets = [0x8000, 0x9000, 0xA000, 0x10000]
        
        print("[INFO] Searching for partition table...")
        
        for offset in common_offsets:
            if offset + 2 <= len(self.firmware_data):
                if self.firmware_data[offset:offset+2] == self.PARTITION_MAGIC:
                    print(f"[+] Found partition table at 0x{offset:08X}")
                    return offset
                    
        # Search entire file
        print("[INFO] Partition table not at standard offset, searching...")
        for i in range(0, len(self.firmware_data) - 2, 4):  # Aligned search
            if self.firmware_data[i:i+2] == self.PARTITION_MAGIC:
                print(f"[+] Found partition table at 0x{i:08X}")
                return i
                
        print("[WARNING] No partition table found")
        return None
        
    def parse_partition_entry(self, entry_data):
        """Parse a single partition entry"""
        if len(entry_data) < 32:
            return None
            
        # Check magic bytes
        if entry_data[0:2] != self.PARTITION_MAGIC:
            return None
            
        partition = {}
        partition['type'] = entry_data[2]
        partition['subtype'] = entry_data[3]
        partition['offset'] = struct.unpack('<I', entry_data[4:8])[0]
        partition['size'] = struct.unpack('<I', entry_data[8:12])[0]
        partition['name'] = entry_data[12:28].rstrip(b'\x00').decode('ascii', errors='ignore')
        partition['flags'] = struct.unpack('<I', entry_data[28:32])[0]
        
        # Get type and subtype names
        partition['type_name'] = self.PARTITION_TYPES.get(partition['type'], f"0x{partition['type']:02X}")
        
        if partition['type'] == 0x00:  # app
            partition['subtype_name'] = self.APP_SUBTYPES.get(partition['subtype'], f"0x{partition['subtype']:02X}")
        elif partition['type'] == 0x01:  # data
            partition['subtype_name'] = self.DATA_SUBTYPES.get(partition['subtype'], f"0x{partition['subtype']:02X}")
        else:
            partition['subtype_name'] = f"0x{partition['subtype']:02X}"
            
        return partition
        
    def parse_partition_table(self, table_offset):
        """Parse entire partition table"""
        print("\n" + "=" * 80)
        print("PARTITION TABLE")
        print("=" * 80)
        
        self.partitions = []
        offset = table_offset
        max_entries = 95
        
        for i in range(max_entries):
            if offset + 32 > len(self.firmware_data):
                break
                
            entry_data = self.firmware_data[offset:offset+32]
            
            # Check for end marker
            if entry_data[0:2] == b'\xFF\xFF':
                print(f"\n[INFO] End of partition table at entry {i}")
                break
                
            # Check for MD5 checksum entry
            if entry_data[0:2] == self.PARTITION_MAGIC_MD5:
                print(f"\n[INFO] MD5 checksum entry found")
                md5_hash = entry_data[16:32].hex()
                print(f"MD5: {md5_hash}")
                break
                
            partition = self.parse_partition_entry(entry_data)
            if partition:
                self.partitions.append(partition)
            else:
                break
                
            offset += 32
            
        # Print partition table
        if self.partitions:
            print(f"\nFound {len(self.partitions)} partitions:")
            print()
            print(f"{'Name':<16} {'Type':<12} {'SubType':<12} {'Offset':<12} {'Size':<12} {'Flags'}")
            print("-" * 80)
            
            for p in self.partitions:
                size_kb = p['size'] / 1024
                if size_kb >= 1024:
                    size_str = f"{size_kb/1024:.1f} MB"
                else:
                    size_str = f"{size_kb:.0f} KB"
                    
                print(f"{p['name']:<16} {p['type_name']:<12} {p['subtype_name']:<12} "
                      f"0x{p['offset']:08X}   {size_str:<11} 0x{p['flags']:08X}")
        else:
            print("[WARNING] No valid partitions found")
            
    def extract_partition(self, partition, output_dir):
        """Extract a partition to file"""
        output_path = Path(output_dir) / f"{partition['name']}.bin"
        
        start = partition['offset']
        end = start + partition['size']
        
        if end > len(self.firmware_data):
            print(f"[WARNING] Partition {partition['name']} extends beyond file")
            end = len(self.firmware_data)
            
        partition_data = self.firmware_data[start:end]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(partition_data)
            
        print(f"[+] Extracted {partition['name']}: {len(partition_data):,} bytes -> {output_path}")
        
    def extract_all_partitions(self, output_dir):
        """Extract all partitions"""
        if not self.partitions:
            print("[WARNING] No partitions to extract")
            return
            
        print("\n" + "=" * 80)
        print("EXTRACTING PARTITIONS")
        print("=" * 80 + "\n")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for partition in self.partitions:
            self.extract_partition(partition, output_dir)
            
    def run(self, extract=False):
        """Run partition parsing"""
        if not self.load_firmware():
            return False
            
        table_offset = self.find_partition_table()
        if table_offset is not None:
            self.parse_partition_table(table_offset)
            
            if extract and self.partitions:
                analysis_dir = Path(__file__).parent.parent / "analysis" / "partitions"
                self.extract_all_partitions(analysis_dir)
        else:
            print("[ERROR] Could not find partition table")
            return False
            
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_partitions.py <firmware.bin> [--extract]")
        print("\nOptions:")
        print("  --extract    Extract partitions to separate files")
        print("\nExample:")
        print("  python3 parse_partitions.py firmware/genmitsu_kiosk.bin --extract")
        sys.exit(1)
        
    firmware_path = sys.argv[1]
    extract = '--extract' in sys.argv
    
    parser = PartitionParser(firmware_path)
    parser.run(extract=extract)

if __name__ == "__main__":
    main()
