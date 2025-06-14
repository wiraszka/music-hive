#!/usr/bin/env python3
"""
Test file cleanup functionality
"""

import os
import tempfile
import shutil
from downloader import Downloader, AudioQuality

def test_file_cleanup():
    """Test that temporary files are cleaned up after download"""
    temp_dir = tempfile.mkdtemp()
    try:
        downloader = Downloader(temp_dir)
        
        # Short test video
        test_url = 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
        
        print("Starting download test...")
        success, result = downloader.download(test_url, quality=AudioQuality.MEDIUM)
        
        if success:
            print(f"Download successful: {os.path.basename(result)}")
            
            # Check what files exist
            files = os.listdir(temp_dir)
            print(f"Files in directory: {files}")
            
            # Count file types
            webm_count = sum(1 for f in files if f.endswith('.webm'))
            mp3_count = sum(1 for f in files if f.endswith('.mp3'))
            
            print(f"WebM files: {webm_count}")
            print(f"MP3 files: {mp3_count}")
            
            if webm_count == 0 and mp3_count == 1:
                print("✓ Cleanup successful - only MP3 remains")
            else:
                print("! Some temporary files may remain")
                
        else:
            print(f"Download failed: {result}")
            
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_file_cleanup()