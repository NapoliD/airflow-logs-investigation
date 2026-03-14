# Assets

This directory contains visual assets for the project.

## Creating the Demo GIF

### Option 1: Using asciinema + agg (Recommended)

```bash
# Install asciinema
pip install asciinema

# Install agg (asciinema gif generator)
# See: https://github.com/asciinema/agg

# Record the demo
asciinema rec demo.cast -c "python scripts/visual_demo.py"

# Convert to GIF
agg demo.cast demo.gif --theme monokai
```

### Option 2: Using terminalizer

```bash
# Install terminalizer
npm install -g terminalizer

# Record
terminalizer record demo --command "python scripts/visual_demo.py"

# Generate GIF
terminalizer render demo -o demo.gif
```

### Option 3: Using peek (Linux)

```bash
# Install peek
sudo apt install peek

# Open peek, select terminal window, record while running:
python scripts/visual_demo.py
```

### Option 4: Using Kap (macOS)

1. Download Kap from https://getkap.co
2. Select terminal window
3. Run `python scripts/visual_demo.py`
4. Export as GIF

## Recommended Settings

- **Terminal size**: 100 columns x 30 rows
- **Font size**: 14-16px
- **Theme**: Dark (Monokai, Dracula, or similar)
- **GIF width**: 700-800px
- **Frame rate**: 10-15 fps
- **Speed**: 1x or 1.5x

## File Naming

- `demo.gif` - Main demo for README
