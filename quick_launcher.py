#!/usr/bin/env python3
"""
Quick Launcher for MusicHub
Verifies setup and launches the application
"""

import sys
import importlib
from pathlib import Path

def verify_dependencies():
    """Verify all required dependencies are available"""
    print("Verifying dependencies...")
    
    required = [
        ('yt_dlp', 'YouTube downloader'),
        ('mutagen', 'Audio metadata'),
        ('spotipy', 'Spotify integration'),
        ('fuzzywuzzy', 'Song matching'),
        ('Levenshtein', 'Text similarity'),
        ('imageio_ffmpeg', 'Audio processing')
    ]
    
    missing = []
    for module, description in required:
        try:
            importlib.import_module(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"✗ {description} - MISSING")
            missing.append(module)
    
    return len(missing) == 0

def verify_song_filtering():
    """Verify song filtering system"""
    print("\nVerifying song filtering...")
    
    try:
        from utils.song_filter import SongFilter
        filter_system = SongFilter()
        
        # Quick confidence test
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
        
        print(f"✓ Advanced filtering system ({confidence:.1f}% test match)")
        return True
        
    except Exception as e:
        print(f"✗ Filtering system error: {e}")
        return False

def setup_directories():
    """Create application directories"""
    print("\nSetting up directories...")
    
    directories = ['downloads', 'library', 'temp', 'config']
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True, parents=True)
        print("✓ Directory structure ready")
        return True
    except Exception as e:
        print(f"✗ Directory setup failed: {e}")
        return False

def verify_ffmpeg():
    """Verify FFmpeg is available"""
    print("\nVerifying audio processing...")
    
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✓ FFmpeg ready at {ffmpeg_exe}")
        return True
    except Exception as e:
        print(f"✗ FFmpeg error: {e}")
        return False

def main():
    """Quick setup and verification"""
    print("MusicHub Quick Launcher")
    print("=" * 30)
    
    checks = [
        verify_dependencies,
        verify_song_filtering, 
        setup_directories,
        verify_ffmpeg
    ]
    
    for check in checks:
        if not check():
            print("\nSetup incomplete - some components need attention")
            return False
    
    print("\n" + "=" * 30)
    print("✓ MusicHub ready to launch!")
    print("\nAdvanced features enabled:")
    print("• Song filtering with ±5s duration matching")
    print("• Album cover art integration")
    print("• Confidence scoring system")
    print("• Non-Spotify song detection")
    
    return True

if __name__ == "__main__":
    if main():
        print(f"\nLaunching: python main.py")
        import os
        os.system("python main.py")
    else:
        sys.exit(1)