#!/usr/bin/env python3
"""
Test download functionality with fixed FFmpeg setup
"""

import os
import tempfile
import shutil
from downloader import Downloader, AudioQuality

def test_ffmpeg_setup():
    """Test that FFmpeg is properly configured"""
    print("Testing FFmpeg setup...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        downloader = Downloader(temp_dir)
        
        # Check FFmpeg detection
        ffmpeg_exe, ffprobe_exe = downloader._get_ffmpeg_executables()
        print(f"FFmpeg: {ffmpeg_exe}")
        print(f"FFprobe: {ffprobe_exe}")
        
        # Verify both exist
        ffmpeg_ok = ffmpeg_exe and os.path.exists(ffmpeg_exe)
        ffprobe_ok = ffprobe_exe and os.path.exists(ffprobe_exe)
        
        print(f"FFmpeg available: {ffmpeg_ok}")
        print(f"FFprobe available: {ffprobe_ok}")
        
        # Check yt-dlp configuration
        ffmpeg_location = downloader.ydl_opts.get('ffmpeg_location')
        print(f"yt-dlp ffmpeg_location: {ffmpeg_location}")
        
        return ffmpeg_ok and ffprobe_ok
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_download_short_video():
    """Test downloading a very short video to verify functionality"""
    print("\nTesting download functionality...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        downloader = Downloader(temp_dir)
        
        # Use a very short test video (Creative Commons)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll (short clip)
        
        def progress_callback(percent, message):
            print(f"Progress: {percent:.1f}% - {message}")
        
        print(f"Attempting download from: {test_url}")
        success, result = downloader.download(
            test_url, 
            quality=AudioQuality.MEDIUM,
            progress_callback=progress_callback
        )
        
        print(f"Download success: {success}")
        if success:
            print(f"Downloaded file: {result}")
            print(f"File exists: {os.path.exists(result)}")
            if os.path.exists(result):
                file_size = os.path.getsize(result)
                print(f"File size: {file_size} bytes")
        else:
            print(f"Download error: {result}")
        
        return success
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Run all tests"""
    print("FFmpeg and Download Functionality Test")
    print("=" * 40)
    
    # Test FFmpeg setup
    ffmpeg_ok = test_ffmpeg_setup()
    
    if not ffmpeg_ok:
        print("FFmpeg setup failed - cannot proceed with download test")
        return False
    
    # Test download
    download_ok = test_download_short_video()
    
    print("\n" + "=" * 40)
    print(f"FFmpeg setup: {'PASS' if ffmpeg_ok else 'FAIL'}")
    print(f"Download test: {'PASS' if download_ok else 'FAIL'}")
    print(f"Overall: {'PASS' if ffmpeg_ok and download_ok else 'FAIL'}")
    
    return ffmpeg_ok and download_ok

if __name__ == "__main__":
    main()