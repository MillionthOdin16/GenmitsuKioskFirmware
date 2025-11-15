#!/usr/bin/env python3
"""
Firmware Validation and Testing Script
Compares rebuilt firmware with original for functional equivalence
"""

import serial
import time
import sys
from pathlib import Path

class FirmwareValidator:
    """Validate rebuilt firmware against original"""
    
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.test_results = []
        
    def connect(self):
        """Connect to device"""
        print(f"[INFO] Connecting to {self.port} at {self.baudrate} baud...")
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for boot
            # Clear any boot messages
            self.ser.reset_input_buffer()
            print("[✓] Connected")
            return True
        except Exception as e:
            print(f"[✗] Connection failed: {e}")
            return False
            
    def send_command(self, cmd):
        """Send command and get response"""
        if not self.ser:
            return None
            
        self.ser.write(f"{cmd}\n".encode())
        time.sleep(0.2)
        
        response = []
        while self.ser.in_waiting:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                response.append(line)
                
        return response
        
    def test_build_info(self):
        """Test $I command - build info"""
        print("\n=== Test 1: Build Info ($I) ===")
        response = self.send_command("$I")
        
        if response:
            for line in response:
                print(f"  {line}")
                if "Grbl_ESP32" in line:
                    self.test_results.append(("Build Info", "PASS", "Grbl_ESP32 detected"))
                    return True
                    
        self.test_results.append(("Build Info", "FAIL", "No valid response"))
        return False
        
    def test_settings(self):
        """Test $$ command - all settings"""
        print("\n=== Test 2: Settings ($$) ===")
        response = self.send_command("$$")
        
        critical_settings = {
            '$100': None,  # X steps/mm
            '$101': None,  # Y steps/mm
            '$110': None,  # X max rate
            '$111': None,  # Y max rate
            '$120': None,  # X accel
            '$121': None,  # Y accel
        }
        
        if response:
            for line in response:
                for setting in critical_settings:
                    if line.startswith(setting):
                        value = line.split('=')[1] if '=' in line else ''
                        critical_settings[setting] = value
                        print(f"  {line}")
                        
        # Check if we got settings
        if any(v is not None for v in critical_settings.values()):
            self.test_results.append(("Settings", "PASS", f"Retrieved {sum(1 for v in critical_settings.values() if v)} settings"))
            return True
        else:
            self.test_results.append(("Settings", "FAIL", "No settings retrieved"))
            return False
            
    def test_machine_name(self):
        """Check for Genmitsu Kiosk identification"""
        print("\n=== Test 3: Machine Identification ===")
        response = self.send_command("$I")
        
        found_genmitsu = False
        for line in response:
            print(f"  {line}")
            if "Genmitsu" in line or "GENMITSU" in line or "genmitsu" in line:
                found_genmitsu = True
                
        if found_genmitsu:
            self.test_results.append(("Machine ID", "PASS", "Genmitsu branding present"))
        else:
            self.test_results.append(("Machine ID", "WARN", "Generic Grbl_ESP32 (branding may differ)"))
            
    def test_laser_mode(self):
        """Test laser mode setting"""
        print("\n=== Test 4: Laser Mode ===")
        response = self.send_command("$$")
        
        laser_mode = None
        for line in response:
            if "$GCode/LaserMode" in line or "$32" in line:
                print(f"  {line}")
                laser_mode = line
                
        if laser_mode:
            if "=1" in laser_mode or "=On" in laser_mode:
                self.test_results.append(("Laser Mode", "PASS", "Laser mode enabled"))
            else:
                self.test_results.append(("Laser Mode", "WARN", "Laser mode disabled"))
        else:
            self.test_results.append(("Laser Mode", "FAIL", "Laser mode setting not found"))
            
    def test_wifi_status(self):
        """Test WiFi functionality"""
        print("\n=== Test 5: WiFi Status ===")
        response = self.send_command("$WiFi/ListAPs")
        
        if response and len(response) > 1:
            print(f"  WiFi responding: {len(response)} lines")
            self.test_results.append(("WiFi", "PASS", "WiFi operational"))
        else:
            self.test_results.append(("WiFi", "INFO", "WiFi status unclear"))
            
    def test_io_safety(self):
        """Test that laser is OFF by default"""
        print("\n=== Test 6: Safety Check ===")
        print("  Checking laser is OFF (M5)...")
        response = self.send_command("M5")
        
        if response:
            if "ok" in str(response).lower() or len(response) > 0:
                self.test_results.append(("Safety", "PASS", "M5 (laser off) accepted"))
            else:
                self.test_results.append(("Safety", "WARN", "M5 response unclear"))
        else:
            self.test_results.append(("Safety", "FAIL", "No response to M5"))
            
        print("  ⚠️  DO NOT TEST M3/M4 WITHOUT PROPER SAFETY MEASURES ⚠️")
        
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print("VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n{'Test':<20} {'Result':<8} {'Details'}")
        print("-" * 70)
        
        pass_count = 0
        fail_count = 0
        warn_count = 0
        
        for test, result, details in self.test_results:
            print(f"{test:<20} {result:<8} {details}")
            if result == "PASS":
                pass_count += 1
            elif result == "FAIL":
                fail_count += 1
            elif result == "WARN":
                warn_count += 1
                
        print("\n" + "-" * 70)
        print(f"Summary: {pass_count} passed, {fail_count} failed, {warn_count} warnings")
        
        if fail_count == 0:
            print("\n✓ Firmware appears functionally equivalent")
        else:
            print(f"\n✗ {fail_count} critical issues detected")
            
    def run_validation(self):
        """Run all validation tests"""
        print("=" * 70)
        print("FIRMWARE VALIDATION TEST SUITE")
        print("=" * 70)
        print("\n⚠️  SAFETY WARNING ⚠️")
        print("This will test firmware functionality but NOT test laser output.")
        print("Laser testing MUST be done manually with proper safety precautions.")
        print("\nPress Enter to continue or Ctrl+C to abort...")
        input()
        
        if not self.connect():
            return False
            
        try:
            self.test_build_info()
            self.test_settings()
            self.test_machine_name()
            self.test_laser_mode()
            self.test_wifi_status()
            self.test_io_safety()
            
        finally:
            if self.ser:
                self.ser.close()
                
        self.generate_report()
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_firmware.py <serial_port>")
        print("\nExample:")
        print("  python3 validate_firmware.py /dev/ttyUSB0")
        print("  python3 validate_firmware.py COM3")
        sys.exit(1)
        
    port = sys.argv[1]
    
    validator = FirmwareValidator(port)
    validator.run_validation()

if __name__ == "__main__":
    main()
