# Adam's Music Downloader

A Python desktop application for downloading music from YouTube with Spotify metadata integration and local music library management.

## Features

- **YouTube Music Downloading**: Search and download music from YouTube
- **Spotify Integration**: Automatic metadata retrieval from Spotify
- **Music Library Management**: Scan and organize your local music collection
- **Modern GUI**: Clean PyQt6 interface with sidebar navigation
- **Quality Selection**: Choose from multiple audio quality options
- **Progress Tracking**: Real-time download progress monitoring

## Screenshots

The application features a modern design with:
- Left sidebar navigation (20% width)
- Main content area with cityscape background
- Centered "MUSIC is LIFE" branding
- Search functionality in the lower third of the window

## Requirements

- Python 3.11+
- PyQt6
- yt-dlp
- spotipy
- mutagen
- requests

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/music-downloader.git
cd music-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Spotify API credentials:
   - Create a Spotify app at https://developer.spotify.com/
   - Set environment variables:
     - `SPOTIFY_CLIENT_ID`
     - `SPOTIFY_CLIENT_SECRET`

## Usage

1. Run the application:
```bash
python main.py
```

2. **Download Tab**: Search for music and download from YouTube
3. **Library Tab**: Manage your local music collection
4. **Settings Tab**: Configure download location and preferences
5. **About Tab**: Application information

## Configuration

The application stores settings in a configuration file that includes:
- Download directory
- Audio quality preferences
- Library scan paths

## Project Structure

```
├── gui/                    # PyQt6 GUI components
│   ├── main_window.py     # Main application window
│   ├── download_tab.py    # Download functionality
│   ├── library_tab.py     # Library management
│   └── style.py           # Application styling
├── library/               # Music library management
├── utils/                 # Utility functions
├── assets/                # Application assets
├── preview/               # HTML design previews
├── main.py               # Application entry point
├── downloader.py         # YouTube download logic
├── search_spotify.py     # Spotify API integration
└── search_youtube.py     # YouTube search functionality
```

## Development

This project was built using Replit and includes HTML previews for design visualization since PyQt6 cannot run in cloud environments.

## License

This project is based on the original work by Adam Wiraszka: https://github.com/wiraszka/music-downloader

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request