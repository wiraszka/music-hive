#!/usr/bin/env python3
"""
Test script to verify cover art loading flow
Simulates the complete search and metadata matching process
"""

from search_spotify import SpotifySearch
from utils.song_filter import SongFilter
import os

def test_spotify_matching_flow():
    """Test the complete Spotify matching flow that the GUI uses"""
    print("Testing Complete Spotify Matching Flow")
    print("=" * 45)
    
    # Check if we have Spotify credentials
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ No Spotify credentials found")
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to test")
        return
    
    try:
        spotify = SpotifySearch()
        song_filter = SongFilter()
        
        # Simulate a YouTube search result (what would come from YouTube)
        test_youtube_result = {
            'title': 'ILLENIUM - Beautiful Creatures (Official Video)',
            'duration': '4:01',
            'channel': 'ILLENIUM',
            'url': 'https://youtube.com/watch?v=test123'
        }
        
        print(f"1. YouTube Result: {test_youtube_result['title']}")
        
        # Step 2: Search Spotify (what GUI does in _search_spotify_for_youtube_result)
        print("\n2. Searching Spotify for metadata...")
        
        # Extract clean query for Spotify search
        from process_text import clean_search_query, extract_song_info
        
        clean_title = clean_search_query(test_youtube_result['title'])
        artist, song_name = extract_song_info(clean_title)
        
        print(f"   Extracted: artist='{artist}', song='{song_name}'")
        
        # Search Spotify with multiple strategies (like the GUI does)
        spotify_results = []
        
        search_queries = []
        if artist and song_name:
            search_queries.append(f'artist:"{artist}" track:"{song_name}"')
            search_queries.append(f"{artist} {song_name}")
        search_queries.append(clean_title)
        
        for query in search_queries:
            print(f"   Trying Spotify search: '{query}'")
            results = spotify.search_track(query, limit=3)
            if results:
                spotify_results = results
                print(f"   ✓ Found {len(results)} Spotify results")
                break
        
        if not spotify_results:
            print("   ❌ No Spotify results found")
            return
        
        # Step 3: Find best match (what GUI does in _find_best_spotify_match)
        print("\n3. Finding best Spotify match...")
        
        best_match = None
        best_score = 0
        
        from fuzzywuzzy import fuzz
        youtube_title = test_youtube_result['title'].lower()
        
        for i, track in enumerate(spotify_results):
            track_name = track.get('title', '').lower()
            artist_name = track.get('artist', '').lower()
            
            # Score calculation (matches GUI logic)
            title_similarity = fuzz.ratio(youtube_title, track_name)
            score = title_similarity * 0.4
            
            if artist_name and 'illenium' in youtube_title:
                score += 25
            
            print(f"   Result {i+1}: '{track.get('title')}' by '{track.get('artist')}'")
            print(f"     Score: {score:.1f}% (title: {title_similarity:.1f}%)")
            
            if score > best_score:
                best_score = score
                best_match = track
        
        if not best_match or best_score <= 40:
            print(f"   ❌ No match above confidence threshold (best: {best_score:.1f}%)")
            return
        
        print(f"   ✓ Best match: '{best_match.get('title')}' by '{best_match.get('artist')}' ({best_score:.1f}%)")
        
        # Step 4: Check song filter decision (what GUI does in should_include_result)
        print("\n4. Checking song filter decision...")
        
        should_include, reason, confidence = song_filter.should_include_result(
            test_youtube_result, best_match, 'illenium beautiful creatures'
        )
        
        print(f"   Include: {should_include}")
        print(f"   Reason: {reason}")
        print(f"   Confidence: {confidence:.1f}%")
        
        # Step 5: Check cover art availability (what GUI checks for album_art loading)
        print("\n5. Checking cover art availability...")
        
        if 'spotify' in reason and best_match:
            print("   ✓ Result qualifies for Spotify metadata (contains 'spotify')")
            
            if 'album_art' in best_match and best_match['album_art']:
                album_art_url = best_match['album_art']
                print(f"   ✓ Album art URL found: {album_art_url[:50]}...")
                
                # Test if URL is accessible
                import requests
                try:
                    response = requests.head(album_art_url, timeout=3)
                    if response.status_code == 200:
                        print(f"   ✓ Album art URL is accessible ({response.status_code})")
                        print("\n🎉 COMPLETE SUCCESS: Cover art should load in GUI!")
                    else:
                        print(f"   ❌ Album art URL not accessible ({response.status_code})")
                except Exception as e:
                    print(f"   ❌ Cannot access album art URL: {e}")
            else:
                print("   ❌ No album_art field in Spotify result")
                print(f"   Available fields: {list(best_match.keys())}")
        else:
            print(f"   ❌ Result doesn't qualify for Spotify metadata (reason: {reason})")
        
        print("\n" + "=" * 45)
        print("Summary:")
        print(f"✓ Spotify search: Working")
        print(f"✓ Best match found: {best_match.get('title') if best_match else 'None'}")
        print(f"✓ Song filter decision: {reason} ({confidence:.1f}%)")
        print(f"✓ Cover art URL: {'Available' if best_match and best_match.get('album_art') else 'Missing'}")
        
        if should_include and 'spotify' in reason and best_match and best_match.get('album_art'):
            print("\n✅ All conditions met - cover art SHOULD appear in GUI")
        else:
            print("\n❌ Some condition failed - cover art will NOT appear")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spotify_matching_flow()