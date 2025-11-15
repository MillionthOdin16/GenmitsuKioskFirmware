# Web Interface Setup Guide for Genmitsu Kiosk

## Problem Description

The Genmitsu Kiosk firmware has an empty SPIFFS partition, which means the web interface files are missing. You're seeing a fallback page that says "index file is missing."

## Web Interface Architecture

Grbl_ESP32 uses a two-tier web interface system:

1. **Primary Interface**: Stored in SPIFFS partition
   - Full-featured web UI
   - Files: `index.html.gz`, `favicon.ico`
   - Located in SPIFFS filesystem on flash

2. **Fallback Interface**: Embedded in firmware
   - Basic interface when SPIFFS is empty
   - Compiled into the binary (NoFile.h)
   - Limited functionality

## Current State

Your device:
- ✓ Has web server running
- ✓ Has fallback interface active
- ✗ Missing SPIFFS files (partition is empty in dump)

## Solution: Upload Web Interface Files

### Method 1: Upload via Web Interface (Easiest)

If you can access the current fallback page:

1. **Connect to device WiFi**:
   - SSID: `Genmitsu_Kiosk_C_V07` or `Genmitsu_Kiosk_V07`
   - Default IP: `http://192.168.0.1`

2. **Access upload page**:
   - Go to `http://192.168.0.1/files`
   - This should show file management interface

3. **Upload required files**:
   - Download from Grbl_ESP32: https://github.com/bdring/Grbl_Esp32
   - Files needed from `Grbl_Esp32/data/`:
     - `index.html.gz` (main interface - 114KB)
     - `favicon.ico` (optional - 1.2KB)

4. **Upload process**:
   ```
   Navigate to: http://192.168.0.1/files
   Click "Upload" or similar button
   Select index.html.gz
   Wait for upload to complete
   Refresh the main page
   ```

### Method 2: Upload via Serial Commands (If Web Upload Doesn't Work)

1. **Connect via USB serial** (115200 baud)

2. **Check SPIFFS status**:
   ```
   [ESP220]
   ```
   This shows SPIFFS information

3. **Upload files via ESPWebUI commands**:
   Unfortunately, Grbl_ESP32 doesn't support file upload via serial.
   You'll need to use Method 3 or Method 4.

### Method 3: Flash SPIFFS Partition Directly

**Requirements**:
- esptool.py installed
- index.html.gz and favicon.ico files
- mkspiffs tool

**Steps**:

1. **Get the web interface files**:
   ```bash
   git clone https://github.com/bdring/Grbl_Esp32.git
   cd Grbl_Esp32/Grbl_Esp32/data
   # Files are here: index.html.gz, favicon.ico
   ```

2. **Create SPIFFS image**:
   ```bash
   # Install mkspiffs
   # Download from: https://github.com/igrr/mkspiffs/releases
   
   # Create SPIFFS image (192KB size for Genmitsu Kiosk)
   mkspiffs -c ./data -b 4096 -p 256 -s 196608 spiffs.bin
   ```

3. **Flash SPIFFS partition**:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
       write_flash 0x3D0000 spiffs.bin
   ```

4. **Restart device**:
   - Power cycle or send reset command
   - Access web interface at `http://192.168.0.1`

### Method 4: Include in Custom Firmware Build

When building custom firmware:

1. **Place files in data directory**:
   ```
   Grbl_Esp32/
   └── Grbl_Esp32/
       └── data/
           ├── index.html.gz
           └── favicon.ico
   ```

2. **Build with PlatformIO**:
   ```bash
   # This automatically creates and uploads SPIFFS
   pio run -t uploadfs
   
   # Then upload firmware
   pio run -t upload
   ```

## Web Interface Features

Once properly installed, the Grbl_ESP32 web interface provides:

### Main Features:
- **G-code Upload & Execution**: Send files to run
- **Jog Controls**: Move axes manually
- **Real-time Status**: Position, state, buffer status
- **Settings Management**: View and modify $ settings
- **File Management**: SPIFFS file browser
- **Console**: Direct G-code command input
- **WiFi Configuration**: Change network settings
- **Firmware Upload**: OTA updates

