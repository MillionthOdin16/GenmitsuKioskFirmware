/*
    genmitsu_kiosk_machine.h
    
    Machine definition for Genmitsu Kiosk 2.5W Laser Engraver
    Reverse engineered from firmware binary (C07-251021)
    
    Platform: ESP32
    Controller: Grbl_ESP32
    
    *** IMPORTANT VERIFICATION REQUIRED ***
    
    This configuration is based on binary analysis and must be verified
    with actual hardware before use. Values marked VERIFIED have strong
    evidence from binary. Values marked TBD MUST be determined from hardware.
    
    TO VERIFY: Connect to device via serial and use these commands:
      $$  - View all current settings
      $#  - View coordinate systems and offsets  
      $I  - View build info
    
    2025 - Reverse engineered from binary
*/

#define MACHINE_NAME "GENMITSU_KIOSK"

// ============================================================================
// I2S STEPPER CONFIGURATION - VERIFIED FROM BINARY
// ============================================================================
// The Genmitsu Kiosk uses I2S for step generation (high precision)
// Binary analysis shows GPIO 25, 26, 27 heavily referenced (30+, 34, 27 times)
#define USE_I2S_STEPS

#define I2S_OUT_BCK             GPIO_NUM_25  // VERIFIED: 30 refs in binary
#define I2S_OUT_WS              GPIO_NUM_26  // VERIFIED: 34 refs in binary
#define I2S_OUT_DATA            GPIO_NUM_27  // VERIFIED: 27 refs in binary

// I2S Output mapping (shift register bits) - REQUIRES HARDWARE VERIFICATION
// #define I2S_OUT_X_STEP          ??  // TBD - trace with hardware
// #define I2S_OUT_X_DIR           ??  // TBD - trace with hardware
// #define I2S_OUT_Y_STEP          ??  // TBD - trace with hardware
// #define I2S_OUT_Y_DIR           ??  // TBD - trace with hardware

// ============================================================================
// LIMIT SWITCHES - REQUIRES HARDWARE VERIFICATION
// ============================================================================
// MUST BE DETERMINED FROM HARDWARE - cannot be reliably extracted from binary
// without actual GPIO initialization code analysis

// #define X_LIMIT_PIN             GPIO_NUM_??  // TBD - check with hardware
// #define Y_LIMIT_PIN             GPIO_NUM_??  // TBD - check with hardware
// #define PROBE_PIN               GPIO_NUM_??  // TBD - check with hardware

// ============================================================================
// LASER/SPINDLE CONFIGURATION - PARTIALLY VERIFIED
// ============================================================================
#define SPINDLE_TYPE            SpindleType::PWM

// Laser PWM Output - LIKELY but REQUIRES VERIFICATION
// Binary analysis: GPIO 16 referenced 134 times (strong candidate)
//                  GPIO 17 referenced 48 times (alternate)
// VERIFY with hardware before use!
// #define SPINDLE_OUTPUT_PIN      GPIO_NUM_16  // LIKELY - verify with multimeter
// #define SPINDLE_ENABLE_PIN      GPIO_NUM_??  // TBD - check with hardware

// PWM Configuration - VERIFIED FROM BINARY
// Binary contains 5000Hz at multiple offsets
// 10-bit resolution most common (186 occurrences)
#define DEFAULT_SPINDLE_FREQ    5000  // VERIFIED: found in binary
// Note: Actual resolution determined at runtime by LEDC driver

// ============================================================================
// DEFAULT SETTINGS - CANNOT BE EXTRACTED, USE DEVICE SETTINGS
// ============================================================================
// CRITICAL: Default configuration values are NOT stored as simple constants
// in the binary. They are either:
//   1. Stored in the machine-specific source code (not in binary)
//   2. Calculated at runtime
//   3. Stored in NVS partition (user-configurable)
//
// TO GET ACTUAL VALUES: Connect to device and run $$ command
//
// The values below are PLACEHOLDERS based on typical Grbl defaults.
// THEY MUST BE REPLACED with actual values from your device!

#define DEFAULT_STEP_PULSE_MICROSECONDS 3      // Typical Grbl default
#define DEFAULT_STEPPER_IDLE_LOCK_TIME  250    // Typical Grbl default

#define DEFAULT_STEPPING_INVERT_MASK    0      // TBD - get from $$
#define DEFAULT_DIRECTION_INVERT_MASK   0      // TBD - get from $$
#define DEFAULT_INVERT_ST_ENABLE        0      // TBD - get from $$
#define DEFAULT_INVERT_LIMIT_PINS       1      // Typical Grbl default
#define DEFAULT_INVERT_PROBE_PIN        0      // Typical Grbl default

#define DEFAULT_STATUS_REPORT_MASK      1      // Typical Grbl default

