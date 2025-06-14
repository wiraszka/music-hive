# MusicHub - Advanced Music Downloader

A sophisticated desktop application for downloading music from YouTube with intelligent song filtering, Spotify metadata integration, and high-quality audio processing.

## Key Features

### Advanced Song Filtering
- **Strict Duration Matching**: ±5 second tolerance prevents metadata mismatches
- **Confidence Scoring**: Weighted algorithm (title 40%, duration 35%, artist 25%)
- **Content Filtering**: Automatically removes live performances, covers, albums, remixes
- **Non-Spotify Detection**: Includes bootlegs and unofficial releases when relevant

### Visual Indicators
- **High Confidence**: ✓ symbol with full metadata and album art
- **Medium Confidence**: ~ symbol with validated metadata  
- **YouTube Only**: Relevance-based inclusion without Spotify data
- **Album Cover Art**: 37x37px thumbnails per search result

### Audio Quality
- Multiple quality options: 128k, 192k, 256k, 320k
- Zero-setup FFmpeg integration via imageio-ffmpeg
- Embedded metadata with album artwork
- MP3 output with accurate tags

## Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
python setup_for_local.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install yt-dlp==2025.4.30 mutagen==1.47.0 spotipy==2.25.1 requests==2.32.3 PyQt6==6.9.0 fuzzywuzzy==0.18.0 python-levenshtein==0.27.1 imageio-ffmpeg==0.6.0

# Run application
python main.py
```

## Requirements

- **Python**: 3.8 or higher
- **Platform**: Windows, macOS, or Linux with desktop environment
- **Spotify API**: Client ID and Secret (get from https://developer.spotify.com/dashboard)

### Platform-Specific Notes

**Windows**: All dependencies install automatically via pip

**macOS**: All dependencies install automatically via pip  

**Linux**: If GUI issues occur, install system packages:
```bash
sudo apt-get install python3-pyqt6 libgl1-mesa-glx
```

## Configuration

### Spotify API Setup
1. Visit https://developer.spotify.com/dashboard
2. Create a new application
3. Copy Client ID and Client Secret
4. Add to `config/config.json`:

```json
{
  "spotify_client_id": "your_client_id_here",
  "spotify_client_secret": "your_client_secret_here",
  "download_location": "/path/to/downloads",
  "audio_quality": "320k",
  "confidence_threshold": 60.0,
  "duration_tolerance": 5
}
```

### Environment Variables (Alternative)
```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

## Usage

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Search for Music**
   - Enter artist and song name
   - Results show confidence indicators and album art
   - Advanced filtering removes non-songs automatically

3. **Download**
   - Select desired result
   - Choose audio quality
   - Download with embedded metadata and album art

## Advanced Filtering Workflow

```
Search Query → YouTube Search (20 results) → Song Filtering → Spotify Matching → Confidence Scoring → Result Display
```

### Filtering Logic
1. **Duration Filter**: Removes videos under 30s or over 10 minutes
2. **Content Filter**: Excludes live performances, albums, covers, remixes
3. **Relevance Filter**: Basic relevance scoring removes irrelevant content
4. **Spotify Matching**: Individual searches for remaining results
5. **Confidence Calculation**: Multi-factor scoring with strict duration validation
6. **Inclusion Decision**: High/medium confidence or YouTube-only inclusion

### Confidence Thresholds
- **≥80%**: High confidence (✓) - Full Spotify metadata applied
- **≥60%**: Medium confidence (~) - Validated Spotify metadata
- **<60%**: YouTube-only if relevance ≥75% - No Spotify metadata

## File Structure

```
MusicHub/
├── main.py                    # Application entry point
├── setup_for_local.py         # Automated setup script
├── gui/                       # User interface components
│   ├── main_window.py
│   ├── download_tab.py        # Enhanced with filtering
│   └── style.py
├── utils/
│   ├── song_filter.py         # Advanced filtering system
│   └── config.py
├── search_youtube.py          # YouTube search integration
├── search_spotify.py          # Spotify API integration
├── downloader.py              # Download and audio processing
├── process_text.py            # Text processing utilities
├── config/                    # Configuration files
├── downloads/                 # Downloaded music files
└── library/                   # Local music library
```

## Dependencies

All dependencies install automatically via setup script:

- **yt-dlp**: YouTube downloading
- **mutagen**: Audio metadata handling
- **spotipy**: Spotify API integration
- **PyQt6**: Desktop GUI framework
- **fuzzywuzzy**: Fuzzy string matching
- **python-levenshtein**: Fast text similarity
- **imageio-ffmpeg**: Bundled FFmpeg (no manual install needed)
- **requests**: HTTP requests

## Troubleshooting

### Import Errors
Run the setup verification:
```bash
python setup_for_local.py
```

### No Search Results
- Check internet connection
- Verify Spotify API credentials
- Try simpler search terms

### Download Fails
- Ensure write permissions to download folder
- Check available disk space
- Verify FFmpeg integration with setup script

### GUI Won't Start
- Ensure desktop environment available
- Install platform-specific GUI libraries (see Platform Notes)
- Check Python version (3.8+ required)

## Performance

- **Efficient Filtering**: Processes 20 YouTube results, filters to ~5-10 relevant songs
- **Minimal API Calls**: Bulk filtering before individual Spotify searches
- **Fast Text Matching**: python-levenshtein accelerates fuzzy matching
- **Smart Caching**: Confidence scores cached during processing

## Development

### Running Tests
```bash
python setup_for_local.py  # Includes comprehensive testing
```

### Key Components
- `utils/song_filter.py`: Core filtering logic with confidence scoring
- `gui/download_tab.py`: Enhanced UI with album art and indicators
- `downloader.py`: Audio processing with FFmpeg integration
- `search_*.py`: YouTube and Spotify search APIs

## License

This project is for educational and personal use. Respect YouTube's Terms of Service and content creators' rights.

---

**Ready to use**: All advanced filtering features are integrated and tested for local desktop deployment.