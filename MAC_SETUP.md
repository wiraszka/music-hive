# Running Adam's Music Downloader on Mac

## Quick Setup

1. **Navigate to your downloaded project folder:**
```bash
cd /path/to/music-downloader
```

2. **Install dependencies:**
```bash
pip install PyQt6 yt-dlp mutagen spotipy requests
```

3. **Set Spotify API credentials:**
```bash
export SPOTIFY_CLIENT_ID="your_client_id_from_replit"
export SPOTIFY_CLIENT_SECRET="your_client_secret_from_replit"
```

4. **Run the application:**
```bash
python main.py
```

## Alternative Easy Setup

Simply run the setup script:
```bash
python setup_and_run.py
```

This will automatically:
- Check Python version
- Install all required packages
- Guide you through API setup
- Create default directories
- Launch the application

## What You'll See

When the application launches, you'll get:
- Left sidebar with Download, Library, Settings, and About tabs
- Clicking tabs switches the main content area
- Download tab has the "MUSIC is LIFE" interface for YouTube searching
- Library tab for managing your local music collection
- Settings tab for configuring download location and quality
- All buttons use the light gray color scheme as requested

## Features Working

- YouTube search and download with quality selection
- Spotify metadata integration (your API keys are already configured)
- Local music library scanning and organization
- Tab navigation between different sections
- Progress tracking for downloads
- Metadata enhancement for existing music files

The navigation tabs will function exactly as shown in the HTML preview, but with real downloading and library management capabilities.