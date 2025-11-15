#!/bin/bash
# Download and prepare Grbl_ESP32 web interface files

set -e

echo "=============================================="
echo "Grbl_ESP32 Web Interface Downloader"
echo "=============================================="
echo ""

# Create directory for web files
WEB_DIR="web_interface"
mkdir -p "$WEB_DIR"

echo "[1/4] Downloading index.html.gz..."
wget -q -O "$WEB_DIR/index.html.gz" \
    "https://raw.githubusercontent.com/bdring/Grbl_Esp32/master/Grbl_Esp32/data/index.html.gz"

echo "[2/4] Downloading favicon.ico..."
wget -q -O "$WEB_DIR/favicon.ico" \
    "https://raw.githubusercontent.com/bdring/Grbl_Esp32/master/Grbl_Esp32/data/favicon.ico"

echo "[3/4] Verifying downloads..."
if [ -f "$WEB_DIR/index.html.gz" ]; then
    SIZE=$(stat -f%z "$WEB_DIR/index.html.gz" 2>/dev/null || stat -c%s "$WEB_DIR/index.html.gz" 2>/dev/null)
    echo "   index.html.gz: $SIZE bytes (should be ~114KB)"
else
    echo "   ERROR: index.html.gz not downloaded!"
    exit 1
fi

if [ -f "$WEB_DIR/favicon.ico" ]; then
    SIZE=$(stat -f%z "$WEB_DIR/favicon.ico" 2>/dev/null || stat -c%s "$WEB_DIR/favicon.ico" 2>/dev/null)
    echo "   favicon.ico: $SIZE bytes (should be ~1.2KB)"
else
    echo "   ERROR: favicon.ico not downloaded!"
    exit 1
fi

echo "[4/4] Creating upload instructions..."
cat > "$WEB_DIR/UPLOAD_INSTRUCTIONS.txt" << 'EOF'
Web Interface Upload Instructions
==================================

FILES IN THIS DIRECTORY:
  - index.html.gz   (Main web interface)
  - favicon.ico     (Browser icon)

METHOD 1: Upload via Web Interface
-----------------------------------
1. Connect to Genmitsu Kiosk WiFi
   SSID: Genmitsu_Kiosk_C_V07 (or similar)

2. Open browser and go to:
   http://192.168.0.1/files

3. Click upload button

4. Select index.html.gz

5. Upload favicon.ico (optional)

6. Go to http://192.168.0.1
   - Full interface should now load!

METHOD 2: Flash SPIFFS Directly
--------------------------------
Requires: esptool, mkspiffs

1. Create SPIFFS image:
   mkspiffs -c . -b 4096 -p 256 -s 196608 spiffs.bin

2. Flash to device:
   esptool.py --chip esp32 --port /dev/ttyUSB0 \
       write_flash 0x3D0000 spiffs.bin

3. Restart device

METHOD 3: Include in Custom Build
----------------------------------
1. Copy files to Grbl_Esp32/Grbl_Esp32/data/

2. Build with PlatformIO:
   pio run -t uploadfs

For detailed instructions, see:
docs/WEB_INTERFACE_SETUP.md
EOF

echo ""
echo "=============================================="
echo "SUCCESS!"
echo "=============================================="
echo ""
echo "Files downloaded to: $WEB_DIR/"
echo ""
echo "Next steps:"
echo "  1. Read: $WEB_DIR/UPLOAD_INSTRUCTIONS.txt"
echo "  2. Connect to device WiFi"
echo "  3. Upload index.html.gz via http://192.168.0.1/files"
echo ""
echo "For detailed guide: docs/WEB_INTERFACE_SETUP.md"
echo ""