### Interface Layout:
```
┌─────────────────────────────────────────┐
│ Grbl_ESP32 Web Interface                │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌──────────┐ ┌───────────┐ │
│ │  JOG    │ │  CONSOLE │ │  FILES    │ │
│ │ Controls│ │ G-code   │ │ Manager   │ │
│ └─────────┘ └──────────┘ └───────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Status: Idle                        │ │
│ │ Position: X:0.00 Y:0.00 Z:0.00      │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Settings | WiFi | System            │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Accessing Different Interface Sections

Once web interface is working:

### Main Dashboard:
```
http://192.168.0.1/
```

### File Manager:
```
http://192.168.0.1/files
```

### Settings:
Access via interface buttons or:
```
Send $$ command in console
```

### WiFi Configuration:
Access via interface or commands:
```
[ESP100]  - Show WiFi mode
[ESP105]  - Show SSID
[ESP110]  - Show AP SSID
```

## Troubleshooting

### Problem: Can't Access http://192.168.0.1

**Solutions**:
1. Check you're connected to device WiFi (not your home network)
2. Try http://grbl_esp32.local (mDNS)
3. Check WiFi is in AP mode: Connect via serial, send `[ESP100]`

### Problem: Upload Fails

**Solutions**:
1. File might be too large (should be <192KB for SPIFFS)
2. SPIFFS might not be mounted
3. Try direct flash method (Method 3)

### Problem: Interface Loads But Looks Broken

**Solutions**:
1. Clear browser cache
2. Try different browser
3. Check console for JavaScript errors
4. Verify index.html.gz is complete (should be ~114KB)

### Problem: "Forbidden" or "Access Denied"

**Solutions**:
1. Authentication might be enabled
2. Default credentials (if set): admin/admin
3. Disable auth via settings

## Getting Web Interface Files

### Option 1: From GitHub (Recommended)
```bash
wget https://github.com/bdring/Grbl_Esp32/raw/master/Grbl_Esp32/data/index.html.gz
wget https://github.com/bdring/Grbl_Esp32/raw/master/Grbl_Esp32/data/favicon.ico
```

### Option 2: Clone Repository
```bash
git clone https://github.com/bdring/Grbl_Esp32.git
cd Grbl_Esp32/Grbl_Esp32/data
# Files are here
```

### Option 3: Build from Source
The web interface is actually based on ESP3D-WEBUI:
```bash
git clone https://github.com/luc-github/ESP3D-WEBUI.git
# Follow build instructions
# Generates index.html.gz
```

## SPIFFS Partition Information

For Genmitsu Kiosk (from firmware analysis):

```
Partition: spiffs
Type: data (0x01)
Subtype: spiffs (0x82)
Offset: 0x3D0000 (3,993,600 bytes from start)
Size: 196,608 bytes (192 KB)
```

**Files that fit**:
- index.html.gz: ~114KB ✓
- favicon.ico: ~1.2KB ✓
- Custom GCode files: ~70KB available
- Total: ~185KB usable

## Advanced: Creating Custom Web Interface

If you want to modify the interface:

1. **Get ESP3D-WEBUI source**:
   ```bash
   git clone https://github.com/luc-github/ESP3D-WEBUI.git
   ```

2. **Modify HTML/CSS/JS** in the source

3. **Build**:
   ```bash
   npm install
   npm run build-embedded
   ```

4. **Result**: Creates `index.html.gz`

5. **Upload** using one of the methods above

## Security Considerations

### Default Setup:
- No authentication by default
- Anyone on WiFi can control machine
- HTTP only (not HTTPS)

### To Enable Security:
1. **Enable authentication**:
   ```
   [ESP555]P=admin T=ADMIN
   ```

2. **Set password**:
   ```
   [ESP555]P=newpassword T=USER
   ```

3. **Use WPA2** on WiFi AP (already enabled)

## Recommended Setup Sequence

1. ✓ Connect to device WiFi
2. ✓ Access http://192.168.0.1
3. ✓ Upload index.html.gz via /files page
4. ✓ Upload favicon.ico
5. ✓ Refresh main page
6. ✓ Full interface should now load
7. ✓ Configure WiFi to connect to your network
8. ✓ Set authentication if desired
9. ✓ Test all functions (jog, console, file upload)
10. ✓ Bookmark the IP address

## Alternative: Use Serial Console Only

If web interface is not critical:

- All functions available via serial (115200 baud)
- Send G-code directly
- Use $ commands for settings
- Simpler, more reliable for some users

Commands:
```
$$          - View settings
$I          - Build info
$G          - Parser state
$X          - Unlock
$H          - Home
G0 X10      - Move
M3 S500     - Laser on (50% power)
M5          - Laser off
```

## Summary

**Quickest Solution**:
1. Download index.html.gz from GitHub
2. Access http://192.168.0.1/files
3. Upload index.html.gz
4. Reload main page

**Most Reliable**:
1. Use Method 3 (flash SPIFFS directly)
2. Ensures clean installation
3. Works even if web upload is broken

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Ready to use
