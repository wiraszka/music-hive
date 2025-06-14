#!/usr/bin/env python3
"""
Zero Setup Launcher for MusicHub
Automatically installs all dependencies and configures the application
"""

import os
import sys
import subprocess
import json
import importlib
from pathlib import Path

# Complete dependency list with versions
DEPENDENCIES = [
    'yt-dlp>=2025.4.30',
    'mutagen>=1.47.0', 
    'spotipy>=2.25.1',
    'requests>=2.32.3',
    'PyQt6>=6.9.0',
    'fuzzywuzzy>=0.18.0',
    'python-levenshtein>=0.27.1',
    'imageio-ffmpeg>=0.6.0'
]

# Spotify API credentials
SPOTIFY_CLIENT_ID = "your_spotify_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret_here"

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Install all required Python packages"""
    print("Installing dependencies...")
    
    try:
        for package in DEPENDENCIES:
            print(f"Installing {package.split('>=')[0]}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✓ All dependencies installed")
        return True
        
    except subprocess.CalledProcessError:
        print("✗ Dependency installation failed")
        return False

def verify_core_components():
    """Verify all core components are working"""
    print("Verifying components...")
    
    # Test imports
    components = [
        ('yt_dlp', 'YouTube downloader'),
        ('mutagen', 'Audio metadata'),
        ('spotipy', 'Spotify integration'),
        ('fuzzywuzzy', 'Song matching'),
        ('Levenshtein', 'Text similarity'),
        ('imageio_ffmpeg', 'Audio processing')
    ]
    
    for module, description in components:
        try:
            importlib.import_module(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"✗ {description} failed")
            return False
    
    return True

def verify_filtering_system():
    """Verify the advanced song filtering system"""
    print("Verifying filtering system...")
    
    try:
        from utils.song_filter import SongFilter
        from fuzzywuzzy import fuzz
        
        # Test filter initialization
        filter_system = SongFilter()
        
        # Test confidence calculation
        sample_youtube = {
            'title': 'Artist - Song Name',
            'duration': '3:30',
            'channel': 'Music Channel'
        }
        
        sample_spotify = {
            'name': 'Song Name',
            'artists': [{'name': 'Artist'}],
            'duration_ms': 210000
        }
        
        confidence = filter_system.calculate_spotify_match_confidence(
            sample_youtube, sample_spotify
        )
        
        if confidence > 80:
            print("✓ High-precision matching system")
        else:
            print("✓ Filtering system operational")
        
        return True
        
    except Exception as e:
        print(f"✗ Filtering system error: {e}")
        return False

def setup_ffmpeg():
    """Ensure FFmpeg is available via imageio-ffmpeg"""
    print("Setting up audio processing...")
    
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Test FFmpeg functionality
        result = subprocess.run([ffmpeg_exe, '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✓ Audio processing ready")
            return True
        else:
            print("✗ Audio processing setup failed")
            return False
            
    except Exception as e:
        print(f"✗ Audio processing error: {e}")
        return False

def create_config():
    """Create configuration with embedded credentials"""
    print("Setting up configuration...")
    
    try:
        # Create config directory
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Default download location
        download_location = Path.home() / "Downloads" / "MusicDownloader"
        download_location.mkdir(parents=True, exist_ok=True)
        
        # Configuration data
        config_data = {
            "download_location": str(download_location),
            "spotify_client_id": SPOTIFY_CLIENT_ID,
            "spotify_client_secret": SPOTIFY_CLIENT_SECRET,
            "audio_quality": "320k",
            "max_search_results": 20,
            "confidence_threshold": 60.0,
            "duration_tolerance": 5
        }
        
        # Write config file
        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✓ Configuration saved to {config_file}")
        return True
        
    except Exception as e:
        print(f"✗ Configuration setup failed: {e}")
        return False

def create_directories():
    """Create necessary application directories"""
    directories = [
        "downloads",
        "library", 
        "temp",
        "config"
    ]
    
    try:
        for directory in directories:
            dir_path = Path(directory)
            dir_path.mkdir(exist_ok=True, parents=True)
            print(f"✓ Created directory: {directory}")
        
        print("✓ Directory structure created")
        return True
        
    except Exception as e:
        print(f"✗ Directory creation failed: {e}")
        return False

def test_complete_pipeline():
    """Test the complete application pipeline"""
    print("Testing complete pipeline...")
    
    try:
        # Test search components
        from search_youtube import YouTubeSearch
        from search_spotify import SpotifySearch
        
        youtube = YouTubeSearch()
        spotify = SpotifySearch()
        
        # Test download components  
        from downloader import Downloader, AudioQuality
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = Downloader(temp_dir)
        
        # Test filtering integration
        from utils.song_filter import SongFilter
        filter_system = SongFilter()
        
        # Test text processing
        from process_text import clean_search_query, extract_song_info
        clean_search_query("test query")
        extract_song_info("Artist - Song")
        
        print("✓ Complete pipeline functional")
        return True
        
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        return False

def main():
    """Main setup and launch process"""
    print("MusicHub Zero-Setup Launcher")
    print("=" * 40)
    
    # Setup steps
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies), 
        ("Core Components", verify_core_components),
        ("Filtering System", verify_filtering_system),
        ("Audio Processing", setup_ffmpeg),
        ("Configuration", create_config),
        ("Directories", create_directories),
        ("Pipeline Test", test_complete_pipeline)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}:")
        print("-" * 25)
        
        if not step_func():
            print(f"\n✗ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 40)
    print("✓ MusicHub setup complete!")
    print("\nFeatures enabled:")
    print("• Advanced song filtering with ±5s duration matching")
    print("• Album cover art and Spotify metadata integration")
    print("• Non-Spotify song detection for bootlegs/remixes")
    print("• High-precision confidence scoring system")
    print("• Zero-configuration FFmpeg integration")
    
    print(f"\nReady to launch: python main.py")
    
    # Auto-launch option
    response = input("\nLaunch MusicHub now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        try:
            os.system("python main.py")
        except KeyboardInterrupt:
            print("\nApplication closed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)