# macOS Setup Guide - Adam's Music Downloader

## Quick Setup (Choose One Method)

### Method 1: Homebrew (Recommended)
```bash
# Install Homebrew (requires admin password once)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Install Python dependencies and run
python3 setup_and_run.py
```

### Method 2: MacPorts
```bash
# Install MacPorts from https://www.macports.org/install.php
# Then install FFmpeg
sudo port install ffmpeg

# Install Python dependencies and run
python3 setup_and_run.py
```

### Method 3: Manual Installation
```bash
# Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
# Extract to ~/.local/bin/
mkdir -p ~/.local/bin
# Copy ffmpeg and ffprobe binaries to ~/.local/bin/
chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="$HOME/.local/bin:$PATH"

# Install Python dependencies and run
python3 setup_and_run.py
```

## What Each Method Does

**Homebrew**: Most popular package manager for macOS. Requires admin password once during initial setup, then manages all dependencies automatically.

**MacPorts**: Alternative package manager. Also requires admin access but some users prefer it.

**Manual**: Download pre-compiled binaries. No admin required after initial download, but requires manual PATH configuration.

## Verification

After installation, verify FFmpeg works:
```bash
ffmpeg -version
ffprobe -version
```

Both commands should display version information without errors.

## Running the Application

Once FFmpeg is installed:
```bash
python3 main.py
```

The application will automatically detect your FFmpeg installation and enable audio conversion features.

## Troubleshooting

**"ffmpeg not found" error**: FFmpeg is not in your PATH. Check installation and ensure binaries are executable.

**Permission denied**: Run `chmod +x` on the FFmpeg binaries.

**GUI not displaying**: Install PyQt6 dependencies: `pip3 install PyQt6`

## Alternative: Conda Environment

If you use Anaconda or Miniconda:
```bash
conda create -n music-downloader python=3.9
conda activate music-downloader
conda install -c conda-forge ffmpeg
pip install yt-dlp mutagen spotipy requests PyQt6
python main.py
```

This creates an isolated environment with all dependencies managed by conda.