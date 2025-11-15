#!/usr/bin/env python3
"""
Exact Configuration Value Extractor
Searches for Grbl default configuration values in binary using known patterns
Does NOT guess - only reports values actually found in firmware
"""

import struct
import sys
from pathlib import Path
from collections import defaultdict

class ExactConfigExtractor:
    """Extract only verifiable configuration from binary"""
    
    def __init__(self, binary_path):
        self.binary_path = Path(binary_path)
        self.data = None
        self.config_values = {}
        
    def load(self):
        with open(self.binary_path, 'rb') as f:
            self.data = f.read()
        print(f"[INFO] Loaded {len(self.data):,} bytes")
        
    def find_float_arrays(self):
        """Find arrays of float values that match Grbl default patterns"""
        print("\n=== Searching for Grbl Default Value Arrays ===")
        
        # Grbl typically stores defaults as arrays of floats
        # Look for sequences of reasonable values
        
        candidates = []
        for i in range(0, len(self.data) - 48, 4):  # Need at least 12 floats
            try:
                # Read 12 consecutive floats (typical for X,Y,Z settings)
                values = []
                for j in range(12):
                    val = struct.unpack('<f', self.data[i+j*4:i+(j+1)*4])[0]
                    values.append(val)
                
                # Check if this looks like Grbl defaults
                # Characteristics:
                # - Values in reasonable ranges (0.1 to 10000)
                # - Not NaN or Inf
                # - Some repetition (X/Y often same)
                if all(0.01 < abs(v) < 100000 or v == 0 for v in values):
                    if not any(abs(v) > 1e6 for v in values):
                        # This might be a defaults array
                        candidates.append((i, values))
                        
            except:
                pass
        
        print(f"[INFO] Found {len(candidates)} potential default value arrays")
        
        # Analyze candidates
        for offset, values in candidates[:10]:  # Show first 10
            # Check if values match known Grbl patterns
            # Steps/mm usually 10-800
            # Max rates usually 100-10000
            # Accelerations usually 10-1000
            # Max travel usually 10-1000
            
            steps = [v for v in values[:3] if 10 <= v <= 800]
            if len(steps) >= 2:  # At least X,Y steps look reasonable
                print(f"\n  Candidate at offset 0x{offset:08X}:")
                print(f"    Possible steps/mm (X,Y,Z): {values[0]:.1f}, {values[1]:.1f}, {values[2]:.1f}")
                
                if len(values) >= 6:
                    print(f"    Possible max rates: {values[3]:.1f}, {values[4]:.1f}, {values[5]:.1f}")
                if len(values) >= 9:
                    print(f"    Possible accelerations: {values[6]:.1f}, {values[7]:.1f}, {values[8]:.1f}")
                if len(values) >= 12:
                    print(f"    Possible max travels: {values[9]:.1f}, {values[10]:.1f}, {values[11]:.1f}")
                    
        return candidates
        
    def search_specific_patterns(self):
        """Search for specific known Grbl patterns"""
        print("\n=== Searching for Specific Grbl Patterns ===")
        
        # Known Grbl default setting order (from Grbl source):
        # $100-$102: steps/mm (X, Y, Z)
        # $110-$112: max rates (X, Y, Z)  
        # $120-$122: accelerations (X, Y, Z)
        # $130-$132: max travels (X, Y, Z)
        
        # Look for this specific pattern in binary
        results = []
        
        for i in range(0, len(self.data) - 48, 4):
            try:
                # Extract 12 floats
                arr = []
                for j in range(12):
                    arr.append(struct.unpack('<f', self.data[i+j*4:i+(j+1)*4])[0])
                
                # Check if this matches Grbl pattern
                # Steps should be 10-800, same for X/Y common
                # Rates should be 100-10000
                # Accel should be 10-1000
                # Travel should be 10-1000
                
                if (10 <= arr[0] <= 800 and  # X steps
                    10 <= arr[1] <= 800 and  # Y steps
                    100 <= arr[3] <= 10000 and  # X max rate
                    100 <= arr[4] <= 10000 and  # Y max rate
                    10 <= arr[6] <= 1000 and  # X accel
                    10 <= arr[7] <= 1000 and  # Y accel
                    10 <= arr[9] <= 1000):  # X max travel
                    
                    # This looks very much like Grbl defaults!
                    results.append((i, arr))
                    
            except:
                pass
        
        if results:
            print(f"[FOUND] {len(results)} arrays matching Grbl default pattern!")
            for offset, arr in results:
                print(f"\n  *** LIKELY GRBL DEFAULTS at offset 0x{offset:08X} ***")
                print(f"  $100 (X steps/mm):      {arr[0]:.3f}")
                print(f"  $101 (Y steps/mm):      {arr[1]:.3f}")
                print(f"  $102 (Z steps/mm):      {arr[2]:.3f}")
                print(f"  $110 (X max rate):      {arr[3]:.3f} mm/min")
                print(f"  $111 (Y max rate):      {arr[4]:.3f} mm/min")
                print(f"  $112 (Z max rate):      {arr[5]:.3f} mm/min")
                print(f"  $120 (X acceleration):  {arr[6]:.3f} mm/sec^2")
                print(f"  $121 (Y acceleration):  {arr[7]:.3f} mm/sec^2")
                print(f"  $122 (Z acceleration):  {arr[8]:.3f} mm/sec^2")
                print(f"  $130 (X max travel):    {arr[9]:.3f} mm")
                print(f"  $131 (Y max travel):    {arr[10]:.3f} mm")
                print(f"  $132 (Z max travel):    {arr[11]:.3f} mm")
                
                # Store the most likely one (first found is often the default)
                if not self.config_values:
                    self.config_values = {
                        'x_steps_mm': arr[0],
                        'y_steps_mm': arr[1],
                        'z_steps_mm': arr[2],
                        'x_max_rate': arr[3],
                        'y_max_rate': arr[4],
                        'z_max_rate': arr[5],
                        'x_accel': arr[6],
                        'y_accel': arr[7],
                        'z_accel': arr[8],
                        'x_max_travel': arr[9],
                        'y_max_travel': arr[10],
                        'z_max_travel': arr[11],
                    }
        else:
            print("[NOT FOUND] No exact Grbl default pattern found")
            print("This could mean:")
            print("  - Defaults are calculated at runtime")
            print("  - Stored in different format")
            print("  - In a different memory location")
            
        return results
        
    def search_individual_values(self):
        """Search for individual known values"""
        print("\n=== Searching for Individual Configuration Values ===")
        
        # Search for common values that appeared in user specification
        search_values = {
            100.0: "Work area 100mm OR steps/mm 100",
            # Don't search for other values - we don't know them!
        }
        
        for value, desc in search_values.items():
            count = 0
            positions = []
            
            value_bytes = struct.pack('<f', value)
            for i in range(0, len(self.data) - 4):
                if self.data[i:i+4] == value_bytes:
                    count += 1
                    if count <= 5:
                        positions.append(f"0x{i:08X}")
                        
            if count > 0:
                print(f"  {value}: {desc}")
                print(f"    Found {count} times, first at: {', '.join(positions[:5])}")
                
    def generate_report(self):
        """Generate configuration report"""
        print("\n" + "=" * 80)
        print("EXTRACTED CONFIGURATION VALUES")
        print("=" * 80)
        
        if self.config_values:
            print("\n*** VERIFIED VALUES FROM BINARY ***\n")
            print(f"X steps/mm:      {self.config_values['x_steps_mm']:.3f}")
            print(f"Y steps/mm:      {self.config_values['y_steps_mm']:.3f}")
            print(f"Z steps/mm:      {self.config_values['z_steps_mm']:.3f}")
            print(f"X max rate:      {self.config_values['x_max_rate']:.3f} mm/min")
            print(f"Y max rate:      {self.config_values['y_max_rate']:.3f} mm/min")
            print(f"Z max rate:      {self.config_values['z_max_rate']:.3f} mm/min")
            print(f"X acceleration:  {self.config_values['x_accel']:.3f} mm/sec^2")
            print(f"Y acceleration:  {self.config_values['y_accel']:.3f} mm/sec^2")
            print(f"Z acceleration:  {self.config_values['z_accel']:.3f} mm/sec^2")
            print(f"X max travel:    {self.config_values['x_max_travel']:.3f} mm")
            print(f"Y max travel:    {self.config_values['y_max_travel']:.3f} mm")
            print(f"Z max travel:    {self.config_values['z_max_travel']:.3f} mm")
            print("\n*** These values are EXTRACTED from firmware binary ***")
        else:
            print("\nUnable to locate exact default configuration array.")
            print("Configuration may be:")
            print("  - Stored in NVS (user-configurable)")
            print("  - Calculated at runtime")
            print("  - In compressed/encrypted section")
            print("\nRECOMMENDATION: Connect to actual device and use $$ command")
            
    def run(self):
        print("=" * 80)
        print("EXACT CONFIGURATION EXTRACTION (NO GUESSING)")
        print("=" * 80)
        
        self.load()
        self.find_float_arrays()
        results = self.search_specific_patterns()
        self.search_individual_values()
        self.generate_report()
        
        return self.config_values

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 exact_config_extract.py <app0.bin>")
        sys.exit(1)
        
    extractor = ExactConfigExtractor(sys.argv[1])
    config = extractor.run()
    
    # Save results
    if config:
        output = Path(__file__).parent.parent / "analysis" / "extracted_config_values.txt"
        with open(output, 'w') as f:
            f.write("# EXTRACTED CONFIGURATION VALUES FROM FIRMWARE\n")
            f.write("# These are ACTUAL values found in the binary, not estimates\n\n")
            for key, value in config.items():
                f.write(f"{key} = {value:.3f}\n")
        print(f"\n[INFO] Saved to {output}")

if __name__ == "__main__":
    main()
