# Browser Extension Icons

This folder contains the icon files for the AI Speech Enhancement browser extension.

## Icon Sizes

- `icon16.png` - 16x16 pixels (toolbar icon, small)
- `icon48.png` - 48x48 pixels (extension management page)
- `icon128.png` - 128x128 pixels (Chrome Web Store, installation)

## Creating Icons

### Option 1: Use an Online Tool
1. Use the provided `icon128.svg` file
2. Visit https://www.iloveimg.com/resize-image or similar
3. Convert SVG to PNG at required sizes

### Option 2: Use ImageMagick (Command Line)
```bash
# Install ImageMagick if not already installed
# On Ubuntu/Debian: sudo apt-get install imagemagick
# On Mac: brew install imagemagick

# Convert SVG to PNG at different sizes
convert icon128.svg -resize 16x16 icon16.png
convert icon128.svg -resize 48x48 icon48.png
convert icon128.svg -resize 128x128 icon128.png
```

### Option 3: Use GIMP (GUI)
1. Open `icon128.svg` in GIMP
2. Export as PNG
3. Scale to required sizes

### Option 4: Use Figma/Adobe Illustrator
1. Import the SVG
2. Export at multiple resolutions

## Temporary Placeholder

For development, you can use emoji or simple colored squares:

**Quick Placeholder Script:**
```bash
# Create simple placeholder PNGs with ImageMagick
convert -size 16x16 xc:#667eea icon16.png
convert -size 48x48 xc:#667eea icon48.png
convert -size 128x128 xc:#667eea icon128.png
```

## Design Guidelines

### Chrome Web Store
- 128x128 PNG
- Transparent background or solid color
- Clear and recognizable at small sizes
- Match brand colors (#667eea, #764ba2)

### Firefox Add-ons
- 128x128 PNG
- Similar guidelines as Chrome

## Brand Colors

- Primary: #667eea (Purple-Blue)
- Secondary: #764ba2 (Purple)
- Accent: #f093fb (Pink)
