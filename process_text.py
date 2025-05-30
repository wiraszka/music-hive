"""
Text Processing Module
Provides functions for text processing and normalization
"""

import re
import unicodedata
from typing import Tuple

def clean_filename(filename: str) -> str:
    """
    Clean a filename by removing invalid characters
    
    Args:
        filename: The filename to clean
        
    Returns:
        Cleaned filename
    """
    # Replace characters not allowed in filenames
    invalid_chars = r'[\\/*?:"<>|]'
    cleaned = re.sub(invalid_chars, '', filename)
    
    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Trim leading/trailing spaces
    cleaned = cleaned.strip()
    
    # Limit length to avoid issues with long filenames
    max_length = 100
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
        
    return cleaned

def normalize_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing accents
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_song_info(title: str) -> Tuple[str, str]:
    """
    Try to extract artist and song name from a video title
    
    Args:
        title: Video title
        
    Returns:
        Tuple of (artist, song_name)
    """
    # Common patterns in music video titles
    patterns = [
        # Artist - Song
        r'^(.*?)\s*-\s*(.*?)$',
        # Artist "Song"
        r'^(.*?)\s*"(.*?)"',
        # Artist 'Song'
        r'^(.*?)\s*\'(.*?)\'',
        # Artist: Song
        r'^(.*?)\s*:\s*(.*?)$',
        # Artist | Song
        r'^(.*?)\s*\|\s*(.*?)$',
        # Song by Artist
        r'^(.*?)\s*by\s*(.*?)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            groups = match.groups()
            # Handle "Song by Artist" pattern differently
            if pattern == r'^(.*?)\s*by\s*(.*?)$':
                return groups[1].strip(), groups[0].strip()
            else:
                return groups[0].strip(), groups[1].strip()
    
    # If no pattern matches, return the whole title as song name with empty artist
    return "", title.strip()

def clean_search_query(query: str) -> str:
    """
    Clean and normalize a search query
    
    Args:
        query: The search query
        
    Returns:
        Cleaned query
    """
    # Remove common terms that interfere with music search
    noise_terms = [
        'official', 'video', 'music video', 'lyric video', 'audio',
        'official audio', 'official music video', 'lyrics', 'hq', 'hd',
        'full album', 'full song', 'live', 'cover'
    ]
    
    query_lower = query.lower()
    
    for term in noise_terms:
        # Match the term as a whole word
        pattern = r'\b' + re.escape(term) + r'\b'
        query_lower = re.sub(pattern, '', query_lower)
    
    # Remove parentheses and their contents (often contains "Official Video" etc.)
    query_lower = re.sub(r'\([^)]*\)', '', query_lower)
    query_lower = re.sub(r'\[[^\]]*\]', '', query_lower)
    
    # Remove extra whitespace
    query_lower = re.sub(r'\s+', ' ', query_lower).strip()
    
    return query_lower
