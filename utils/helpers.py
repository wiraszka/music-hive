"""
Helper utility functions
"""

import os
import sys
import logging
import platform
from typing import Optional

logger = logging.getLogger(__name__)

def get_platform() -> str:
    """
    Get the current platform
    
    Returns:
        String identifying the platform: 'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'

def get_app_data_dir() -> str:
    """
    Get the application data directory for the current platform
    
    Returns:
        Path to the application data directory
    """
    platform_name = get_platform()
    app_name = "MusicDownloader"
    
    if platform_name == 'windows':
        return os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), app_name)
    elif platform_name == 'macos':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', app_name)
    else:  # linux and others
        return os.path.join(os.path.expanduser('~'), f'.{app_name.lower()}')

def ensure_dir_exists(directory: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {str(e)}")
        return False

def format_filesize(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    
    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.2f} KB"
    
    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{size_mb:.2f} MB"
    
    size_gb = size_mb / 1024
    return f"{size_gb:.2f} GB"

def format_duration(duration_seconds: int) -> str:
    """
    Format duration in human-readable format
    
    Args:
        duration_seconds: Duration in seconds
        
    Returns:
        Formatted duration string (MM:SS or HH:MM:SS)
    """
    minutes, seconds = divmod(duration_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
