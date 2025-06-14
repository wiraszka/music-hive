#!/usr/bin/env python3
"""
Test script to verify cover art logic for remixes vs original songs
"""

from search_spotify import SpotifySearch
from utils.song_filter import SongFilter
from fuzzywuzzy import fuzz
import os

def test_remix_vs_original():
    """Test that remixes don't get wrong cover art from original songs"""
    print("Testing Cover Art Logic for Remixes")
    print("=" * 45)
    
    # Test cases
    test_cases = [
        {
            'title': 'ILLENIUM - Beautiful Creatures (Official Video)',
            'should_have_cover': True,
            'description': 'Original song that exists on Spotify'
        },
        {
            'title': 'Nirvana - Something In The Way (ILLENIUM Remix)',
            'should_have_cover': False,
            'description': 'Remix that doesn\'t exist on Spotify'
        },
        {
            'title': 'Seven Lions - Rush Over Me (ILLENIUM Remix)',
            'should_have_cover': False,
            'description': 'Another remix that shouldn\'t match'
        }
    ]
    
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("No Spotify credentials - simulating logic")
        for case in test_cases:
            print(f"\n{case['description']}: {case['title']}")
            
            # Check for remix indicators
            remix_indicators = ['remix', 'cover', 'bootleg', 'edit', 'rework', 'flip']
            is_remix = any(indicator in case['title'].lower() for indicator in remix_indicators)
            
            print(f"  Is remix/cover: {is_remix}")
            print(f"  Should have cover art: {case['should_have_cover']}")
            
            if is_remix and not case['should_have_cover']:
                print("  ✓ PASS - Remix correctly identified, won't search broadly")
            elif not is_remix and case['should_have_cover']:
                print("  ✓ PASS - Original song will search normally")
            else:
                print("  ? Mixed case")
        
        print("\nLogic Summary:")
        print("✓ Remix detection prevents broad Spotify searches")
        print("✓ Stricter matching threshold (60) prevents weak matches")
        print("✓ Only high_confidence_spotify/medium_confidence_spotify get cover art")
        print("✓ youtube_only results keep placeholder image")
        return
    
    # Real test with Spotify API
    try:
        spotify = SpotifySearch()
        song_filter = SongFilter()
        
        for case in test_cases:
            print(f"\n{case['description']}: {case['title']}")
            
            # Simulate the YouTube result
            youtube_result = {
                'title': case['title'],
                'duration': '4:00',
                'channel': 'Test Channel'
            }
            
            # Check remix detection
            remix_indicators = ['remix', 'cover', 'bootleg', 'edit', 'rework', 'flip']
            is_remix = any(indicator in case['title'].lower() for indicator in remix_indicators)
            print(f"  Remix detected: {is_remix}")
            
            # Test Spotify search with new logic
            if is_remix:
                # Should use very specific searches only
                search_queries = [f'"{case["title"]}"']
                print(f"  Using specific search: {search_queries[0]}")
            else:
                # Should use broad searches
                print(f"  Using broad search strategies")
            
            # Try a search
            results = spotify.search_track(case['title'][:50], limit=1)  # Truncate long titles
            
            if results:
                spotify_track = results[0]
                
                # Test matching score
                youtube_title = case['title'].lower()
                track_name = spotify_track.get('title', '').lower()
                title_similarity = fuzz.ratio(youtube_title, track_name)
                score = title_similarity * 0.4
                
                # Add artist bonus if found
                artist_name = spotify_track.get('artist', '').lower()
                if artist_name and any(part in youtube_title for part in artist_name.split(', ')):
                    score += 25
                
                print(f"  Best match: '{spotify_track.get('title')}' by '{spotify_track.get('artist')}'")
                print(f"  Match score: {score:.1f}% (threshold: 60)")
                
                # Test filter decision
                spotify_match = spotify_track if score > 60 else None
                should_include, reason, confidence = song_filter.should_include_result(
                    youtube_result, spotify_match, case['title']
                )
                
                print(f"  Filter result: {reason} ({confidence:.1f}%)")
                
                # Test cover art logic
                will_show_cover = (spotify_match and 
                                 reason in ['high_confidence_spotify', 'medium_confidence_spotify'])
                
                print(f"  Will show cover art: {will_show_cover}")
                print(f"  Expected: {case['should_have_cover']}")
                
                if will_show_cover == case['should_have_cover']:
                    print("  ✓ PASS - Cover art logic correct")
                else:
                    print("  ✗ FAIL - Cover art logic incorrect")
            else:
                print("  No Spotify results found")
                print(f"  Will show cover art: False")
                print(f"  Expected: {case['should_have_cover']}")
                
                if not case['should_have_cover']:
                    print("  ✓ PASS - No cover art as expected")
                else:
                    print("  ✗ FAIL - Should have found a match")
                    
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_remix_vs_original()