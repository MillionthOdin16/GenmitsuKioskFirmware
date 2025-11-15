# Laser Cutting and Engraving Parameters Guide
## Genmitsu Kiosk 2.5W (445nm Blue Diode Laser)

**Last Updated**: November 2025  
**Firmware Version**: Grbl_ESP32 v1.3a  
**Laser Specifications**:
- Power: 2.5W optical output (445nm blue diode)
- Wavelength: 445nm (blue light - optimal for dark materials)
- Focus: ~0.1mm spot size
- Work Area: 100mm × 100mm
- Max Speed: 12,000 mm/min (200 mm/sec)
- PWM Control: 0-1000 (S0-S1000 in G-code)

---

## Table of Contents
1. [Safety Guidelines](#safety-guidelines)
2. [Understanding Laser Parameters](#understanding-laser-parameters)
3. [Material Database](#material-database)
4. [Advanced Techniques](#advanced-techniques)
5. [Troubleshooting](#troubleshooting)
6. [Quick Reference Chart](#quick-reference-chart)

---

## Safety Guidelines

### CRITICAL SAFETY REQUIREMENTS

**Before Every Operation**:
- ✅ Wear OD6+ 445nm laser safety glasses (orange/amber lenses)
- ✅ Ensure safety door/lid is functional and closed
- ✅ Verify adequate ventilation or fume extraction
- ✅ Keep fire extinguisher (Class A/B) within reach
- ✅ Never leave laser unattended during operation
- ✅ Test focus and power on scrap material first

**Never Laser These Materials** (Toxic/Dangerous):
- ❌ PVC, Vinyl (releases chlorine gas - deadly)
- ❌ ABS plastic (releases cyanide)
- ❌ Polycarbonate (releases bisphenol A)
- ❌ Fiberglass (releases particles)
- ❌ Coated/treated wood (unknown chemicals)
- ❌ Any material containing halogens

**Fire Hazards** (Extra Caution Required):
- 🔥 Paper (can ignite - use low power, high speed)
- 🔥 Cardboard (monitor for embers)
- 🔥 Fabric (especially synthetic)
- 🔥 Cork (smolders easily)

---

## Understanding Laser Parameters

### Key Parameters Explained

**1. Power (S Value in G-code)**
- Range: S0 to S1000 (0% to 100%)
- S250 = 25% power = ~0.625W
- S500 = 50% power = ~1.25W
- S1000 = 100% power = ~2.5W
- **Start low** (S200-S300) and increase gradually

**2. Speed (F Value in G-code)**
- Range: 1 to 12,000 mm/min
- Typical engraving: 1,000-3,000 mm/min
- Typical cutting: 100-800 mm/min
- **Slower = More heat = Deeper cut**
- **Faster = Less heat = Lighter engraving**

**3. Passes**
- Number of times laser traces the same path
- 1 pass: Light engraving
- 2-3 passes: Medium depth
- 4+ passes: Deep cutting (better than slow speed)

**4. Focus Distance**
- Optimal: Material surface to focal point = 0mm
- For engraving: Focus ON surface (sharpest line)
- For cutting: Focus 1-2mm ABOVE surface (deeper penetration)
- Adjust with focus gauge or paper method

**5. DPI (Dots Per Inch) for Image Engraving**
- 254 DPI: High quality photos (slow)
- 300 DPI: Professional quality (very slow)
- 170 DPI: Good balance (recommended)
- 127 DPI: Fast, acceptable quality
- 85 DPI: Draft/testing

---

## Material Database

### 🌲 WOOD & WOOD PRODUCTS

#### Basswood / Balsa (Lightest Woods)
**Best for**: Fine detail engraving, cutting, 3D engraving

**Engraving**:
- Speed: 2,500-3,500 mm/min
- Power: S150-S250 (15-25%)
- Passes: 1-2
- Focus: On surface
- Result: Light brown contrast
- Notes: Easiest to engrave, minimal charring

**Cutting (1-3mm thick)**:
- Speed: 300-600 mm/min
- Power: S400-S600 (40-60%)
- Passes: 2-4
- Focus: 1mm above surface
- Notes: Clean cuts, minimal smoke

#### Plywood (3-ply, Birch/Maple)
**Best for**: Structural parts, boxes, decorative items

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S200-S350 (20-35%)
- Passes: 1-2
- Focus: On surface
- Notes: May show grain patterns

**Cutting**:
- 1.5mm: 400 mm/min, S500, 3-4 passes
- 3mm: 200 mm/min, S700, 5-7 passes
- 4mm: 150 mm/min, S800-S900, 8-12 passes
- Focus: 1-2mm above surface
- Notes: May not cut through all plies evenly; check adhesive type

#### Oak / Hardwoods
**Best for**: Durable items, deep engraving

**Engraving**:
- Speed: 1,500-2,500 mm/min
- Power: S300-S450 (30-45%)
- Passes: 2-3
- Focus: On surface
- Result: Deep brown, excellent contrast
- Notes: Grain affects consistency

**Cutting (1-2mm)**:
- Speed: 200-400 mm/min
- Power: S600-S800 (60-80%)
- Passes: 4-8
- Notes: Difficult with 2.5W, consider multiple passes

#### MDF (Medium Density Fiberboard)
**Best for**: Testing, flat surfaces, no grain

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S200-S300 (20-30%)
- Passes: 1-2
- Notes: Uniform results, some smoke

**Cutting (3mm)**:
- Speed: 300-500 mm/min
- Power: S600-S800 (60-80%)
- Passes: 4-6
- Notes: Check if MDF is laser-safe (some contain formaldehyde)

#### Cork
**Best for**: Coasters, stamps, decorative

**Engraving**:
- Speed: 3,000-4,000 mm/min
- Power: S150-S250 (15-25%)
- Passes: 1
- Notes: Burns easily, go light

**Cutting (2-3mm)**:
- Speed: 400-600 mm/min
- Power: S400-S500 (40-50%)
- Passes: 2-3
- Notes: Fire hazard - monitor closely

---

### 📄 PAPER & CARDBOARD

#### Paper (Copy/Printer Paper)
**Best for**: Invitations, art, templates

**Engraving/Scoring**:
- Speed: 5,000-8,000 mm/min
- Power: S50-S150 (5-15%)
- Passes: 1
- Focus: On surface
- Notes: Use lowest power to avoid ignition

**Cutting (80-100gsm)**:
- Speed: 3,000-5,000 mm/min
- Power: S100-S200 (10-20%)
- Passes: 1-2
- Notes: HIGH FIRE RISK - never leave unattended

#### Cardstock (200-300gsm)
**Best for**: Business cards, tags, models

**Engraving**:
- Speed: 3,000-4,000 mm/min
- Power: S100-S200 (10-20%)
- Passes: 1

**Cutting**:
- Speed: 1,500-2,500 mm/min
- Power: S250-S400 (25-40%)
- Passes: 2-3

#### Cardboard (Corrugated)
**Best for**: Prototypes, packaging, models

**Engraving**:
- Speed: 2,500-3,500 mm/min
- Power: S150-S250 (15-25%)
- Passes: 1

**Cutting (2-4mm)**:
- Speed: 600-1,000 mm/min
- Power: S400-S600 (40-60%)
- Passes: 3-5
- Notes: Air gaps in corrugation may affect quality

---

### 🎨 LEATHER & FABRIC

#### Genuine Leather (Vegetable Tanned)
**Best for**: Wallets, belts, patches, art

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S200-S350 (20-35%)
- Passes: 1-2
- Focus: On surface
- Result: Light brown to dark brown
- Notes: Beautiful contrast, pleasant smell

**Cutting (1-2mm)**:
- Speed: 400-800 mm/min
- Power: S500-S700 (50-70%)
- Passes: 2-3
- Notes: Check leather type - no chrome-tanned

#### Synthetic Leather / Faux Leather
**Best for**: Similar to genuine leather

**Engraving**:
- Speed: 2,500-3,500 mm/min
- Power: S150-S250 (15-25%)
- Passes: 1
- Notes: Test first - some contain PVC (dangerous!)

**Cutting**:
- Speed: 600-1,000 mm/min
- Power: S400-S600 (40-60%)
- Passes: 2-3

#### Cotton Fabric (Natural)
**Best for**: Patches, clothing decoration

**Engraving**:
- Speed: 3,000-5,000 mm/min
- Power: S100-S200 (10-20%)
- Passes: 1
- Notes: Creates brown/tan marks, may char edges

**Cutting**:
- Speed: 1,500-2,500 mm/min
- Power: S250-S400 (25-40%)
- Passes: 1-2
- Notes: Edges will seal (useful to prevent fraying)

#### Felt
**Best for**: Crafts, patches, decorations

**Engraving**:
- Speed: 3,500-4,500 mm/min
- Power: S100-S200 (10-20%)
- Passes: 1

**Cutting (2-3mm)**:
- Speed: 800-1,200 mm/min
- Power: S300-S500 (30-50%)
- Passes: 1-2
- Notes: Clean cuts, sealed edges

#### Denim
**Best for**: Personalization, art on jeans

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S250-S400 (25-40%)
- Passes: 1-2
- Notes: Creates light blue/white contrast on dark denim

---

### 🎨 PLASTICS (Safe Types Only)

#### Acrylic (PMMA / Plexiglas)
**Best for**: Signs, jewelry, decorative items

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S200-S350 (20-35%)
- Passes: 1-2
- Focus: On surface
- Result: White/frosted appearance
- Notes: Excellent for signs, high contrast

**Cutting (1-3mm)**:
- 1mm: 800 mm/min, S600, 2-3 passes
- 2mm: 500 mm/min, S700-S800, 4-6 passes
- 3mm: 300 mm/min, S800-S900, 6-10 passes
- Focus: 1mm above surface
- Notes: May require multiple passes, flame-polished edges

**Color Notes**:
- Clear acrylic: Engraves white/frosted
- Black acrylic: Engraves gray/white (excellent contrast)
- Colored acrylic: Engraves lighter shade of same color

#### Delrin (POM / Acetal)
**Best for**: Gears, mechanical parts, stamps

**Engraving**:
- Speed: 2,500-3,500 mm/min
- Power: S300-S450 (30-45%)
- Passes: 1-2
- Result: White/light gray on black

**Cutting (1-2mm)**:
- Speed: 400-600 mm/min
- Power: S600-S800 (60-80%)
- Passes: 3-5
- Notes: Durable, low friction material

---

### 🖼️ COATED MATERIALS

#### Anodized Aluminum
**Best for**: Tags, nameplates, jewelry

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S600-S900 (60-90%)
- Passes: 1-2
- Focus: On surface
- Result: Removes anodizing, reveals bare aluminum
- Notes: Black anodized works best (high contrast)

**Limitations**:
- Cannot cut metal with 2.5W laser
- Only removes coating/anodization
- Bare aluminum does not engrave

#### Powder-Coated Metal
**Best for**: Tools, signs, industrial marking

**Engraving**:
- Speed: 1,500-2,500 mm/min
- Power: S700-S900 (70-90%)
- Passes: 2-3
- Result: Removes powder coating, reveals metal
- Notes: Dark coatings work best

#### Painted Wood/Metal
**Best for**: Selective paint removal, signs

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S300-S600 (30-60%)
- Passes: 1-2
- Notes: Varies by paint type - test first

---

### 🍃 NATURAL MATERIALS

#### Cork
**Best for**: Coasters, trivets, decorative items

**Engraving**:
- Speed: 3,000-4,000 mm/min
- Power: S150-S250 (15-25%)
- Passes: 1
- Notes: Natural texture shows through

**Cutting (3-5mm)**:
- Speed: 400-600 mm/min
- Power: S500-S700 (50-70%)
- Passes: 3-5
- Notes: Smolders - monitor closely

#### Bamboo
**Best for**: Eco-friendly products, cutting boards

**Engraving**:
- Speed: 2,000-3,000 mm/min
- Power: S250-S400 (25-40%)
- Passes: 1-2
- Result: Dark brown, beautiful contrast
- Notes: Grain direction affects results

**Cutting (2-4mm)**:
- Speed: 300-600 mm/min
- Power: S600-S800 (60-80%)
- Passes: 4-8

#### Stone (Marble, Granite, Slate)
**Best for**: Coasters, plaques, memorials

**Engraving on Polished Stone**:
- Speed: 1,000-2,000 mm/min
- Power: S800-S1000 (80-100%)
- Passes: 2-4
- Focus: On surface
- Result: Light frosting (subtle)
- Notes: Works best on dark, polished stone

**Engraving on Slate**:
- Speed: 1,500-2,500 mm/min
- Power: S700-S900 (70-90%)
- Passes: 2-3
- Result: Better contrast than polished stone

**Limitations**:
- Cannot cut stone
- Results subtle compared to wood
- Best with high-contrast dark stones

#### Food-Safe Materials

**Wood Cutting Boards** (Maple, Bamboo):
- Use food-safe finishes after laser work
- Mineral oil recommended
- Clean thoroughly before use

**Glass/Ceramic** (Coated):
- Can mark some glass coatings
- Speed: 2,000-3,000 mm/min
- Power: S600-S900 (60-90%)
- Passes: 1-2
- Notes: Inconsistent results, test first

---

## Advanced Techniques

### 3D Engraving / Depth Mapping

**Concept**: Vary laser power based on image grayscale to create depth

**Settings**:
- Speed: 2,000-3,000 mm/min (constant)
- Power: S100-S800 (varies with image brightness)
- DPI: 170-254 (higher = better detail)
- Material: Light wood (basswood, pine) works best

**G-code Mode**: M4 (dynamic power mode)
- Adjusts power in real-time based on speed
- Better for images and grayscale

**Tips**:
- Prepare image: High contrast, good grayscale range
- Test on scrap: Adjust min/max power
- Multiple passes: Slight offset for smoother gradients

### Vector Cutting vs. Raster Engraving

**Vector Cutting** (Line-based):
- G-code follows paths (G1/G2/G3 commands)
- Speed: Travel along defined lines only
- Best for: Cutting, outlines, text
- Efficiency: Fast, minimal laser time

**Raster Engraving** (Image-based):
- Laser scans back and forth like printer
- Speed: Covers entire area in rows
- Best for: Photos, grayscale, fills
- Efficiency: Slower, more detailed

### Multi-Pass Strategies

**Strategy 1: Same Power, Multiple Passes**
- Best for: Cutting thicker materials
- Advantage: Consistent depth, less charring
- Example: 3mm plywood at S600, 4 passes

**Strategy 2: Increasing Power Each Pass**
- Best for: Progressive depth control
- Example: Pass 1 @ S300, Pass 2 @ S500, Pass 3 @ S700
- Advantage: Gentler initial cut, aggressive finish

**Strategy 3: Offset Passes (3D Depth)**
- Best for: Smooth gradients
- Offset: 0.1-0.2mm between passes
- Advantage: Smoother surface finish

### Focus Techniques

**On-Surface Focus** (Standard):
- Material surface = focal point
- Result: Sharpest line, ~0.1mm width
- Best for: Fine detail, engraving

**Above-Surface Focus** (Cutting):
- Focal point 1-2mm above material
- Result: Deeper penetration, wider kerf
- Best for: Cutting thicker materials

**Below-Surface Focus** (Wide Line):
- Focal point below material (defocused)
- Result: Wider, softer lines
- Best for: Artistic effects, less char

### Air Assist (If Available)

**Benefits**:
- Clears smoke/debris from cut path
- Reduces charring and residue
- Improves cut quality
- Reduces fire risk

**Settings**:
- Low pressure: 5-10 PSI (engraving)
- High pressure: 10-15 PSI (cutting)
- Angle nozzle toward cutting direction

**DIY Air Assist**:
- Small aquarium pump (~3-5W)
- Direct airflow near laser focal point
- Keep nozzle 10-20mm from work

---

## Troubleshooting

### Problem: Burn Marks / Excessive Charring

**Causes & Solutions**:
1. **Too much power**: Reduce S value by 100-200
2. **Too slow speed**: Increase speed by 500-1,000 mm/min
3. **Poor focus**: Re-adjust focus gauge
4. **No air assist**: Add ventilation or air flow
5. **Multiple passes too close**: Increase time between passes

**Prevention**:
- Start with lower power, increase gradually
- Use masking tape on surface (remove after)
- Clean lens regularly

### Problem: Incomplete Cut / Not Cutting Through

**Causes & Solutions**:
1. **Insufficient power**: Increase S value by 100-200
2. **Too fast speed**: Reduce speed by 500 mm/min
3. **Material too thick**: Add more passes
4. **Focus too high/low**: Re-check focus distance
5. **Dirty lens**: Clean with lens cleaning solution

**Prevention**:
- Check material thickness with caliper
- Test cut on scrap first
- Use correct focus for cutting (1mm above surface)

### Problem: Uneven Cuts / Depth Variation

**Causes & Solutions**:
1. **Unlevel bed**: Level work surface with shims
2. **Warped material**: Flatten with weights/tape
3. **Inconsistent focus**: Material surface not flat
4. **Variable material density**: Normal for some woods

**Prevention**:
- Use flat, stable work surface
- Flatten materials before cutting
- Test engrave at multiple points to verify level

### Problem: Weak Engraving / Low Contrast

**Causes & Solutions**:
1. **Insufficient power**: Increase S value by 100-200
2. **Wrong material**: Some materials don't engrave well (metals)
3. **Poor image prep**: Increase contrast in source image
4. **Wrong focus**: Verify focus is on surface

**Prevention**:
- Use high-contrast images (black/white, not gray)
- Test on material scrap first
- Choose laser-friendly materials (light woods)

### Problem: Smoke Stains / Residue

**Causes & Solutions**:
1. **Poor ventilation**: Add fume extraction
2. **Material outgassing**: Normal for some materials
3. **No air assist**: Add compressed air flow
4. **Protective coating needed**: Apply masking tape before engraving

**Cleaning**:
- Light residue: Damp cloth with mild soap
- Stubborn marks: Isopropyl alcohol (90%+)
- Wood: Light sanding (220-400 grit)

### Problem: Fire / Flames During Operation

**IMMEDIATE ACTION**:
1. **Press E-stop or pause immediately**
2. **Close safety door** (cuts laser power)
3. **Smother flames** with fire extinguisher or damp cloth
4. **Never use water** on electrical fires

**Prevention**:
- Never leave laser unattended
- Keep fire extinguisher nearby
- Remove flammable materials from work area
- Use lower power for fire-prone materials
- Monitor first pass closely

---

## Quick Reference Chart

### Material Quick Lookup

| Material | Engrave Speed | Engrave Power | Cut Speed | Cut Power | Cut Passes | Max Thickness |
|----------|---------------|---------------|-----------|-----------|------------|---------------|
| **Basswood** | 3,000 | S200 (20%) | 500 | S500 (50%) | 3 | 3mm |
| **Plywood** | 2,500 | S300 (30%) | 300 | S700 (70%) | 6 | 4mm |
| **Oak** | 2,000 | S400 (40%) | 250 | S800 (80%) | 8 | 2mm |
| **MDF** | 2,500 | S250 (25%) | 400 | S700 (70%) | 5 | 3mm |
| **Cork** | 3,500 | S200 (20%) | 500 | S500 (50%) | 3 | 3mm |
| **Paper (80g)** | 6,000 | S100 (10%) | 4,000 | S150 (15%) | 1 | 0.1mm |
| **Cardstock** | 3,500 | S150 (15%) | 2,000 | S300 (30%) | 2 | 0.3mm |
| **Cardboard** | 3,000 | S200 (20%) | 800 | S500 (50%) | 4 | 4mm |
| **Leather** | 2,500 | S300 (30%) | 600 | S600 (60%) | 2 | 2mm |
| **Cotton Fabric** | 4,000 | S150 (15%) | 2,000 | S300 (30%) | 1 | 1mm |
| **Felt** | 4,000 | S150 (15%) | 1,000 | S400 (40%) | 1 | 3mm |
| **Denim** | 2,500 | S300 (30%) | - | - | - | Engrave only |
| **Acrylic (clear)** | 2,500 | S300 (30%) | 500 | S750 (75%) | 5 | 3mm |
| **Delrin** | 3,000 | S400 (40%) | 500 | S700 (70%) | 4 | 2mm |
| **Anodized Al** | 2,500 | S800 (80%) | - | - | - | Marking only |
| **Bamboo** | 2,500 | S300 (30%) | 400 | S700 (70%) | 6 | 4mm |
| **Slate** | 1,500 | S900 (90%) | - | - | - | Marking only |

*All speeds in mm/min. Values are starting points - always test on scrap material.*

---

## G-Code Examples

### Basic Engraving (Rectangle)

```gcode
G21         ; Set units to mm
G90         ; Absolute positioning
M3 S300     ; Laser on at 30% power
G0 X10 Y10  ; Move to start position
G1 X40 Y10 F2000  ; Engrave line to X40 (speed 2000 mm/min)
G1 X40 Y30 F2000  ; Engrave line to Y30
G1 X10 Y30 F2000  ; Engrave line back to X10
G1 X10 Y10 F2000  ; Engrave line back to start
M5          ; Laser off
G0 X0 Y0    ; Return to origin
```

### Cutting Circle (5 passes)

```gcode
G21         ; Set units to mm
G90         ; Absolute positioning
M3 S600     ; Laser on at 60% power
G0 X30 Y20  ; Move to start position
G2 X30 Y20 I-10 J0 F400  ; Cut circle, radius 10mm, pass 1
G2 X30 Y20 I-10 J0 F400  ; Pass 2
G2 X30 Y20 I-10 J0 F400  ; Pass 3
G2 X30 Y20 I-10 J0 F400  ; Pass 4
G2 X30 Y20 I-10 J0 F400  ; Pass 5
M5          ; Laser off
G0 X0 Y0    ; Return to origin
```

### Dynamic Power Image Engraving

```gcode
G21         ; Set units to mm
G90         ; Absolute positioning
M4 S800     ; Dynamic power mode, max 80%
G0 X0 Y0    ; Start position
; (Image scan lines would follow, generated by software)
; Each line varies S value based on image darkness
M5          ; Laser off
```

---

## CAM Software Settings

### LightBurn (Recommended)

**Speed Settings**:
- Set max speed: 12,000 mm/min (match machine)
- Typical engrave: 2,000-3,000 mm/min
- Typical cut: 300-800 mm/min

**Power Settings**:
- Min Power: S0 (0%)
- Max Power: S1000 (100%)
- Typical engrave: 20-40%
- Typical cut: 50-80%

**Image Mode**:
- Choose "Stucki" or "Jarvis" dithering for photos
- DPI: 170-254 for quality
- Scan Angle: 0° or 45° (test both)

### LaserGRBL (Free, Windows)

**Configuration**:
- Max speed: 12,000 mm/min
- Laser mode: M3 (constant) or M4 (dynamic)
- S-Max: 1000

**Image Settings**:
- Dithering: Floyd-Steinberg
- Line to Line: 170-254 DPI
- Quality: "High" for final, "Draft" for testing

---

## Maintenance for Best Results

### Daily (Before Each Session)

1. **Clean lens**: Use lens cleaning solution and microfiber cloth
2. **Check focus**: Verify focus gauge/paper method
3. **Level check**: Ensure work surface is level
4. **Safety check**: Test safety door, e-stop

### Weekly (After ~10 hours of use)

1. **Clean mirrors**: Remove dust with compressed air, clean if needed
2. **Check belts**: Ensure proper tension (should twang like guitar string)
3. **Lubricate rails**: Light machine oil on linear rails
4. **Clear ventilation**: Check fume extraction paths

### Monthly

1. **Deep clean**: Remove all dust and debris from enclosure
2. **Calibrate**: Test square cuts, adjust if needed
3. **Firmware check**: Verify settings haven't changed (run $$)

---

## Tips for Best Results

### General Tips

1. **Always test first**: Use scrap material before final piece
2. **Start conservative**: Low power, high speed, then adjust
3. **Multiple light passes > One heavy pass**: Better quality, less charring
4. **Focus is critical**: 90% of problems are focus-related
5. **Clean lens regularly**: Dirty lens = weak laser, uneven results

### Material-Specific Tips

**Wood**:
- Mask with painter's tape to prevent burn marks
- Sand lightly (220 grit) before engraving for best contrast
- Apply finish (oil/wax) after engraving to protect

**Paper/Cardboard**:
- Use lowest power possible to avoid fire
- Flatten with books/weights before cutting
- Cut from lightest color side for cleanest edge

**Leather**:
- Test on hidden area first (varies by tanning method)
- Natural/vegetable tanned = best results
- Apply leather conditioner after engraving

**Acrylic**:
- Remove protective film on both sides before engraving
- For frosted look: Engrave from back, view from front
- Polish cut edges with flame or acrylic polish

**Fabric**:
- Iron flat before engraving
- Use hoop or frame to keep taut
- Wash before laser to remove sizing

### Artwork Preparation

**Vector Files** (AI, SVG, DXF):
- Use black (#000000) for cuts (100% power)
- Use gray for engraving (varies power)
- Simplify complex paths (too many nodes = slow)
- Set line width to 0.01mm (hairline)

**Raster Images** (JPG, PNG, BMP):
- Convert to grayscale
- Increase contrast (levels/curves)
- Resize to actual size BEFORE importing
- 300 DPI for source, 170-254 DPI for engraving

---

## Safety Reminders

### Eye Safety
- **ALWAYS wear 445nm laser safety glasses**
- Even brief exposure can cause permanent eye damage
- Provide glasses for anyone in room
- Never look at focused laser spot

### Fire Safety
- Never leave laser unattended
- Keep fire extinguisher within 10 feet
- Clear flammable materials from area
- Use fume extraction for all materials
- Monitor first pass of new materials closely

### Fume Safety
- Adequate ventilation required for ALL materials
- Never laser toxic materials (PVC, ABS, etc.)
- Some materials (acrylic) produce harmful fumes
- Use proper fume extraction or outdoor setup

---

## Appendix: Units & Conversions

### Speed Conversions
- 1,000 mm/min = 1 cm/sec = 3.94 inches/min
- 12,000 mm/min = 20 cm/sec = 47.2 inches/min = 200 mm/sec

### Power Levels
- 2.5W laser ≈ 2,500 milliwatts
- S250 = 0.625W output
- S500 = 1.25W output
- S750 = 1.875W output
- S1000 = 2.5W output (full power)

### Material Thickness (Common)
- Paper: 0.08-0.1mm (80-100 gsm)
- Cardstock: 0.2-0.3mm (200-300 gsm)
- Veneer: 0.6-1mm
- Plywood: 1.5mm, 3mm, 4mm, 6mm (common)
- Acrylic: 1mm, 2mm, 3mm, 4mm, 5mm, 6mm

---

## Resources & Further Reading

### Recommended CAM Software
- **LightBurn** (paid, $60): Best features, active development
- **LaserGRBL** (free): Good for beginners, Windows only
- **LaserWeb** (free, open source): Cross-platform

### Online Material Libraries
- LightBurn Material Library (community-shared settings)
- Thingiverse (laser cut designs and parameters)
- Instructables (laser project tutorials)

### Communities
- r/lasercutting (Reddit)
- LightBurn Forum
- Grbl_ESP32 GitHub Discussions

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Machine**: Genmitsu Kiosk 2.5W (445nm)  
**Firmware**: Grbl_ESP32 v1.3a

**Disclaimer**: These parameters are starting points based on the machine's specifications and community experience. Always test on scrap material first. Different batches of the same material may require adjustment. User assumes all responsibility for safe operation.
