# Music Downloader

A desktop application for downloading music from YouTube with Spotify metadata integration and local library management.

## Features

- Search and download music from YouTube
- Spotify metadata integration for accurate tagging
- Quality selection (128k to 320k)
- Responsive GUI with adaptive layout
- Local music library management
- Intelligent song filtering and matching

## Quick Setup

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure Spotify API:**
   - Get API keys from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Edit `credentials.env` with your keys:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Requirements

- Python 3.8+
- FFmpeg (auto-installed by setup script)
- Spotify API credentials

## Project Structure

```
music-downloader/
├── main.py              # Application entry point
├── setup.py             # Setup and dependency installer
├── gui/                 # User interface components
├── utils/               # Utility modules
├── library/             # Music library management
├── assets/              # Application assets
└── downloads/           # Default download directory
```

## Supported Platforms

- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu, Fedora, Arch, etc.)

## License

This project is for educational purposes. Respect copyright laws and YouTube's terms of service.