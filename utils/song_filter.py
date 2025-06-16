"""
Song filtering and matching utilities
Provides functions to filter YouTube results and match them with Spotify metadata
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from fuzzywuzzy import fuzz
from process_text import clean_search_query, extract_song_info, normalize_text

class SongFilter:
    """Handles filtering and matching of YouTube results with Spotify metadata"""
    
    # Keywords that indicate non-song content
    EXCLUSION_KEYWORDS = [
        'live', 'concert', 'tour', 'performance', 'festival',
        'album', 'full album', 'playlist', 'compilation',
        'cover version', 'covers', 'instrumental', 'karaoke',
        'reaction', 'review', 'interview', 'behind the scenes',
        'making of', 'documentary', 'trailer', 'teaser',
        'how to', 'tutorial', 'lesson', 'guide'
    ]
    
    # More specific patterns for filtering (case insensitive)
    EXCLUSION_PATTERNS = [
        r'\blive\b.*\bconcert\b',
        r'\bfull\s+album\b',
        r'\bcover\s+by\b',
        r'\breaction\s+to\b',
        r'\blyrics?\s+video\b',
        r'\bofficial\s+trailer\b'
    ]
    
    # Minimum and maximum duration for songs (in seconds)
    MIN_DURATION = 30   # 30 seconds
    MAX_DURATION = 600  # 10 minutes
    
    # Matching thresholds
    HIGH_CONFIDENCE_THRESHOLD = 80
    MEDIUM_CONFIDENCE_THRESHOLD = 60
    YOUTUBE_RELEVANCE_THRESHOLD = 65  # Lowered to include more legitimate songs
    NON_SPOTIFY_THRESHOLD = 70        # Lowered to include remixes and unofficial releases
    
    # Duration tolerance (±5 seconds)
    DURATION_TOLERANCE = 5
    
    def __init__(self):
        pass
    
    def filter_youtube_results(self, youtube_results: List[Dict[str, Any]], 
                             search_query: str) -> List[Dict[str, Any]]:
        """
        Filter YouTube results to include only legitimate songs
        
        Args:
            youtube_results: Raw YouTube search results
            search_query: Original search query
            
        Returns:
            Filtered list of YouTube results
        """
        # First pass: filter for valid songs with adaptive criteria
        valid_results = []
        is_artist_query = self._is_artist_search(search_query)
        
        for result in youtube_results:
            if self._is_valid_song(result, search_query, relaxed=is_artist_query):
                valid_results.append(result)
        
        # Second pass: remove duplicates
        deduplicated_results = self._remove_duplicates(valid_results, search_query)
        
        # Third pass: for artist searches, ensure variety
        if self._is_artist_search(search_query):
            deduplicated_results = self._ensure_artist_variety(deduplicated_results, search_query)
        
        # Final pass: limit to exactly 5 results for consistent UI
        if len(deduplicated_results) > 5:
            deduplicated_results = deduplicated_results[:5]
        
        return deduplicated_results
    
    def _is_valid_song(self, result: Dict[str, Any], search_query: str, relaxed: bool = False) -> bool:
        """
        Check if a YouTube result represents a valid song
        
        Args:
            result: YouTube result dictionary
            search_query: Original search query
            relaxed: Whether to use relaxed filtering criteria (for artist searches)
            
        Returns:
            True if the result appears to be a song
        """
        title = result.get('title', '').lower()
        duration = self._parse_duration(result.get('duration', ''))
        
        # Check duration bounds
        if duration < self.MIN_DURATION or duration > self.MAX_DURATION:
            return False
        
        # Check for exclusion keywords (more lenient for artist searches)
        if self._contains_exclusion_keywords(title, relaxed=relaxed):
            return False
        
        # Check relevance to search query with adaptive threshold
        relevance_score = self._calculate_youtube_relevance(result, search_query)
        threshold = 25 if relaxed else 40  # Lower threshold for artist searches
        if relevance_score < threshold:
            return False
        
        return True
    
    def _contains_exclusion_keywords(self, title: str, relaxed: bool = False) -> bool:
        """Check if title contains keywords indicating non-song content"""
        title_lower = title.lower()
        
        # Check basic exclusion keywords (but skip "remix" - that's handled separately)
        for keyword in self.EXCLUSION_KEYWORDS:
            if keyword in title_lower:
                return True
        
        # Check exclusion patterns
        for pattern in self.EXCLUSION_PATTERNS:
            if re.search(pattern, title_lower):
                return True
        
        # Additional specific patterns (more lenient for artist searches)
        if not relaxed:
            additional_patterns = [
                r'\blive\s+(at|in|from)\b',
                r'\b\d+\s*hour[s]?\b',  # Multi-hour content
                r'\bmix\s*#?\d+\b',     # DJ mixes (but not remixes)
                r'\bfull\s+concert\b',
                r'\bsetlist\b',
                r'\bmashup\s+of\b'
            ]
            
            for pattern in additional_patterns:
                if re.search(pattern, title_lower):
                    return True
        
        return False
    
    def _remove_duplicates(self, results: List[Dict[str, Any]], search_query: str) -> List[Dict[str, Any]]:
        """Remove duplicate results based on title similarity and duration"""
        if not results:
            return results
        
        unique_results = []
        
        for result in results:
            title = result.get('title', '')
            duration = result.get('duration', '')
            
            # Extract core song information for comparison
            core_title = self._extract_core_title(title)
            
            # Check if this is similar to any existing result
            is_duplicate = False
            for i, existing in enumerate(unique_results):
                existing_core = self._extract_core_title(existing.get('title', ''))
                
                # Check title similarity and duration proximity
                title_similarity = fuzz.ratio(core_title.lower(), existing_core.lower())
                duration_similar = self._are_durations_similar(duration, existing.get('duration', ''))
                
                if title_similarity > 80 and duration_similar:
                    # This is a duplicate, decide which to keep
                    if self._is_better_source(result, existing):
                        unique_results[i] = result
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def _extract_core_title(self, title: str) -> str:
        """Extract core song information from title, removing decorative elements"""
        core = title
        
        # Remove common decorative elements
        core = re.sub(r'\s*\(official.*?\)\s*', '', core, flags=re.IGNORECASE)
        core = re.sub(r'\s*\[official.*?\]\s*', '', core, flags=re.IGNORECASE)
        core = re.sub(r'\s*(official|music|lyric|lyrics)\s*(video|audio)?\s*', '', core, flags=re.IGNORECASE)
        core = re.sub(r'\s*\|\s*.*$', '', core)  # Remove everything after |
        core = re.sub(r'\s*-\s*official.*$', '', core, flags=re.IGNORECASE)
        core = re.sub(r'\s+', ' ', core).strip()
        
        return core
    
    def _are_durations_similar(self, duration1: str, duration2: str) -> bool:
        """Check if two duration strings are similar (within 10 seconds)"""
        try:
            seconds1 = self._parse_duration(duration1)
            seconds2 = self._parse_duration(duration2)
            return abs(seconds1 - seconds2) <= 10
        except:
            return duration1 == duration2
    
    def _is_better_source(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> bool:
        """Determine if result1 is from a better source than result2"""
        channel1 = result1.get('channel', '').lower()
        channel2 = result2.get('channel', '').lower()
        
        # Prefer official channels
        official_indicators = ['official', 'records', 'music', 'vevo']
        
        result1_official = any(indicator in channel1 for indicator in official_indicators)
        result2_official = any(indicator in channel2 for indicator in official_indicators)
        
        if result1_official and not result2_official:
            return True
        elif result2_official and not result1_official:
            return False
        
        # If both or neither are official, prefer shorter titles (usually cleaner)
        title1_len = len(result1.get('title', ''))
        title2_len = len(result2.get('title', ''))
        
        return title1_len < title2_len
    
    def _is_artist_search(self, search_query: str) -> bool:
        """Determine if the search query is for an artist rather than a specific song"""
        query_lower = search_query.lower().strip()
        
        # Common patterns that indicate artist searches
        artist_patterns = [
            r'^[a-zA-Z\s&]+$',  # Just letters, spaces, and ampersands (no dashes, parentheses)
            r'^[a-zA-Z\s&]+ songs?$',
            r'^[a-zA-Z\s&]+ hits?$',
            r'^best of [a-zA-Z\s&]+$'
        ]
        
        for pattern in artist_patterns:
            if re.match(pattern, query_lower):
                # Additional check: no common song title indicators
                if ' - ' not in query_lower and '(' not in query_lower and '[' not in query_lower:
                    return True
        
        return False
    
    def _ensure_artist_variety(self, results: List[Dict[str, Any]], search_query: str) -> List[Dict[str, Any]]:
        """For artist searches, ensure variety of songs rather than duplicates"""
        if len(results) <= 5:
            return results
        
        # Group results by similarity and pick the best from each group
        song_groups = {}
        
        for result in results:
            title = result.get('title', '')
            
            # Extract potential song name (remove artist name and extra info)
            song_part = self._extract_song_from_title(title, search_query)
            
            # Group similar songs together
            grouped = False
            for existing_song in song_groups:
                if fuzz.ratio(song_part.lower(), existing_song.lower()) > 70:
                    song_groups[existing_song].append(result)
                    grouped = True
                    break
            
            if not grouped:
                song_groups[song_part] = [result]
        
        # Pick the best result from each group
        diverse_results = []
        for song_name, group_results in song_groups.items():
            # Sort by source quality and pick the best
            best_result = max(group_results, key=lambda r: self._score_result_quality(r))
            diverse_results.append(best_result)
        
        # Sort by overall relevance and return top results
        diverse_results.sort(key=lambda r: self._calculate_youtube_relevance(r, search_query), reverse=True)
        
        return diverse_results[:10]  # Return top 10 diverse results
    
    def _extract_song_from_title(self, title: str, artist_query: str) -> str:
        """Extract the song name from a title, removing artist name"""
        title_clean = title
        
        # Remove artist name if it appears at the beginning
        artist_words = artist_query.lower().split()
        title_lower = title.lower()
        
        for i in range(len(artist_words), 0, -1):
            artist_phrase = ' '.join(artist_words[:i])
            if title_lower.startswith(artist_phrase):
                title_clean = title[len(artist_phrase):].strip(' -')
                break
        
        # Remove common prefixes/suffixes
        title_clean = re.sub(r'^\s*[-–]\s*', '', title_clean)  # Remove leading dash
        title_clean = re.sub(r'\s*\(.*?\)\s*$', '', title_clean)  # Remove trailing parentheses
        title_clean = re.sub(r'\s*\[.*?\]\s*$', '', title_clean)  # Remove trailing brackets
        title_clean = re.sub(r'\s*(official|music|video|audio|lyric|lyrics)\s*$', '', title_clean, flags=re.IGNORECASE)
        
        return title_clean.strip()
    
    def _score_result_quality(self, result: Dict[str, Any]) -> float:
        """Score a result based on quality indicators"""
        score = 0.0
        
        title = result.get('title', '').lower()
        channel = result.get('channel', '').lower()
        
        # Official channel indicators
        if any(word in channel for word in ['official', 'records', 'music', 'vevo']):
            score += 3.0
        
        # Official video indicators
        if any(word in title for word in ['official video', 'official audio']):
            score += 2.0
        
        # Avoid low-quality indicators
        if any(word in title for word in ['cover', 'karaoke', 'instrumental']):
            score -= 2.0
        
        # Prefer cleaner titles (less promotional text)
        if len(title) < 100:  # Reasonable title length
            score += 1.0
        
        return score
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse duration string to seconds
        
        Args:
            duration_str: Duration in format like "3:45" or "1:23:45"
            
        Returns:
            Duration in seconds
        """
        if not duration_str or duration_str == "00:00":
            return 0
        
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except (ValueError, AttributeError):
            return 0
        
        return 0
    
    def calculate_spotify_match_confidence(self, youtube_result: Dict[str, Any], 
                                         spotify_track: Dict[str, Any]) -> float:
        """
        Calculate confidence score for Spotify-YouTube matching
        
        Args:
            youtube_result: YouTube video data
            spotify_track: Spotify track data
            
        Returns:
            Confidence score (0-100)
        """
        # Extract data
        youtube_title = youtube_result.get('title', '')
        youtube_duration = self._parse_duration(youtube_result.get('duration', ''))
        
        spotify_name = spotify_track.get('name', '')
        spotify_artists = [artist.get('name', '') for artist in spotify_track.get('artists', [])]
        spotify_duration_ms = spotify_track.get('duration_ms', 0)
        spotify_duration = spotify_duration_ms // 1000  # Convert to seconds
        
        # Title similarity (40% weight)
        title_score = self._calculate_title_similarity(youtube_title, spotify_name, spotify_artists)
        
        # Duration similarity (35% weight)
        duration_score = self._calculate_duration_similarity(youtube_duration, spotify_duration)
        
        # Artist similarity (25% weight)
        artist_score = self._calculate_artist_similarity(youtube_title, spotify_artists)
        
        # Weighted confidence score
        confidence = (title_score * 0.4 + duration_score * 0.35 + artist_score * 0.25)
        
        return min(100, max(0, confidence))
    
    def _calculate_title_similarity(self, youtube_title: str, spotify_name: str, 
                                  spotify_artists: List[str]) -> float:
        """Calculate similarity between YouTube title and Spotify track name"""
        # Clean titles
        youtube_clean = clean_search_query(youtube_title)
        spotify_clean = clean_search_query(spotify_name)
        
        # Direct title comparison
        title_similarity = fuzz.ratio(youtube_clean, spotify_clean)
        
        # Check if Spotify track name appears in YouTube title
        if spotify_clean.lower() in youtube_clean.lower():
            title_similarity = max(title_similarity, 85)
        
        # Check if main artist appears in YouTube title
        artist_in_title = False
        if spotify_artists:
            main_artist = clean_search_query(spotify_artists[0])
            if main_artist.lower() in youtube_clean.lower():
                artist_in_title = True
        
        # Boost score if artist is mentioned
        if artist_in_title:
            title_similarity = min(100, title_similarity + 15)
        
        return title_similarity
    
    def _calculate_duration_similarity(self, youtube_duration: int, spotify_duration: int) -> float:
        """Calculate similarity between YouTube and Spotify durations"""
        if youtube_duration == 0 or spotify_duration == 0:
            return 0
        
        duration_diff = abs(youtube_duration - spotify_duration)
        
        if duration_diff <= self.DURATION_TOLERANCE:
            return 100
        elif duration_diff <= 10:
            return 80
        elif duration_diff <= 20:
            return 60
        elif duration_diff <= 30:
            return 40
        else:
            return 0
    
    def _calculate_artist_similarity(self, youtube_title: str, spotify_artists: List[str]) -> float:
        """Calculate how well Spotify artists match YouTube title"""
        if not spotify_artists:
            return 50  # Neutral score if no artist data
        
        youtube_clean = clean_search_query(youtube_title).lower()
        max_similarity = 0
        
        for artist in spotify_artists:
            artist_clean = clean_search_query(artist).lower()
            
            # Check if artist name appears in title
            if artist_clean in youtube_clean:
                max_similarity = max(max_similarity, 90)
            else:
                # Fuzzy match artist name
                similarity = fuzz.partial_ratio(artist_clean, youtube_clean)
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_youtube_relevance(self, youtube_result: Dict[str, Any], 
                                   search_query: str) -> float:
        """
        Calculate how relevant a YouTube result is to the search query
        (for non-Spotify songs)
        
        Args:
            youtube_result: YouTube video data
            search_query: Original search query
            
        Returns:
            Relevance score (0-100)
        """
        title = youtube_result.get('title', '')
        channel = youtube_result.get('channel', '')
        
        # Clean strings
        title_clean = clean_search_query(title).lower()
        query_clean = clean_search_query(search_query).lower()
        
        # Direct query matching (50% weight)
        query_similarity = fuzz.ratio(query_clean, title_clean)
        
        # Check if query words appear in title (30% weight)
        query_words = query_clean.split()
        title_words = title_clean.split()
        word_matches = sum(1 for word in query_words if word in title_words)
        word_score = (word_matches / len(query_words)) * 100 if query_words else 0
        
        # Check for song patterns (20% weight)
        pattern_score = self._check_song_patterns(title)
        
        # Weighted relevance score
        relevance = (query_similarity * 0.5 + word_score * 0.3 + pattern_score * 0.2)
        
        return min(100, max(0, relevance))
    
    def _check_song_patterns(self, title: str) -> float:
        """Check if title follows common song naming patterns"""
        title_lower = title.lower()
        
        # Common song patterns
        patterns = [
            r'[\w\s]+ - [\w\s]+',           # "Artist - Song"
            r'[\w\s]+ by [\w\s]+',          # "Song by Artist"
            r'[\w\s]+\s*\|\s*[\w\s]+',      # "Artist | Song"
            r'[\w\s]+:\s*[\w\s]+',          # "Artist: Song"
            r'\(official.*\)',              # "(official video/audio)"
            r'\[official.*\]',              # "[official video/audio]"
            r'[\w\s]+\s*\([\w\s]+\s+remix\)',  # "Song (Artist Remix)"
            r'[\w\s]+\s+remix',             # "Song Artist Remix"
        ]
        
        pattern_matches = 0
        for pattern in patterns:
            if re.search(pattern, title_lower):
                pattern_matches += 1
        
        # Boost score for remix patterns specifically
        remix_patterns = [
            r'\w+\s+remix',                 # "ILLENIUM Remix"
            r'\(.*remix.*\)',               # "(ILLENIUM Remix)"
            r'remix\s+by\s+\w+',           # "Remix by ILLENIUM"
        ]
        
        is_remix = any(re.search(pattern, title_lower) for pattern in remix_patterns)
        
        # Score based on pattern matches
        if pattern_matches >= 2 or is_remix:
            return 90
        elif pattern_matches == 1:
            return 75
        else:
            return 40
    
    def should_include_result(self, youtube_result: Dict[str, Any], 
                            spotify_track: Optional[Dict[str, Any]], 
                            search_query: str) -> Tuple[bool, str, float]:
        """
        Determine if a YouTube result should be included in final results
        
        Args:
            youtube_result: YouTube video data
            spotify_track: Spotify track data (None if no match)
            search_query: Original search query
            
        Returns:
            Tuple of (should_include, reason, confidence_score)
        """
        if spotify_track:
            # Calculate Spotify match confidence
            confidence = self.calculate_spotify_match_confidence(youtube_result, spotify_track)
            
            if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                return True, "high_confidence_spotify", confidence
            elif confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
                return True, "medium_confidence_spotify", confidence
            else:
                # Low Spotify confidence, check if it's still a good YouTube match
                youtube_relevance = self._calculate_youtube_relevance(youtube_result, search_query)
                if youtube_relevance >= self.YOUTUBE_RELEVANCE_THRESHOLD:
                    return True, "youtube_only", youtube_relevance
                else:
                    return False, "low_confidence", confidence
        else:
            # No Spotify match, check YouTube relevance
            youtube_relevance = self._calculate_youtube_relevance(youtube_result, search_query)
            if youtube_relevance >= self.NON_SPOTIFY_THRESHOLD:
                return True, "youtube_only", youtube_relevance
            else:
                return False, "irrelevant", youtube_relevance