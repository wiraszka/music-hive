#!/usr/bin/env python3
"""
Test download functionality with FFmpeg
"""

from downloader import Downloader, AudioQuality
import os
import tempfile

def test_ffmpeg_detection():
    """Test if FFmpeg can be detected"""
    print("Testing FFmpeg detection...")
    
    # Create a temporary download directory
    with tempfile.TemporaryDirectory() as temp_dir:
        downloader = Downloader(temp_dir)
        
        # Check if FFmpeg location is detected
        ffmpeg_path = downloader._find_ffmpeg()
        if ffmpeg_path:
            print(f"FFmpeg found at: {ffmpeg_path}")
        else:
            print("FFmpeg using system default")
        
        # Check yt-dlp configuration
        print(f"yt-dlp config includes ffmpeg_location: {'ffmpeg_location' in downloader.ydl_opts}")
        
        return True

def test_short_download():
    """Test downloading a very short video for verification"""
    print("\nTesting download with a short video...")
    
    # Use a short test video (public domain)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - very short
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Download directory: {temp_dir}")
        
        try:
            downloader = Downloader(temp_dir)
            
            def progress_callback(percent, message):
                print(f"Progress: {percent:.1f}% - {message}")
            
            success, result = downloader.download(
                test_url, 
                quality=AudioQuality.MEDIUM,
                progress_callback=progress_callback
            )
            
            if success:
                print(f"Download successful: {result}")
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"File size: {file_size} bytes")
                    return True
                else:
                    print(f"File not found at: {result}")
                    return False
            else:
                print(f"Download failed: {result}")
                return False
                
        except Exception as e:
            print(f"Download test error: {e}")
            return False

def main():
    """Run download tests"""
    print("Testing download functionality with FFmpeg...")
    print("=" * 50)
    
    ffmpeg_ok = test_ffmpeg_detection()
    download_ok = test_short_download()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print(f"FFmpeg detection: {'PASS' if ffmpeg_ok else 'FAIL'}")
    print(f"Download test: {'PASS' if download_ok else 'FAIL'}")
    
    if ffmpeg_ok and download_ok:
        print("\nDownload functionality is working correctly!")
    else:
        print("\nSome issues need to be addressed.")

if __name__ == "__main__":
    main()