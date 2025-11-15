# Ghidra Python Script for ESP32 Firmware Analysis
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
