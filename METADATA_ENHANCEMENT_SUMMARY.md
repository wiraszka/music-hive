# YouTube Metadata Extraction Implementation

## New Metadata Strategy

The system now implements a **three-tier metadata approach** for downloads:

### 1. Priority 1: High-Confidence Spotify Metadata
- Songs marked as `high_confidence_spotify` or `medium_confidence_spotify`
- Full Spotify metadata including album art, release date, genres
- **Example**: "ILLENIUM - Beautiful Creatures" gets complete Spotify tags

### 2. Priority 2: YouTube-Extracted Metadata
- Songs without Spotify matches but with clear ARTIST - TITLE format
- Extracts artist and song name from video title
- **Example**: "Nirvana - Something In The Way (ILLENIUM Remix)" gets:
  - Artist: "Nirvana"
  - Title: "Something In The Way (ILLENIUM Remix)"
  - Album: "" (empty)

### 3. Priority 3: YouTube-Fallback Metadata
- Songs that don't match ARTIST - TITLE pattern
- Uses cleaned video title and intelligent channel detection
- **Example**: "Amazing Song" from "ArtistName" channel gets:
  - Artist: "ArtistName" (if channel looks like artist)
  - Title: "Amazing Song"
  - Album: "" (empty)

## Technical Implementation

### GUI Changes (`gui/download_tab.py`)
- Added `_extract_youtube_metadata()` function
- Added `_clean_title_for_metadata()` function
- Enhanced download logic to use extracted metadata for non-Spotify matches
- Debug logging shows metadata source and extraction process

### Downloader Changes (`downloader.py`)
- Enhanced metadata application to handle three sources
- Progress indicators differentiate metadata types:
  - "Applying Spotify metadata..."
  - "Applying extracted metadata..."
  - "Applying basic metadata..."

### Title Cleaning Features
Removes common YouTube decorations:
- "(Official Video)", "[Official Audio]"
- "(Music Video)", "(Lyrics)", "(HD)", "(4K)"
- Handles both parentheses and brackets
- Preserves important info like remix credits

### Channel Intelligence
- Detects artist channels vs generic music channels
- Generic indicators: "music", "official", "records", "entertainment"
- Short channel names (≤3 words) without generic terms = likely artist
- Falls back to "Unknown Artist" for clearly generic channels

## Results

**Before**: Remixes downloaded with no metadata tags
```
File: nirvana_something_in_the_way_illenium_remix.mp3
Artist: (empty)
Title: (empty)
Album: (empty)
```

**After**: Remixes get proper extracted metadata
```
File: nirvana_something_in_the_way_illenium_remix.mp3
Artist: Nirvana
Title: Something In The Way (ILLENIUM Remix)
Album: (empty)
Source: youtube_extracted
```

## Debug Output Examples

**High-Confidence Spotify Match:**
```
[METADATA DEBUG] Applying Spotify metadata for high_confidence_spotify match
[DOWNLOAD DEBUG] Applying Spotify metadata to: Beautiful_Creatures.mp3
```

**YouTube Extraction:**
```
[METADATA DEBUG] Extracting basic metadata from YouTube title for youtube_only result
[EXTRACT DEBUG] Successfully extracted: 'Something In The Way (ILLENIUM Remix)' by 'Nirvana'
[DOWNLOAD DEBUG] Applying YouTube-extracted metadata to: something_in_the_way_remix.mp3
```

This ensures all downloaded files have meaningful metadata while maintaining security against incorrect Spotify matches for remixes and covers.