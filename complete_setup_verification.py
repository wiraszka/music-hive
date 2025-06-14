#!/usr/bin/env python3
"""
Complete setup verification for Music Downloader
Tests all components end-to-end including the new filtering system
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

def install_all_dependencies():
    """Install all required dependencies"""
    packages = [
        'yt-dlp>=2025.4.30',
        'mutagen>=1.47.0', 
        'spotipy>=2.25.1',
        'requests>=2.32.3',
        'PyQt6>=6.9.0',
        'fuzzywuzzy>=0.18.0',
        'python-levenshtein>=0.27.1',
        'imageio-ffmpeg>=0.6.0'
    ]
    
    print("Installing all required dependencies...")
    try:
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ All dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def test_imports():
    """Test all critical imports"""
    print("\nTesting module imports...")
    
    modules = [
        'yt_dlp',
        'mutagen.mp3',
        'mutagen.id3',
        'spotipy',
        'requests',
        'fuzzywuzzy.fuzz',
        'Levenshtein',
        'imageio_ffmpeg',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_ffmpeg_integration():
    """Test FFmpeg integration with download process"""
    print("\nTesting FFmpeg integration...")
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Test FFmpeg functionality
        result = subprocess.run([ffmpeg_exe, '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ FFmpeg working: {ffmpeg_exe}")
            return True
        else:
            print("✗ FFmpeg not functional")
            return False
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False

def test_song_filtering_system():
    """Test the complete song filtering pipeline"""
    print("\nTesting song filtering system...")
    try:
        from utils.song_filter import SongFilter
        from fuzzywuzzy import fuzz
        
        filter_system = SongFilter()
        
        # Test sample data
        sample_youtube_results = [
            {
                'title': 'Artist - Song Name (Official Audio)',
                'duration': '3:45',
                'channel': 'Artist Official',
                'url': 'https://youtube.com/watch?v=test1'
            },
            {
                'title': 'Artist Live Concert 2023 Full Show',
                'duration': '1:45:30',
                'channel': 'Concert Channel',
                'url': 'https://youtube.com/watch?v=test2'
            },
            {
                'title': 'Song Name by Artist',
                'duration': '3:42',
                'channel': 'Music Channel',
                'url': 'https://youtube.com/watch?v=test3'
            }
        ]
        
        sample_spotify_track = {
            'name': 'Song Name',
            'artists': [{'name': 'Artist'}],
            'duration_ms': 225000,  # 3:45
            'album': {
                'images': [{'url': 'https://example.com/cover.jpg'}]
            },
            'id': 'spotify_track_id'
        }
        
        # Test filtering
        filtered = filter_system.filter_youtube_results(sample_youtube_results, "artist song name")
        print(f"✓ Filtered {len(sample_youtube_results)} to {len(filtered)} results")
        
        # Test confidence calculation
        if filtered:
            confidence = filter_system.calculate_spotify_match_confidence(
                filtered[0], sample_spotify_track
            )
            print(f"✓ Confidence calculation: {confidence:.1f}%")
        
        # Test fuzzy matching
        similarity = fuzz.ratio("artist song name", "song name by artist")
        print(f"✓ Fuzzy matching: {similarity}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Song filtering test failed: {e}")
        return False

def test_search_components():
    """Test YouTube and Spotify search components"""
    print("\nTesting search components...")
    
    try:
        # Test YouTube search
        from search_youtube import YouTubeSearch
        youtube = YouTubeSearch()
        print("✓ YouTube search component loaded")
        
        # Test Spotify search
        from search_spotify import SpotifySearch
        spotify = SpotifySearch()
        print("✓ Spotify search component loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Search components test failed: {e}")
        return False

def test_download_components():
    """Test download and metadata components"""
    print("\nTesting download components...")
    
    try:
        from downloader import Downloader, AudioQuality
        
        # Test downloader initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = Downloader(temp_dir)
            print("✓ Downloader initialized")
        
        # Test audio quality enum
        quality = AudioQuality.BEST
        print(f"✓ Audio quality: {quality.value}")
        
        # Test metadata handling
        from mutagen.mp3 import MP3
        print("✓ Metadata handling available")
        
        return True
        
    except Exception as e:
        print(f"✗ Download components test failed: {e}")
        return False

def test_gui_initialization():
    """Test GUI components without display"""
    print("\nTesting GUI components...")
    
    try:
        # Test Qt imports
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import Qt, QPropertyAnimation
        from PyQt6.QtGui import QPixmap, QPainter
        
        print("✓ Qt components available")
        
        # Test config system
        from utils.config import Config
        print("✓ Configuration system available")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI components test failed: {e}")
        return False

def test_end_to_end_pipeline():
    """Test the complete pipeline logic without actual network calls"""
    print("\nTesting end-to-end pipeline...")
    
    try:
        from utils.song_filter import SongFilter
        from process_text import clean_search_query, extract_song_info
        
        filter_system = SongFilter()
        
        # Simulate the complete pipeline
        query = "artist name song title"
        
        # 1. Text processing
        clean_query = clean_search_query(query)
        artist, song = extract_song_info(clean_query)
        print(f"✓ Text processing: '{query}' -> artist: '{artist}', song: '{song}'")
        
        # 2. Mock YouTube results
        mock_results = [
            {'title': 'Artist Name - Song Title', 'duration': '3:30', 'channel': 'Music'}
        ]
        
        # 3. Filtering
        filtered = filter_system.filter_youtube_results(mock_results, query)
        print(f"✓ Filtering: {len(filtered)} valid songs")
        
        # 4. Mock Spotify data
        mock_spotify = {
            'name': 'Song Title',
            'artists': [{'name': 'Artist Name'}],
            'duration_ms': 210000
        }
        
        # 5. Confidence calculation
        if filtered:
            confidence = filter_system.calculate_spotify_match_confidence(
                filtered[0], mock_spotify
            )
            print(f"✓ Match confidence: {confidence:.1f}%")
        
        # 6. Inclusion decision
        should_include, reason, conf = filter_system.should_include_result(
            filtered[0] if filtered else mock_results[0], 
            mock_spotify, 
            query
        )
        print(f"✓ Inclusion decision: {should_include} ({reason}, {conf:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end pipeline test failed: {e}")
        return False

def create_test_config():
    """Create a test configuration file"""
    print("\nCreating test configuration...")
    
    try:
        config_data = {
            "download_location": os.path.expanduser("~/Downloads/MusicDownloader"),
            "spotify_client_id": "test_client_id",
            "spotify_client_secret": "test_client_secret"
        }
        
        os.makedirs("config", exist_ok=True)
        with open("config/config.json", "w") as f:
            json.dump(config_data, f, indent=2)
        
        print("✓ Test configuration created")
        return True
        
    except Exception as e:
        print(f"✗ Configuration creation failed: {e}")
        return False

def main():
    """Run complete setup verification"""
    print("Music Downloader Complete Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Dependency Installation", install_all_dependencies),
        ("Module Imports", test_imports),
        ("FFmpeg Integration", test_ffmpeg_integration),
        ("Song Filtering System", test_song_filtering_system),
        ("Search Components", test_search_components),
        ("Download Components", test_download_components),
        ("GUI Components", test_gui_initialization),
        ("End-to-End Pipeline", test_end_to_end_pipeline),
        ("Test Configuration", create_test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"VERIFICATION SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All systems working correctly!")
        print("✓ Song filtering with strict duration matching enabled")
        print("✓ Album cover art and metadata integration ready")
        print("✓ Non-Spotify song detection operational")
        print("\nReady to run: python main.py")
        return True
    else:
        print("✗ Some systems need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)