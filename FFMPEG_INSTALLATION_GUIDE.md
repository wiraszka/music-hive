# FFmpeg Installation Guide

## Overview
FFmpeg is a critical dependency for Adam's Music Downloader that enables audio conversion from YouTube videos to MP3 format. All setup scripts now automatically check for and attempt to install FFmpeg.

## Automatic Installation

### Setup Scripts Updated
All setup scripts now include FFmpeg dependency management:

1. **auto_setup.py** - Fully automated installation
2. **easy_setup.py** - Interactive setup with FFmpeg check
3. **setup_and_run.py** - Comprehensive system check including FFmpeg

### Installation Process
When running any setup script, FFmpeg installation follows this flow:

1. **Detection**: Check if FFmpeg is already installed
2. **Platform Detection**: Identify operating system (macOS, Linux, Windows)
3. **Automatic Installation**: Use appropriate package manager
4. **Fallback Instructions**: Provide manual installation steps if automatic fails

## Platform-Specific Installation

### macOS
**Automatic via Homebrew:**
```bash
brew install ffmpeg
```

**Manual Installation:**
1. Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Run: `brew install ffmpeg`

### Linux (Ubuntu/Debian)
**Automatic via apt:**
```bash
sudo apt update
sudo apt install -y ffmpeg
```

**Other Linux distributions:**
- **CentOS/RHEL:** `sudo yum install ffmpeg` or `sudo dnf install ffmpeg`
- **Arch Linux:** `sudo pacman -S ffmpeg`

### Windows
**Manual Installation Required:**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to system PATH
4. Restart command prompt/terminal

## Verification

### Check Installation
Run in terminal/command prompt:
```bash
ffmpeg -version
```

### Expected Output
Should display FFmpeg version information and available codecs.

## Integration with Application

### Downloader Configuration
The application automatically:
- Detects FFmpeg location using `shutil.which()`
- Sets `ffmpeg_location` parameter in yt-dlp configuration
- Falls back to system PATH if specific location not found

### Error Handling
If FFmpeg is missing during download:
- Clear error message displayed to user
- Automatic fallback to manual installation instructions
- Setup scripts guide user through installation process

## Troubleshooting

### Common Issues
1. **PATH not updated**: Restart terminal after installation
2. **Permission errors**: Use `sudo` on Linux/macOS for system-wide installation
3. **Package manager missing**: Install Homebrew (macOS) or update package lists (Linux)

### Support Commands
- **macOS**: `brew doctor` to check Homebrew issues
- **Linux**: `apt list --installed | grep ffmpeg` to verify installation
- **Windows**: `where ffmpeg` to check PATH configuration

## Setup Script Features

### auto_setup.py
- Silent FFmpeg installation
- No user interaction required
- Embedded Spotify credentials

### easy_setup.py
- Interactive FFmpeg setup
- Progress feedback
- Error handling with manual instructions

### setup_and_run.py
- Comprehensive system checks
- Platform-specific installation methods
- Detailed error reporting and recovery instructions

All scripts ensure FFmpeg is available before proceeding with application launch.