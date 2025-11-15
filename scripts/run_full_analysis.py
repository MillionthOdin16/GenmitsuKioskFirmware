#!/usr/bin/env python3
"""
Complete Firmware Analysis Workflow
Runs all analysis tools in sequence
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results"""
    print("\n" + "=" * 80)
    print(f"Running: {description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_full_analysis.py <firmware.bin>")
        print("\nThis script runs all analysis tools in sequence:")
        print("  1. Firmware structure analysis")
        print("  2. String extraction")
        print("  3. Partition parsing and extraction")
        print("\nExample:")
        print("  python3 run_full_analysis.py firmware/genmitsu_kiosk.bin")
        sys.exit(1)
        
    firmware_path = Path(sys.argv[1])
    
    if not firmware_path.exists():
        print(f"[ERROR] Firmware file not found: {firmware_path}")
        sys.exit(1)
        
    print("=" * 80)
    print("ESP32 FIRMWARE COMPLETE ANALYSIS")
    print("=" * 80)
    print(f"\nTarget: {firmware_path}")
    print(f"Size: {firmware_path.stat().st_size:,} bytes")
    
    scripts_dir = Path(__file__).parent
    
    # Step 1: Main firmware analysis
    cmd = f"python3 {scripts_dir}/analyze_firmware.py {firmware_path}"
    if not run_command(cmd, "Firmware Structure Analysis"):
        print("[WARNING] Firmware analysis had issues")
        
    # Step 2: String extraction
    cmd = f"python3 {scripts_dir}/extract_strings.py {firmware_path}"
    if not run_command(cmd, "String Extraction"):
        print("[WARNING] String extraction had issues")
        
    # Step 3: Partition parsing with extraction
    cmd = f"python3 {scripts_dir}/parse_partitions.py {firmware_path} --extract"
    if not run_command(cmd, "Partition Analysis and Extraction"):
        print("[WARNING] Partition parsing had issues")
        
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nResults saved to:")
    print("  - analysis/")
    print("    ├── *_analysis.txt      (Firmware structure analysis)")
    print("    ├── *_strings.txt       (Extracted strings)")
    print("    └── partitions/         (Extracted partition files)")
    print("\nNext steps:")
    print("  1. Review analysis reports in the analysis/ directory")
    print("  2. Use Ghidra or radare2 to decompile extracted partitions")
    print("  3. Analyze strings for WiFi credentials, API endpoints, etc.")
    print("  4. Document findings in docs/FINDINGS.md")

if __name__ == "__main__":
    main()
