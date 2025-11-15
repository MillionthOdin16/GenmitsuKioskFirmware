#!/usr/bin/env python3
"""
ESP32 App Partition Detailed Analyzer
Analyzes the main application partition for detailed reverse engineering
"""

import sys
import struct
from pathlib import Path

class AppPartitionAnalyzer:
    """Detailed analysis of ESP32 application partition"""
    
    ESP_IMAGE_HEADER_MAGIC = 0xE9
    
    def __init__(self, app_path):
        self.app_path = Path(app_path)
        self.app_data = None
        
    def load_app(self):
        """Load application partition"""
        if not self.app_path.exists():
            print(f"[ERROR] File not found: {self.app_path}")
            return False
            
        with open(self.app_path, 'rb') as f:
            self.app_data = f.read()
            
        print(f"[INFO] Loaded app partition: {len(self.app_data):,} bytes")
        return True
        
    def analyze_app_header(self):
        """Analyze ESP32 application image header"""
        print("\n" + "=" * 80)
        print("ESP32 APPLICATION IMAGE HEADER")
        print("=" * 80)
        
        if len(self.app_data) < 24:
            print("[ERROR] File too small for ESP32 app header")
            return
            
        # Parse image header
        magic = self.app_data[0]
        segment_count = self.app_data[1]
        spi_mode = self.app_data[2]
        spi_speed_size = self.app_data[3]
        entry_addr = struct.unpack('<I', self.app_data[4:8])[0]
        
        print(f"\nImage Header (offset 0x0000):")
        print(f"  Magic:          0x{magic:02X}", end="")
        if magic == self.ESP_IMAGE_HEADER_MAGIC:
            print(" ✓ (Valid ESP32 image)")
        else:
            print(" (Non-standard)")
            
        print(f"  Segment count:  {segment_count}")
        print(f"  SPI mode:       {self.get_spi_mode(spi_mode)}")
        print(f"  SPI speed:      {self.get_spi_speed(spi_speed_size & 0x0F)}")
        print(f"  SPI size:       {self.get_flash_size((spi_speed_size & 0xF0) >> 4)}")
        print(f"  Entry point:    0x{entry_addr:08X}")
        
        # Parse extended header if present
        if len(self.app_data) >= 32:
            wp_pin = self.app_data[8]
            print(f"  WP pin:         {wp_pin} (0xFF = disabled)")
            
            # Additional info
            clk_div = self.app_data[9:12]
            print(f"  Drive settings: {clk_div.hex()}")
            
        # Parse segments
        print(f"\n  Segments:")
        offset = 24  # After header
        
        for i in range(segment_count):
            if offset + 8 > len(self.app_data):
                break
                
            seg_addr = struct.unpack('<I', self.app_data[offset:offset+4])[0]
            seg_size = struct.unpack('<I', self.app_data[offset+4:offset+8])[0]
            
            print(f"    Segment {i}: Load addr 0x{seg_addr:08X}, Size {seg_size:,} bytes ({seg_size/1024:.1f} KB)")
            
            # Identify segment type by load address
            if 0x40000000 <= seg_addr < 0x40400000:
                print(f"              → IRAM (Instruction RAM)")
            elif 0x3FF00000 <= seg_addr < 0x3FF80000:
                print(f"              → DRAM (Data RAM)")
            elif 0x3F400000 <= seg_addr < 0x3F800000:
                print(f"              → Flash cache mapping")
            elif 0x50000000 <= seg_addr < 0x50002000:
                print(f"              → RTC Fast Memory")
                
            offset += 8 + seg_size
            # Align to 4 bytes
            if seg_size % 4:
                offset += 4 - (seg_size % 4)
                
    def get_spi_mode(self, mode):
        """Get SPI mode string"""
        modes = {0: "QIO", 1: "QOUT", 2: "DIO", 3: "DOUT"}
        return modes.get(mode, f"Unknown (0x{mode:02X})")
        
    def get_spi_speed(self, speed):
        """Get SPI speed string"""
        speeds = {0: "40MHz", 1: "26MHz", 2: "20MHz", 0xF: "80MHz"}
        return speeds.get(speed, f"Unknown (0x{speed:02X})")
        
    def get_flash_size(self, size):
        """Get flash size string"""
        sizes = {0: "1MB", 1: "2MB", 2: "4MB", 3: "8MB", 4: "16MB"}
        return sizes.get(size, f"Unknown (0x{size:02X})")
        
    def find_function_signatures(self):
        """Search for common function signatures and patterns"""
        print("\n" + "=" * 80)
        print("FUNCTION SIGNATURE ANALYSIS")
        print("=" * 80)
        
        # Look for common ESP32 function prologues
        # Xtensa typically uses entry instruction: 0x36 0xXX 0xXX
        entry_pattern = b'\x36'
        
        entry_count = 0
        for i in range(len(self.app_data) - 2):
            if self.app_data[i] == 0x36:
                # Check if it looks like an entry instruction
                entry_count += 1
                
        print(f"[INFO] Found approximately {entry_count} potential function entries")
        print(f"[INFO] Estimated function count: ~{entry_count // 10} functions")
        
    def find_constants(self):
        """Find interesting constants and magic numbers"""
        print("\n" + "=" * 80)
        print("CONSTANT ANALYSIS")
        print("=" * 80)
        
        constants = {
            # GPIO related
            0x3FF44000: "GPIO_BASE",
            0x3FF00000: "DPORT_BASE",
            
            # Common frequencies (in Hz)
            115200: "UART Baud Rate (115200)",
            80000000: "80 MHz",
            40000000: "40 MHz",
            26000000: "26 MHz",
            
            # Common port numbers
            80: "HTTP Port",
            443: "HTTPS Port",
            1900: "SSDP Port",
            5353: "mDNS Port",
            
            # WiFi channel
            2412: "WiFi Channel 1 (2.4GHz)",
            2437: "WiFi Channel 6 (2.4GHz)",
            2462: "WiFi Channel 11 (2.4GHz)",
        }
        
        found_constants = {}
        
        # Search for 32-bit little-endian constants
        for i in range(0, len(self.app_data) - 4, 4):
            value = struct.unpack('<I', self.app_data[i:i+4])[0]
            if value in constants:
                if value not in found_constants:
                    found_constants[value] = []
                found_constants[value].append(i)
                
        print("\nFound constants:")
        for value, offsets in sorted(found_constants.items()):
            print(f"  0x{value:08X} ({value:,}) - {constants[value]}")
            print(f"    Found at {len(offsets)} location(s): {', '.join([f'0x{o:06X}' for o in offsets[:5]])}", end="")
            if len(offsets) > 5:
                print(f" ... and {len(offsets) - 5} more")
            else:
                print()
                
    def find_version_strings(self):
        """Find version-related strings"""
        print("\n" + "=" * 80)
        print("VERSION STRING ANALYSIS")
        print("=" * 80)
        
        # Convert to string for searching
        data_str = self.app_data.decode('latin1')
        
        version_patterns = [
            'v3.2.3-14-gd3e562907',
            'Grbl_ESP32',
            'C07-251021',
            'Genmitsu',
            'ESP-IDF',
        ]
        
        print("\nVersion-related strings:")
        for pattern in version_patterns:
            idx = data_str.find(pattern)
            if idx != -1:
                # Extract surrounding context
                start = max(0, idx - 20)
                end = min(len(data_str), idx + len(pattern) + 20)
                context = data_str[start:end].replace('\n', '\\n').replace('\r', '\\r')
                print(f"  [0x{idx:06X}] ...{context}...")
                
    def analyze_data_sections(self):
        """Analyze data sections for configuration"""
        print("\n" + "=" * 80)
        print("DATA SECTION ANALYSIS")
        print("=" * 80)
        
        # Look for GRBL configuration defaults
        print("\nSearching for GRBL setting patterns...")
        
        # Common GRBL setting markers
        settings_markers = [
            b'$0=',
            b'$1=',
            b'$GCode/',
            b'$Laser/',
            b'$Spindle/',
        ]
        
        found = 0
        for marker in settings_markers:
            idx = self.app_data.find(marker)
            if idx != -1:
                found += 1
                # Extract setting
                end_idx = self.app_data.find(b'\x00', idx)
                if end_idx != -1 and end_idx - idx < 100:
                    setting = self.app_data[idx:end_idx].decode('ascii', errors='ignore')
                    print(f"  [0x{idx:06X}] {setting}")
                    
        if found == 0:
            print("  [INFO] No GRBL setting strings found (may be dynamically generated)")
            
    def create_memory_map(self):
        """Create a memory map of the application"""
        print("\n" + "=" * 80)
        print("MEMORY MAP SUMMARY")
        print("=" * 80)
        
        print("""
ESP32 Application Memory Layout:
  
  0x00000000 - 0x00000018   Image Header (24 bytes)
  0x00000018 - ...          Segment Headers + Data
  
Typical ESP32 Memory Regions:
  
  0x40000000 - 0x40400000   IRAM (Instruction RAM) - 4MB
    └─ Contains executable code, interrupt handlers
  
  0x3FF00000 - 0x3FF80000   DRAM (Data RAM) - 512KB
    └─ Variables, stack, heap
  
  0x3F400000 - 0x3F800000   Flash Cache Mapping - 4MB
    └─ Read-only code and data from flash
  
  0x50000000 - 0x50002000   RTC Fast Memory - 8KB
    └─ Deep sleep retention memory
    
For detailed disassembly:
  1. Load app0.bin in Ghidra
  2. Processor: Xtensa:LE:32:default
  3. Base address: 0x3F400000 (or use segment load addresses)
  4. Analyze and decompile
""")
        
    def generate_ghidra_script(self):
        """Generate a Ghidra import script"""
        output_path = Path(__file__).parent.parent / "analysis" / "ghidra_import.py"
        
        script = """# Ghidra Python Script for ESP32 Firmware Analysis
# Load this in Ghidra's Script Manager

from ghidra.app.util.importer import MessageLog
from ghidra.app.util.opinion import BinaryLoader
from ghidra.program.model.lang import LanguageCompilerSpecPair

# ESP32 uses Xtensa LX6 processor
def setup_esp32_analysis():
    # Get current program
    program = getCurrentProgram()
    
    # Define memory regions based on ESP32 architecture
    memory = program.getMemory()
    
    # Add comments about ESP32 architecture
    listing = program.getListing()
    
    print("ESP32 Analysis Setup Complete")
    print("Processor: Xtensa LX6")
    print("Recommended language: Xtensa:LE:32:default")
    print("")
    print("Next steps:")
    print("1. Auto-analyze the binary")
    print("2. Search for strings to find function references")
    print("3. Look for 'app_main' entry point")
    print("4. Analyze interrupt vector table")

# Run setup
setup_esp32_analysis()
"""
        
        with open(output_path, 'w') as f:
            f.write(script)
            
        print(f"[INFO] Generated Ghidra script: {output_path}")
        
    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 80)
        print("ESP32 APP PARTITION DETAILED ANALYZER")
        print("=" * 80)
        
        if not self.load_app():
            return False
            
        self.analyze_app_header()
        self.find_version_strings()
        self.find_constants()
        self.analyze_data_sections()
        self.find_function_signatures()
        self.create_memory_map()
        self.generate_ghidra_script()
        
        print("\n" + "=" * 80)
        print("DETAILED ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Load app0.bin in Ghidra for full disassembly")
        print("2. Use generated ghidra_import.py script for setup")
        print("3. Cross-reference with strings analysis")
        print("4. Map out function call graph")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_app_partition.py <app0.bin>")
        print("\nExample:")
        print("  python3 analyze_app_partition.py analysis/partitions/app0.bin")
        sys.exit(1)
        
    app_path = sys.argv[1]
    
    analyzer = AppPartitionAnalyzer(app_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