#define DEFAULT_JUNCTION_DEVIATION      0.01   // Typical Grbl default
#define DEFAULT_ARC_TOLERANCE           0.002  // Typical Grbl default
#define DEFAULT_REPORT_INCHES           0      // mm mode

#define DEFAULT_SOFT_LIMIT_ENABLE       0      // Typically disabled initially
#define DEFAULT_HARD_LIMIT_ENABLE       0      // Typically disabled initially

#define DEFAULT_HOMING_ENABLE           0      // TBD - get from $$
#define DEFAULT_HOMING_DIR_MASK         0      // TBD - get from $$
#define DEFAULT_HOMING_FEED_RATE        200.0  // TBD - get from $$ ($24)
#define DEFAULT_HOMING_SEEK_RATE        1000.0 // TBD - get from $$ ($25)
#define DEFAULT_HOMING_DEBOUNCE_DELAY   250    // Typical Grbl default
#define DEFAULT_HOMING_PULLOFF          3.0    // Typical Grbl default

// Laser power range
#define DEFAULT_SPINDLE_RPM_MAX         1000.0 // TBD - get from $$ ($31)
#define DEFAULT_SPINDLE_RPM_MIN         0.0    // TBD - get from $$ ($30)

#define DEFAULT_LASER_MODE              1      // Likely enabled for laser

// ============================================================================
// MOTION PARAMETERS - MUST BE OBTAINED FROM DEVICE
// ============================================================================
// These values are CRITICAL for proper operation and CANNOT be guessed.
// They depend on:
//   - Mechanical configuration (belt pitch, pulley teeth, gear ratios)
//   - Microstepping settings (1, 2, 4, 8, 16, 32 microsteps)
//   - Motor specifications
//   - Physical constraints

// STEPS PER MM - GET FROM DEVICE USING $100, $101, $102
// #define DEFAULT_X_STEPS_PER_MM          ???  // GET FROM $$ command ($100)
// #define DEFAULT_Y_STEPS_PER_MM          ???  // GET FROM $$ command ($101)
// #define DEFAULT_Z_STEPS_PER_MM          ???  // GET FROM $$ command ($102)

// MAX RATES - GET FROM DEVICE USING $110, $111, $112
// #define DEFAULT_X_MAX_RATE              ???  // GET FROM $$ command ($110)
// #define DEFAULT_Y_MAX_RATE              ???  // GET FROM $$ command ($111)
// #define DEFAULT_Z_MAX_RATE              ???  // GET FROM $$ command ($112)

// ACCELERATION - GET FROM DEVICE USING $120, $121, $122
// #define DEFAULT_X_ACCELERATION          ???  // GET FROM $$ command ($120)
// #define DEFAULT_Y_ACCELERATION          ???  // GET FROM $$ command ($121)
// #define DEFAULT_Z_ACCELERATION          ???  // GET FROM $$ command ($122)

// MAX TRAVEL - VERIFIED FROM PRODUCT SPECIFICATIONS
// Genmitsu Kiosk 2.5W official work area: 100mm x 100mm
#define DEFAULT_X_MAX_TRAVEL            100.0  // VERIFIED from product specs
#define DEFAULT_Y_MAX_TRAVEL            100.0  // VERIFIED from product specs
// #define DEFAULT_Z_MAX_TRAVEL            ???  // GET FROM $$ command ($132)

/*
    ============================================================================
    CRITICAL: HOW TO GET ACTUAL CONFIGURATION VALUES
    ============================================================================
    
    1. Connect to your Genmitsu Kiosk via USB serial (115200 baud)
    
    2. Send these commands and save the output:
    
       $$    - Lists all settings with their values
       $#    - Lists work coordinate offsets
       $I    - Lists build info and version
    
    3. The $$ command will show settings like:
       $100=80.000    (X steps/mm)
       $101=80.000    (Y steps/mm)
       $110=5000.000  (X max rate mm/min)
       $111=5000.000  (Y max rate mm/min)
       $120=200.000   (X acceleration mm/sec^2)
       $121=200.000   (Y acceleration mm/sec^2)
       $130=100.000   (X max travel mm)
       $131=100.000   (Y max travel mm)
       ... etc
    
    4. Replace the ??? values above with the actual values from $$
    
    5. For GPIO pins, you may see settings like:
       $Axes/X/StepperEnable/Pin
       $Spindle/OutputPin
       $Spindle/EnablePin
       
       Or examine the PCB to trace connections.
    
    6. Build and test with EXTREME CAUTION:
       - Start with laser power at MINIMUM
       - Verify all limit switches work
       - Test emergency stop
       - Check motion is correct direction
       - Gradually increase speeds/power
    
    ============================================================================
*/

// clang-format on
