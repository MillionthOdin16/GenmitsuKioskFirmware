#!/usr/bin/env python3
"""
Advanced Binary Analysis - GPIO Pin Extraction
Uses pattern matching to find GPIO pin assignments in binary
"""

import sys
import struct
from pathlib import Path
from collections import defaultdict

class GPIOPinAnalyzer:
    """Deep analysis of GPIO pin assignments"""
    
    def __init__(self, binary_path):
        self.binary_path = Path(binary_path)
        self.data = None
        self.gpio_refs = defaultdict(list)
        
    def load(self):
        with open(self.binary_path, 'rb') as f:
            self.data = f.read()
        print(f"[INFO] Loaded {len(self.data):,} bytes")
        
    def find_gpio_constants(self):
        """Find GPIO_NUM_XX values (0-39 for ESP32)"""
        print("\n=== GPIO Number References ===")
        
        # ESP32 has GPIO 0-39
        # Look for these as 32-bit constants
        gpio_usage = defaultdict(int)
        
        for i in range(0, len(self.data) - 4, 4):
            value = struct.unpack('<I', self.data[i:i+4])[0]
            
            # GPIO numbers are small integers (0-39)
            if 0 <= value <= 39:
                # Check if this looks like a GPIO reference
                # by examining surrounding bytes for patterns
                context = self.data[max(0, i-16):i+20]
                
                # Common patterns near GPIO assignments
                if any(marker in context for marker in [
                    b'gpio', b'GPIO', b'pin', b'PIN',
                    b'\x3f\xf4', b'\x3f\xf0',  # GPIO base addresses
                ]):
                    gpio_usage[value] += 1
                    if gpio_usage[value] <= 3:  # Track first few occurrences
                        self.gpio_refs[value].append(i)
        
        print("\nGPIO pins referenced in binary:")
        print(f"{'GPIO':<8} {'Count':<10} {'First Offset'}")
        print("-" * 40)
        
        for gpio in sorted(gpio_usage.keys()):
            if gpio_usage[gpio] > 2:  # Filter noise (only show frequently used)
                offset = self.gpio_refs[gpio][0] if self.gpio_refs[gpio] else 0
                print(f"GPIO_{gpio:<3} {gpio_usage[gpio]:<10} 0x{offset:08X}")
                
        return gpio_usage
        
    def analyze_i2s_pins(self):
        """Analyze I2S pin configuration"""
        print("\n=== I2S Pin Analysis ===")
        
        # Common I2S pins for ESP32
        i2s_candidates = {
            25: "I2S BCK (common)",
            26: "I2S WS (common)",
            27: "I2S DATA (common)",
        }
        
        for gpio, desc in i2s_candidates.items():
            if gpio in self.gpio_refs:
                print(f"  GPIO_{gpio}: {desc} - {len(self.gpio_refs[gpio])} refs")
                
    def analyze_pwm_candidates(self):
        """Find likely PWM pins for laser"""
        print("\n=== PWM/Laser Pin Candidates ===")
        
        # Common PWM-capable pins used for laser control
        pwm_candidates = {
            4: "GPIO_4 (common PWM)",
            16: "GPIO_16 (common PWM)",
            17: "GPIO_17 (common PWM)",
            18: "GPIO_18 (common PWM)",
            19: "GPIO_19 (common PWM)",
            21: "GPIO_21 (common PWM)",
            22: "GPIO_22 (common PWM)",
            23: "GPIO_23 (common PWM)",
        }
        
        for gpio, desc in pwm_candidates.items():
            if gpio in self.gpio_refs:
                print(f"  {desc} - {len(self.gpio_refs[gpio])} refs")
                
    def find_ledc_config(self):
        """Find LEDC (PWM) configuration"""
        print("\n=== LEDC/PWM Configuration Search ===")
        
        # LEDC frequency values (common for laser)
        common_freqs = [1000, 2000, 5000, 10000, 20000]
        
        for i in range(0, len(self.data) - 4, 4):
            value = struct.unpack('<I', self.data[i:i+4])[0]
            if value in common_freqs:
                print(f"  Found {value} Hz at offset 0x{i:08X}")
                
        # PWM resolution (8, 10, 12, 13 bits common)
        print("\n  Common PWM resolutions found:")
        for res in [8, 10, 12, 13]:
            count = 0
            for i in range(0, len(self.data) - 4, 4):
                value = struct.unpack('<I', self.data[i:i+4])[0]
                if value == res:
                    count += 1
            if count > 5:
                print(f"    {res}-bit: {count} occurrences")
                
    def extract_step_resolution(self):
        """Extract stepper motor steps/mm values"""
        print("\n=== Stepper Configuration ===")
        
        # Common steps/mm values for belt-driven systems
        common_steps = [40.0, 50.0, 80.0, 100.0, 160.0, 200.0]
        
        found = {}
        for val in common_steps:
            for i in range(0, len(self.data) - 4, 4):
                try:
                    fval = struct.unpack('<f', self.data[i:i+4])[0]
                    if abs(fval - val) < 0.01:
                        if val not in found:
                            found[val] = 0
                        found[val] += 1
                except:
                    pass
                    
        print("  Likely steps/mm values:")
        for val, count in sorted(found.items()):
            if count > 1 and count < 20:
                print(f"    {val:6.1f} steps/mm - {count} occurrences")
                
    def run_analysis(self):
        """Run all analyses"""
        print("=" * 70)
        print("ADVANCED GPIO & CONFIGURATION ANALYSIS")
        print("=" * 70)
        
        self.load()
        gpio_usage = self.find_gpio_constants()
        self.analyze_i2s_pins()
        self.analyze_pwm_candidates()
        self.find_ledc_config()
        self.extract_step_resolution()
        
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        
        return gpio_usage

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_gpio_analysis.py <binary>")
        sys.exit(1)
        
    analyzer = GPIOPinAnalyzer(sys.argv[1])
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
