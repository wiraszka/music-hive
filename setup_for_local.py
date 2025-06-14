#!/usr/bin/env python3
"""
Local Setup Script for MusicHub
Optimized for downloading and running locally on desktop
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path

# All required dependencies with exact versions
DEPENDENCIES = [
    'yt-dlp==2025.4.30',
    'mutagen==1.47.0', 
    'spotipy==2.25.1',
    'requests==2.32.3',
    'PyQt6==6.9.0',
    'fuzzywuzzy==0.18.0',
    'python-levenshtein==0.27.1',
    'imageio-ffmpeg==0.6.0'
]

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install all required packages"""
    print("Installing dependencies...")
    
    # Update pip first
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    # Install each dependency
    failed = []
    for package in DEPENDENCIES:
        package_name = package.split('==')[0]
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package_name}")
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} failed")
            failed.append(package)
    
    if failed:
        print(f"\n⚠️  Failed to install: {', '.join([p.split('==')[0] for p in failed])}")
        print("Try running manually: pip install " + " ".join(failed))
        return False
    
    print("✅ All dependencies installed")
    return True

def verify_imports():
    """Verify all critical imports work"""
    print("\nVerifying imports...")
    
    imports = [
        ('yt_dlp', 'YouTube downloader'),
        ('mutagen.mp3', 'Audio metadata'),
        ('spotipy', 'Spotify integration'),
        ('fuzzywuzzy.fuzz', 'Song matching'),
        ('Levenshtein', 'Text similarity'),
        ('imageio_ffmpeg', 'Audio processing'),
        ('PyQt6.QtWidgets', 'GUI framework')
    ]
    
    failed = []
    for module, description in imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_song_filtering():
    """Test the complete song filtering system"""
    print("\nTesting song filtering system...")
    
    try:
        from utils.song_filter import SongFilter
        from fuzzywuzzy import fuzz
        
        # Initialize filter
        filter_system = SongFilter()
        print("✅ Filter system initialized")
        
        # Test confidence calculation
        youtube_result = {
            'title': 'Artist Name - Song Title (Official Audio)',
            'duration': '3:30',
            'channel': 'Artist Official'
        }
        
        spotify_track = {
            'name': 'Song Title',
            'artists': [{'name': 'Artist Name'}],
            'duration_ms': 210000
        }
        
        confidence = filter_system.calculate_spotify_match_confidence(youtube_result, spotify_track)
        print(f"✅ Confidence calculation: {confidence:.1f}%")
        
        # Test inclusion logic
        should_include, reason, conf = filter_system.should_include_result(
            youtube_result, spotify_track, "artist name song title"
        )
        print(f"✅ Inclusion logic: {should_include} ({reason})")
        
        # Test fuzzy matching
        similarity = fuzz.ratio("artist song title", "song title by artist")
        print(f"✅ Fuzzy matching: {similarity}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Song filtering failed: {e}")
        return False

def test_download_system():
    """Test download and audio processing"""
    print("\nTesting download system...")
    
    try:
        from downloader import Downloader, AudioQuality
        import tempfile
        
        # Test downloader initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = Downloader(temp_dir)
            print("✅ Downloader initialized")
        
        # Test FFmpeg integration
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✅ FFmpeg available: {os.path.basename(ffmpeg_exe)}")
        
        # Test quality options
        qualities = [q.value for q in AudioQuality]
        print(f"✅ Audio qualities: {', '.join(qualities)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Download system failed: {e}")
        return False

def create_config():
    """Create default configuration"""
    print("\nCreating configuration...")
    
    try:
        # Create config directory
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Default download location
        home = Path.home()
        downloads_dir = home / "Downloads" / "MusicHub"
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        config = {
            "download_location": str(downloads_dir),
            "spotify_client_id": "",
            "spotify_client_secret": "",
            "audio_quality": "320k",
            "max_search_results": 20,
            "confidence_threshold": 60.0,
            "duration_tolerance": 5,
            "enable_album_art": True,
            "filter_live_performances": True,
            "filter_covers": True
        }
        
        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration created: {config_file}")
        print(f"✅ Download folder: {downloads_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def create_directories():
    """Create application directories"""
    print("\nCreating directories...")
    
    directories = [
        "downloads",
        "library",
        "temp",
        "config",
        "assets"
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(exist_ok=True, parents=True)
            print(f"✅ Created: {directory}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory creation failed: {e}")
        return False

def show_platform_notes():
    """Show platform-specific notes"""
    system = platform.system()
    
    print(f"\nPlatform: {system}")
    
    if system == "Windows":
        print("📝 Windows Notes:")
        print("   • All dependencies should install automatically")
        print("   • Run: python main.py")
        
    elif system == "Darwin":  # macOS
        print("📝 macOS Notes:")
        print("   • All dependencies should install automatically")
        print("   • Run: python3 main.py")
        
    elif system == "Linux":
        print("📝 Linux Notes:")
        print("   • If GUI issues occur, install: sudo apt-get install python3-pyqt6")
        print("   • Run: python3 main.py")
    
    print("\n🔑 API Setup Required:")
    print("   1. Get Spotify API keys at: https://developer.spotify.com/dashboard")
    print("   2. Add to config/config.json or set environment variables")

def main():
    """Main setup process"""
    print("MusicHub Local Setup")
    print("=" * 40)
    print("Setting up for local desktop use...\n")
    
    # Setup steps
    steps = [
        ("Python Version", check_python),
        ("Dependencies", install_dependencies),
        ("Import Verification", verify_imports),
        ("Song Filtering", test_song_filtering),
        ("Download System", test_download_system),
        ("Configuration", create_config),
        ("Directories", create_directories)
    ]
    
    failed_steps = []
    for step_name, step_func in steps:
        print(f"{step_name}:")
        print("-" * 25)
        
        if step_func():
            print(f"✅ {step_name} completed\n")
        else:
            print(f"❌ {step_name} failed\n")
            failed_steps.append(step_name)
    
    # Show results
    print("=" * 40)
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Advanced Features Ready:")
        print("   • Song filtering with ±5s duration matching")
        print("   • Album cover art integration")
        print("   • Confidence scoring system")
        print("   • Non-Spotify song detection")
        print("   • Zero-setup FFmpeg integration")
        
        show_platform_notes()
        
        print(f"\n▶️  Ready to launch: python main.py")
        
    else:
        print(f"⚠️  Setup completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"   • {step}")
        print("\nReview the errors above and run setup again.")
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)