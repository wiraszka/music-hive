"""
Download tab for the main application window
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QProgressBar, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox
)
# QAction import removed as it's not needed anymore
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush, QPainter

from downloader import Downloader, AudioQuality
from search_youtube import YouTubeSearch
from search_spotify import SpotifySearch, search_track_on_spotify
from process_text import clean_filename, extract_song_info, clean_search_query
from utils.config import Config
from utils.song_filter import SongFilter

logger = logging.getLogger(__name__)

class DownloadWorker(QThread):
    """Worker thread for downloading music"""
    # Define signals
    progress_updated = pyqtSignal(float, str)  # percent, status message
    download_complete = pyqtSignal(bool, str)  # success, file_path or error_message
    
    def __init__(self, video_url: str, download_dir: str, 
                 song_info: Optional[Dict[str, Any]] = None,
                 quality: AudioQuality = AudioQuality.BEST):
        """
        Initialize download worker
        
        Args:
            video_url: YouTube video URL
            download_dir: Directory to save the downloaded file
            song_info: Optional metadata to apply
            quality: Audio quality for download
        """
        super().__init__()
        self.video_url = video_url
        self.download_dir = download_dir
        self.song_info = song_info
        self.quality = quality
    
    def run(self):
        """Execute the download task"""
        try:
            downloader = Downloader(self.download_dir)
            success, result = downloader.download(
                self.video_url,
                self.song_info,
                self.quality,
                self.progress_updated.emit
            )
            self.download_complete.emit(success, result)
        except Exception as e:
            logger.error(f"Download worker error: {str(e)}")
            self.progress_updated.emit(0, f"Error: {str(e)}")
            self.download_complete.emit(False, str(e))


class DownloadTab(QWidget):
    """Download tab widget"""
    
    def __init__(self, config: Config):
        """
        Initialize download tab
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.config = config
        self.download_location = config.download_location
        
        # Initialize search clients
        self.youtube = YouTubeSearch()
        self.spotify = SpotifySearch()
        self.song_filter = SongFilter()
        
        # Current search results
        self.youtube_results = []
        self.spotify_results = []
        
        # Current selected track info
        self.selected_youtube_index = -1
        self.selected_spotify_index = -1
        
        # Download worker
        self.download_worker = None
        
        # Set background image
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "downloads_bg.jpg")
        self.bg_pixmap = None
        if os.path.exists(self.bg_image_path):
            self.bg_pixmap = QPixmap(self.bg_image_path)
            self.setAutoFillBackground(False)  # We'll handle painting manually
        
        # Initialize UI
        self._init_ui()
    
    def paintEvent(self, event):
        """Custom paint event to draw scaled background image"""
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter = QPainter(self)
            
            # Get widget size
            widget_rect = self.rect()
            
            # Scale pixmap to fit widget while maintaining aspect ratio
            scaled_pixmap = self.bg_pixmap.scaled(
                widget_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center the image if it's larger than the widget
            x_offset = (widget_rect.width() - scaled_pixmap.width()) // 2
            y_offset = (widget_rect.height() - scaled_pixmap.height()) // 2
            
            # Draw the scaled background image
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            
            painter.end()
        
        # Call parent paint event
        super().paintEvent(event)
    
    def _init_ui(self):
        """Initialize the user interface"""
        # Create outer layout with large margins for centering
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add left spacer (25% of width)
        outer_layout.addStretch(1)
        
        # Create center container for middle 50% of screen
        center_container = QWidget()
        center_container.setMaximumWidth(800)  # Fixed max width for consistency
        center_container.setMinimumWidth(600)  # Minimum width for smaller screens
        
        main_layout = QVBoxLayout(center_container)
        main_layout.setContentsMargins(20, 30, 20, 30)
        main_layout.setSpacing(10)  # Reduced spacing between sections
        
        # Create small spacer to push content down slightly
        main_layout.addStretch(1)
        
        # Add "MUSIC is LIFE" text, styled like the original app
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 50)  # Add more space below logo
        
        # MUSIC text
        music_label = QLabel("MUSIC")
        music_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        music_label.setStyleSheet("""
            font-size: 80px;
            font-weight: bold;
            color: white;
            letter-spacing: 5px;
            text-transform: uppercase;
        """)
        logo_layout.addWidget(music_label)
        
        # is text (in badge)
        is_container = QWidget()
        is_container.setFixedWidth(150)
        is_container.setStyleSheet("""
            background-color: #e9c46a;
            border-radius: 5px;
        """)
        is_layout = QHBoxLayout(is_container)
        is_layout.setContentsMargins(20, 5, 20, 5)
        
        is_label = QLabel("is")
        is_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        is_label.setStyleSheet("""
            font-size: 30px;
            font-style: italic;
            color: #333;
        """)
        is_layout.addWidget(is_label)
        
        is_container_layout = QHBoxLayout()
        is_container_layout.addStretch()
        is_container_layout.addWidget(is_container)
        is_container_layout.addStretch()
        
        logo_layout.addLayout(is_container_layout)
        
        # LIFE text
        life_label = QLabel("LIFE")
        life_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        life_label.setStyleSheet("""
            font-size: 100px;
            font-weight: bold;
            color: white;
            letter-spacing: 5px;
            text-transform: uppercase;
        """)
        logo_layout.addWidget(life_label)
        
        main_layout.addWidget(logo_container)
        
        # Search section - make it centered
        search_container = QWidget()
        search_container.setObjectName("search_container")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setMinimumHeight(40)
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Enter song name or artist")
        self.search_input.returnPressed.connect(self._search)
        search_layout.addWidget(self.search_input, 1)  # Stretch to fill available space
        
        search_button = QPushButton("Search")
        search_button.setObjectName("search_button")
        search_button.setMinimumHeight(40)
        search_button.setMinimumWidth(100)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #333333;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
            QPushButton:pressed {
                background-color: #b3b3b3;
            }
        """)
        search_button.clicked.connect(self._search)
        search_layout.addWidget(search_button)
        
        # Add search container directly to main layout
        main_layout.addWidget(search_container)
        
        # Results section - hidden until search is performed
        self.results_container = QWidget()
        self.results_container.setVisible(False)  # Initially hidden
        self.results_container.setMaximumHeight(400)  # Maximum height to prevent overflow
        # Remove minimum height - let it size based on content
        self.results_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Main results layout
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        results_layout.setSpacing(0)  # Remove spacing between items
        
        # Results list without scroll area - display all items directly
        self.results_list = QWidget()
        self.results_list.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.results_list_layout = QVBoxLayout(self.results_list)
        self.results_list_layout.setContentsMargins(0, 0, 0, 0)
        self.results_list_layout.setSpacing(0)  # Remove spacing between items
        # No stretch - let results list size naturally
        
        results_layout.addWidget(self.results_list)
        
        # Add results container to main layout
        main_layout.addWidget(self.results_container)
        
        # Download options - placed below results
        options_layout = QHBoxLayout()
        
        quality_label = QLabel("Quality:")
        options_layout.addWidget(quality_label)
        
        self.quality_dropdown = QComboBox()
        self.quality_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QComboBox:hover {
                border: 1px solid #999999;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666666;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                selection-background-color: #f0f0f0;
                selection-color: #333333;
            }
        """)
        self.quality_dropdown.addItem("Best (320k)", AudioQuality.BEST)
        self.quality_dropdown.addItem("High (256k)", AudioQuality.HIGH)
        self.quality_dropdown.addItem("Medium (192k)", AudioQuality.MEDIUM)
        self.quality_dropdown.addItem("Low (128k)", AudioQuality.LOW)
        options_layout.addWidget(self.quality_dropdown)
        
        options_layout.addStretch()
        
        self.download_location_label = QLabel(f"Download location: {self.download_location}")
        options_layout.addWidget(self.download_location_label)
        
        change_location_button = QPushButton("Change")
        change_location_button.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #333333;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
            QPushButton:pressed {
                background-color: #b3b3b3;
            }
        """)
        change_location_button.clicked.connect(self._change_download_location)
        options_layout.addWidget(change_location_button)
        
        main_layout.addLayout(options_layout)
        
        # Download button - hidden until search is performed
        self.download_button = QPushButton("Download")
        self.download_button.setVisible(False)  # Initially hidden
        self.download_button.setEnabled(False)
        self.download_button.setMinimumHeight(40)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #333333;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
            QPushButton:pressed {
                background-color: #b3b3b3;
            }
            QPushButton:disabled {
                background-color: #e6e6e6;
                color: #999999;
            }
        """)
        self.download_button.clicked.connect(self._download_selected)
        main_layout.addWidget(self.download_button)
        
        # Progress section
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        progress_layout.addWidget(self.status_label)
        
        main_layout.addLayout(progress_layout)
        
        # Add a stretch to push everything up
        main_layout.addStretch(2)
        
        # Add center container to outer layout
        outer_layout.addWidget(center_container, 2)  # Middle 50% gets weight 2
        
        # Add right spacer (25% of width)
        outer_layout.addStretch(1)
    
    def _search(self):
        """Handle search button click"""
        query = self.search_input.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Search", "Please enter a search term.")
            return
        
        # Clear previous results and result list widget
        self.youtube_results = []
        self.selected_youtube_index = -1
        self.download_button.setEnabled(False)
        
        # Clear individual result metadata
        if hasattr(self, 'result_metadata'):
            self.result_metadata.clear()
        if hasattr(self, 'processed_results'):
            self.processed_results.clear()
        
        # Clear the results list
        self._clear_results_list()
        
        # Show loading indicator (could add a spinner here)
        self.status_label.setText("Searching...")
        self.status_label.setVisible(True)
        
        # Search YouTube
        try:
            raw_youtube_results = self.youtube.search(query, limit=15)  # Get more results for filtering
            
            # Filter YouTube results to include only legitimate songs
            filtered_youtube_results = self.song_filter.filter_youtube_results(raw_youtube_results, query)
            
            # Limit to exactly 5 results for consistent UI
            if len(filtered_youtube_results) > 5:
                filtered_youtube_results = filtered_youtube_results[:5]
            
            # If no results after filtering
            if not filtered_youtube_results:
                self.status_label.setVisible(False)
                QMessageBox.information(self, "No Results", "No song results found for your search term.")
                return
            
            # Process each result with Spotify matching and inclusion logic
            self.youtube_results = []
            self.processed_results = []  # Store results with metadata and confidence info
            high_confidence_found = 0
            
            for result in filtered_youtube_results:
                # Search Spotify for this result
                spotify_track = self._search_spotify_for_youtube_result(result)
                
                # Determine if this result should be included
                should_include, reason, confidence = self.song_filter.should_include_result(
                    result, spotify_track, query
                )
                
                if should_include:
                    self.youtube_results.append(result)
                    self.processed_results.append({
                        'youtube_result': result,
                        'spotify_track': spotify_track,
                        'reason': reason,
                        'confidence': confidence
                    })
                    
                    # Count high-confidence matches for early termination
                    if reason in ['high_confidence_spotify', 'medium_confidence_spotify']:
                        high_confidence_found += 1
                        
                    # Early termination: stop if we have enough good results
                    if len(self.processed_results) >= 3 and high_confidence_found >= 2:
                        print(f"[OPTIMIZATION] Early termination: Found {high_confidence_found} high-confidence matches")
                        break
            
            # Hide loading indicator
            self.status_label.setVisible(False)
            
            # Check if we have any valid results after processing
            if not self.youtube_results:
                QMessageBox.information(self, "No Valid Results", 
                                      "No matching songs found. Try refining your search query.")
                return
                
        except Exception as e:
            self.status_label.setVisible(False)
            QMessageBox.critical(self, "Search Error", f"YouTube search failed: {str(e)}")
            return
            
        # Clear previous results first
        self._clear_results_list()
        
        # Show results container and download button
        self.results_container.setVisible(True)
        self.download_button.setVisible(True)
        
        # Force layout update
        self.results_container.updateGeometry()
        
        # Populate results list with filtered and processed results
        for i, processed_result in enumerate(self.processed_results):
            # Create result item with processed metadata
            self._add_result_item_with_metadata(i, processed_result)
        
        # Force another layout update after adding items
        self.results_list.updateGeometry()
        self.results_container.updateGeometry()
                
        # Don't auto-select first result - let user choose
    
    def _set_no_metadata_image(self, cover_label: QLabel):
        """Set a placeholder image for results without Spotify metadata"""
        # Create a simple text-based placeholder
        pixmap = QPixmap(37, 37)
        pixmap.fill(Qt.GlobalColor.lightGray)
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "No\nArt")
        painter.end()
        
        cover_label.setPixmap(pixmap)
    
    def _search_spotify_for_youtube_result(self, youtube_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search Spotify metadata for a YouTube result with multiple strategies"""
        try:
            video_title = youtube_result.get('title', '')
            print(f"[SPOTIFY DEBUG] Searching for: {video_title}")
            
            # Check if this is a remix/cover that likely doesn't exist on Spotify
            remix_indicators = ['remix', 'cover', 'bootleg', 'edit', 'rework', 'flip']
            title_lower = video_title.lower()
            is_remix = any(indicator in title_lower for indicator in remix_indicators)
            
            if is_remix:
                print(f"[SPOTIFY DEBUG] Detected remix/cover - using stricter matching")
            
            # Strategy 1: Extract artist and song name
            clean_title = clean_search_query(video_title)
            artist, song_name = extract_song_info(clean_title)
            
            search_queries = []
            
            if artist and song_name:
                # For remixes, be more specific to avoid matching original songs
                if is_remix:
                    # Only search for the exact remix version
                    search_queries.append(f'"{video_title}"')
                    search_queries.append(clean_title)
                else:
                    # Primary search with both artist and song
                    search_queries.append(f'artist:"{artist}" track:"{song_name}"')
                    search_queries.append(f"{artist} {song_name}")
                    # Fallback: just song name if artist search fails
                    search_queries.append(f'track:"{song_name}"')
            
            # Strategy 2: Clean title search (skip for remixes to avoid false matches)
            if not is_remix:
                search_queries.append(clean_title)
                
                # Strategy 3: Remove common YouTube decorations
                simplified_title = self._simplify_youtube_title(video_title)
                if simplified_title != clean_title:
                    search_queries.append(simplified_title)
            
            # Try each search strategy
            for query in search_queries:
                print(f"[SPOTIFY DEBUG] Trying query: {query}")
                spotify_results = self.spotify.search_track(query, limit=3)
                
                if spotify_results:
                    # Find the best match from results
                    best_match = self._find_best_spotify_match(spotify_results, youtube_result)
                    if best_match:
                        print(f"[SPOTIFY DEBUG] Found match: {best_match.get('name')} by {best_match.get('artists', [{}])[0].get('name', 'Unknown')}")
                        return best_match
            
            print(f"[SPOTIFY DEBUG] No Spotify match found for: {video_title}")
            return None
                    
        except Exception as e:
            print(f"[SPOTIFY DEBUG] Search failed: {str(e)}")
            return None
    
    def _simplify_youtube_title(self, title: str) -> str:
        """Remove YouTube-specific decorations from title"""
        import re
        simplified = title
        
        # Remove common YouTube elements
        simplified = re.sub(r'\s*\(official.*?\)\s*', ' ', simplified, flags=re.IGNORECASE)
        simplified = re.sub(r'\s*\[official.*?\]\s*', ' ', simplified, flags=re.IGNORECASE)
        simplified = re.sub(r'\s*(official|music|lyric|lyrics)\s*(video|audio)?\s*', ' ', simplified, flags=re.IGNORECASE)
        simplified = re.sub(r'\s*\|\s*.*$', '', simplified)  # Remove everything after |
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        
        return simplified
    
    def _find_best_spotify_match(self, spotify_results: List[Dict[str, Any]], 
                                youtube_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best Spotify match from search results"""
        if not spotify_results:
            return None
        
        from fuzzywuzzy import fuzz
        
        youtube_title = youtube_result.get('title', '').lower()
        youtube_duration = self._parse_duration_to_seconds(youtube_result.get('duration', ''))
        
        best_match = None
        best_score = 0
        
        for track in spotify_results:
            score = 0
            
            # Get track name - our Spotify search returns 'title' field
            track_name = track.get('title', '').lower()
            if not track_name:
                print(f"[SPOTIFY DEBUG] No track name found in: {track}")
                continue
                
            title_similarity = fuzz.ratio(youtube_title, track_name)
            score += title_similarity * 0.4
            
            # Get artist name - our Spotify search returns 'artist' field as string
            artist_name = track.get('artist', '')
            artist_found = False
            if artist_name:
                # Check if any part of the artist name appears in YouTube title
                artist_parts = artist_name.lower().split(', ')  # Handle multiple artists like "ILLENIUM, MAX"
                for artist_part in artist_parts:
                    artist_part = artist_part.strip()
                    if artist_part and artist_part in youtube_title:
                        score += 25
                        artist_found = True
                        print(f"[SPOTIFY DEBUG] Artist match found: '{artist_part}' in YouTube title")
                        break
                
                # Additional check: see if YouTube title starts with artist name
                main_artist = artist_parts[0].strip() if artist_parts else ''
                if main_artist and youtube_title.startswith(main_artist):
                    if not artist_found:  # Don't double-count
                        score += 25
                        artist_found = True
                        print(f"[SPOTIFY DEBUG] Artist prefix match: '{main_artist}'")
                
                if not artist_found:
                    print(f"[SPOTIFY DEBUG] No artist match: looking for '{artist_name}' in '{youtube_title}'")
            
            # Check duration similarity - now included in enhanced Spotify results
            spotify_duration = track.get('duration_ms', 0) / 1000
            if youtube_duration > 0 and spotify_duration > 0:
                duration_diff = abs(youtube_duration - spotify_duration)
                if duration_diff <= 5:
                    score += 30
                elif duration_diff <= 15:
                    score += 15
            
            print(f"[SPOTIFY DEBUG] Track: '{track_name}' by '{artist_name}' - Score: {score:.1f}")
            
            if score > best_score:
                best_score = score
                best_match = track
        
        # Return match only if confidence is high enough - stricter threshold for better accuracy
        min_threshold = 60  # Require stronger match to avoid wrong album art
        if best_match and best_score > min_threshold:
            print(f"[SPOTIFY DEBUG] Selected best match with score: {best_score:.1f}")
            return best_match
        else:
            print(f"[SPOTIFY DEBUG] No match found with sufficient confidence (best: {best_score:.1f}, required: {min_threshold})")
            return None
    
    def _parse_duration_to_seconds(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        if not duration_str:
            return 0
        
        try:
            # Handle formats like "3:45" or "1:23:45"
            parts = duration_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                return int(duration_str)
        except ValueError:
            return 0
    
    def _add_result_item_with_metadata(self, index: int, processed_result: Dict[str, Any]):
        """Add a result item with processed metadata and confidence information"""
        youtube_result = processed_result['youtube_result']
        spotify_track = processed_result['spotify_track']
        reason = processed_result['reason']
        confidence = processed_result['confidence']
        
        # Create the visual result item with confidence indicator
        self._add_result_item_with_confidence(index, youtube_result, reason, confidence)
        
        # Update cover art based on metadata availability - only for high confidence Spotify matches
        if spotify_track and reason in ['high_confidence_spotify', 'medium_confidence_spotify']:
            # Store metadata for download
            if not hasattr(self, 'result_metadata'):
                self.result_metadata = {}
            self.result_metadata[index] = spotify_track
            
            # Load album cover - use the album_art field from our Spotify search
            if 'album_art' in spotify_track and spotify_track['album_art']:
                cover_url = spotify_track['album_art']
                print(f"[COVER ART DEBUG] Loading cover for {reason} result {index}: {cover_url}")
                self._load_cover_art(index, cover_url)
            else:
                print(f"[COVER ART DEBUG] No album art found for result {index}: {spotify_track.keys()}")
        else:
            # For youtube_only results or low confidence matches, no cover art
            print(f"[COVER ART DEBUG] No cover art for {reason} result {index} - keeping placeholder")
        # The "No Art" placeholder is already set in _add_result_item
    
    def _add_result_item_with_confidence(self, index: int, result: Dict[str, Any], 
                                       reason: str, confidence: float):
        """Add a result item with confidence indicator"""
        print(f"[GUI DEBUG] _add_result_item_with_confidence called for index {index}")
        # Create result item widget
        result_item = QWidget()
        result_item.setObjectName(f"result_item_{index}")
        result_item.setProperty("resultIndex", index)
        result_item.setCursor(Qt.CursorShape.PointingHandCursor)
        result_item.setFixedHeight(45)  # More compact height
        result_item.setStyleSheet("""
            QWidget[resultIndex] {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 0px;
                margin: 0px;
            }
            QWidget[resultIndex]:hover {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
            }
        """)
        
        # Create layout for result item - with image space
        item_layout = QHBoxLayout(result_item)
        item_layout.setContentsMargins(8, 4, 8, 4)  # Reduced padding
        
        # Album cover art (left side)
        cover_label = QLabel()
        cover_label.setFixedSize(37, 37)  # Square image to fit in 45px height item
        cover_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
        """)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Store cover label reference for later metadata updates
        result_item.cover_label = cover_label
        
        # Set default "no metadata" image
        self._set_no_metadata_image(cover_label)
        
        item_layout.addWidget(cover_label)
        
        # Result details (remaining width)
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)  # Remove spacing between title and info
        
        # Title with confidence indicator
        title_text = result['title']
        if reason == 'high_confidence_spotify':
            title_text += " ✓"  # High confidence indicator
        elif reason == 'medium_confidence_spotify':
            title_text += " ~"  # Medium confidence indicator
        
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            font-weight: bold;
            color: #1a1a1a;
            font-size: 13px;
        """)
        title_label.setWordWrap(True)
        details_layout.addWidget(title_label)
        
        # Channel and duration on same line
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        
        # Channel
        channel_label = QLabel(result['channel'])
        channel_label.setStyleSheet("""
            color: #555555;
            font-size: 11px;
        """)
        info_layout.addWidget(channel_label)
        
        info_layout.addStretch()  # Push duration to right
        
        # Duration
        duration_label = QLabel(result.get('duration', '00:00'))
        duration_label.setStyleSheet("""
            color: #777777;
            font-size: 11px;
        """)
        info_layout.addWidget(duration_label)
        
        # Add confidence score as small text
        if confidence > 0:
            confidence_label = QLabel(f"({confidence:.0f}%)")
            confidence_label.setStyleSheet("""
                color: #999999;
                font-size: 10px;
            """)
            info_layout.addWidget(confidence_label)
        
        details_layout.addLayout(info_layout)
        
        item_layout.addWidget(details_widget)
        
        # Add to results list using the new layout structure
        if hasattr(self, 'results_list_layout'):
            # Add widget directly to the end (no stretch element anymore)
            self.results_list_layout.addWidget(result_item)
        
        # Connect click event
        result_item.mousePressEvent = lambda event, idx=index: self._select_result(idx)
    
    def _load_cover_art(self, result_index: int, cover_url: str):
        """Download and display album cover art for a specific result"""
        print(f"[COVER ART DEBUG] Starting download for result {result_index}: {cover_url}")
        
        try:
            # Download the image
            response = requests.get(cover_url, timeout=5)
            response.raise_for_status()
            print(f"[COVER ART DEBUG] Successfully downloaded image data: {len(response.content)} bytes")
            
            # Create QPixmap from image data
            pixmap = QPixmap()
            success = pixmap.loadFromData(QByteArray(response.content))
            
            if not success:
                print(f"[COVER ART DEBUG] Failed to create QPixmap from image data")
                return
                
            print(f"[COVER ART DEBUG] Created QPixmap: {pixmap.width()}x{pixmap.height()}")
            
            # Scale to fit the label size
            scaled_pixmap = pixmap.scaled(37, 37, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            print(f"[COVER ART DEBUG] Scaled to: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
            # Find the result item and update its cover
            if hasattr(self, 'results_list_layout'):
                print(f"[COVER ART DEBUG] Searching through {self.results_list_layout.count()} layout items")
                for i in range(self.results_list_layout.count()):
                    item = self.results_list_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        widget_index = widget.property('resultIndex') if hasattr(widget, 'property') else None
                        print(f"[COVER ART DEBUG] Checking widget {i}: resultIndex={widget_index}, target={result_index}")
                        
                        if (hasattr(widget, 'property') and 
                            widget.property('resultIndex') == result_index and
                            hasattr(widget, 'cover_label')):
                            print(f"[COVER ART DEBUG] Found matching widget! Setting pixmap...")
                            widget.cover_label.setPixmap(scaled_pixmap)
                            print(f"[COVER ART DEBUG] Successfully set album cover for result {result_index}")
                            return
                            
                print(f"[COVER ART DEBUG] No matching widget found for result {result_index}")
            else:
                print(f"[COVER ART DEBUG] No results_list_layout found")
                            
        except Exception as e:
            print(f"[COVER ART DEBUG] Failed to load cover art for result {result_index}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Keep the "no metadata" placeholder
    
    def _clear_results_list(self):
        """Clear all results from the list"""
        # Clear all widgets from the layout
        if hasattr(self, 'results_list_layout'):
            # Remove all widgets from the layout
            while self.results_list_layout.count() > 0:
                item = self.results_list_layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()
    
    def _add_result_item(self, index: int, result: Dict[str, Any]):
        """
        Add a result item to the results list
        
        Args:
            index: Result index
            result: Result data from YouTube search
        """
        print(f"[GUI DEBUG] _add_result_item called for index {index}")
        # Create result item widget
        result_item = QWidget()
        result_item.setObjectName(f"result_item_{index}")
        result_item.setProperty("resultIndex", index)
        result_item.setCursor(Qt.CursorShape.PointingHandCursor)
        result_item.setFixedHeight(45)  # More compact height
        result_item.setStyleSheet("""
            QWidget[resultIndex] {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 0px;
                margin: 0px;
            }
            QWidget[resultIndex]:hover {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
            }
        """)
        
        # Create layout for result item - with image space
        item_layout = QHBoxLayout(result_item)
        item_layout.setContentsMargins(8, 4, 8, 4)  # Reduced padding
        
        # Album cover art (left side)
        cover_label = QLabel()
        cover_label.setFixedSize(37, 37)  # Square image to fit in 45px height item
        cover_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f5f5f5;
            }
        """)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Store cover label reference for later metadata updates
        result_item.cover_label = cover_label
        
        # Set default "no metadata" image
        self._set_no_metadata_image(cover_label)
        
        item_layout.addWidget(cover_label)
        
        # Result details (remaining width)
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)  # Remove spacing between title and info
        
        # Title
        title_label = QLabel(result['title'])
        title_label.setStyleSheet("""
            font-weight: bold;
            color: #1a1a1a;
            font-size: 13px;
        """)
        title_label.setWordWrap(True)
        details_layout.addWidget(title_label)
        
        # Channel and duration on same line
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        
        # Channel
        channel_label = QLabel(result['channel'])
        channel_label.setStyleSheet("""
            color: #555555;
            font-size: 11px;
        """)
        info_layout.addWidget(channel_label)
        
        info_layout.addStretch()  # Push duration to right
        
        # Duration
        duration_label = QLabel(result.get('duration', '00:00'))
        duration_label.setStyleSheet("""
            color: #777777;
            font-size: 11px;
            font-weight: bold;
        """)
        info_layout.addWidget(duration_label)
        
        details_layout.addLayout(info_layout)
        
        item_layout.addWidget(details_widget)
        
        # Add to results list using the new layout structure
        if hasattr(self, 'results_list_layout'):
            # Add widget directly to the end (no stretch element anymore)
            self.results_list_layout.addWidget(result_item)
        
        # Connect click event
        result_item.mousePressEvent = lambda event, idx=index: self._select_result(idx)
    
    def _select_result(self, index: int):
        """
        Select a result from the list
        
        Args:
            index: Index of the result to select
        """
        # Update selected index
        self.selected_youtube_index = index
        
        # Enable download button
        self.download_button.setEnabled(True)
        
        # Highlight selected item and unhighlight others
        if hasattr(self, 'results_list_layout'):
            # Iterate through all widgets (no stretch element anymore)
            for i in range(self.results_list_layout.count()):
                item = self.results_list_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        if i == index:
                            widget.setStyleSheet("""
                                QWidget[resultIndex] {
                                    background-color: #e6e6e6;
                                    border-radius: 0px;
                                    border: 2px solid #999999;
                                    margin: 0px;
                                }
                            """)
                        else:
                            widget.setStyleSheet("""
                                QWidget[resultIndex] {
                                    background-color: #ffffff;
                                    border-radius: 0px;
                                    border: 1px solid #e0e0e0;
                                    margin: 0px;
                                }
                                QWidget[resultIndex]:hover {
                                    background-color: #f8f8f8;
                                    border: 1px solid #cccccc;
                                }
                            """)
        

    
    def _change_download_location(self):
        """Change download location through parent window"""
        # Call the parent window's method directly
        if hasattr(self.window(), '_set_download_location'):
            self.window()._set_download_location()
        else:
            # Fallback to file dialog if parent method not available
            from PyQt6.QtWidgets import QFileDialog
            new_dir = QFileDialog.getExistingDirectory(
                self, 
                "Select Download Directory",
                self.download_location
            )
            if new_dir:
                self.update_download_location(new_dir)
    
    def update_download_location(self, new_location: str):
        """
        Update download location
        
        Args:
            new_location: New download location path
        """
        self.download_location = new_location
        self.download_location_label.setText(f"Download location: {new_location}")
    
    def _animate_to_download_mode(self):
        """Smoothly animate from results list to progress bar"""
        # Set up progress bar and status
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing download...")
        
        # Create fade out animation for results container
        self.fade_out_animation = QPropertyAnimation(self.results_container, b"windowOpacity")
        self.fade_out_animation.setDuration(300)  # 300ms smooth transition
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # When fade out completes, hide results and show progress
        self.fade_out_animation.finished.connect(self._complete_transition_to_download)
        
        # Start the fade out animation
        self.fade_out_animation.start()
    
    def _complete_transition_to_download(self):
        """Complete the transition to download mode"""
        # Hide results container and download button
        self.results_container.setVisible(False)
        self.download_button.setVisible(False)
        
        # Show progress bar and status with fade in
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        
        # Create fade in animation for progress area
        self.fade_in_animation = QPropertyAnimation(self.progress_bar, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_in_animation.start()
    
    def _animate_back_to_results(self):
        """Smoothly animate back from progress bar to results list"""
        # Create fade out animation for progress bar
        self.progress_fade_out = QPropertyAnimation(self.progress_bar, b"windowOpacity")
        self.progress_fade_out.setDuration(300)
        self.progress_fade_out.setStartValue(1.0)
        self.progress_fade_out.setEndValue(0.0)
        self.progress_fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # When fade out completes, show results again
        self.progress_fade_out.finished.connect(self._complete_transition_to_results)
        
        # Start the fade out animation
        self.progress_fade_out.start()
    
    def _complete_transition_to_results(self):
        """Complete the transition back to results view"""
        # Hide progress bar and status
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Show results container and download button
        self.results_container.setVisible(True)
        self.download_button.setVisible(True)
        
        # Create fade in animation for results
        self.results_fade_in = QPropertyAnimation(self.results_container, b"windowOpacity")
        self.results_fade_in.setDuration(300)
        self.results_fade_in.setStartValue(0.0)
        self.results_fade_in.setEndValue(1.0)
        self.results_fade_in.setEasingCurve(QEasingCurve.Type.InCubic)
        self.results_fade_in.start()
    
    def _download_selected(self):
        """Handle download button click"""
        if self.selected_youtube_index < 0 or self.selected_youtube_index >= len(self.youtube_results):
            QMessageBox.warning(self, "No Selection", "Please select a YouTube video to download.")
            return
        
        # Get selected YouTube video
        video = self.youtube_results[self.selected_youtube_index]
        video_url = video['url']
        
        # Get selected audio quality
        quality = self.quality_dropdown.currentData()
        
        # Get metadata for downloads - Spotify metadata for high-confidence matches, 
        # extracted metadata for YouTube-only results
        metadata = None
        if (hasattr(self, 'processed_results') and 
            self.selected_youtube_index < len(self.processed_results)):
            
            processed_result = self.processed_results[self.selected_youtube_index]
            reason = processed_result['reason']
            spotify_track = processed_result['spotify_track']
            youtube_result = processed_result['youtube_result']
            
            # Priority 1: Apply Spotify metadata for high-confidence matches
            if (spotify_track and 
                reason in ['high_confidence_spotify', 'medium_confidence_spotify']):
                
                print(f"[METADATA DEBUG] Applying Spotify metadata for {reason} match")
                track_id = spotify_track['id']
                metadata = self.spotify.get_track_metadata(track_id)
                
            # Priority 2: Extract basic metadata from YouTube title for other results
            else:
                print(f"[METADATA DEBUG] Extracting basic metadata from YouTube title for {reason} result")
                metadata = self._extract_youtube_metadata(youtube_result)
                if metadata:
                    print(f"[METADATA DEBUG] Extracted: '{metadata.get('title', 'Unknown')}' by '{metadata.get('artist', 'Unknown')}'")
                else:
                    print(f"[METADATA DEBUG] Could not extract metadata from title")
        
        # Start smooth animation to hide results and show progress
        self._animate_to_download_mode()
        
        # Disable UI elements during download
        self.download_button.setEnabled(False)
        self.search_input.setEnabled(False)
        self.results_list.setEnabled(False)
        self.quality_dropdown.setEnabled(False)
        
        # Create and start download worker
        self.download_worker = DownloadWorker(video_url, self.download_location, metadata, quality)
        self.download_worker.progress_updated.connect(self._update_progress)
        self.download_worker.download_complete.connect(self._download_finished)
        self.download_worker.start()
    
    def _update_progress(self, percent: float, status: str):
        """
        Update download progress
        
        Args:
            percent: Progress percentage (0-100)
            status: Status message
        """
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(status)
    
    def _download_finished(self, success: bool, result: str):
        """
        Handle download completion
        
        Args:
            success: Whether download was successful
            result: File path if successful, error message if not
        """
        # Re-enable UI elements
    
    def _extract_youtube_metadata(self, youtube_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract basic metadata from YouTube video title and info"""
        try:
            title = youtube_result.get('title', '')
            channel = youtube_result.get('channel', '')
            
            print(f"[EXTRACT DEBUG] Parsing title: {title}")
            
            # Import the extraction function from process_text
            from process_text import extract_song_info
            
            # Try to extract artist and song from title
            artist, song_name = extract_song_info(title)
            
            if artist and song_name:
                # Successfully extracted ARTIST - TITLE format
                metadata = {
                    'title': song_name.strip(),
                    'artist': artist.strip(),
                    'album': '',  # No album info from YouTube
                    'source': 'youtube_extracted'
                }
                
                print(f"[EXTRACT DEBUG] Successfully extracted: '{metadata['title']}' by '{metadata['artist']}'")
                return metadata
            else:
                # Fallback: use title as-is and channel as artist if it looks like an artist name
                cleaned_title = self._clean_title_for_metadata(title)
                
                # Check if channel looks like an artist name (not generic)
                generic_channels = ['music', 'official', 'records', 'entertainment', 'media', 'network']
                is_artist_channel = (len(channel.split()) <= 3 and 
                                   not any(generic in channel.lower() for generic in generic_channels))
                
                metadata = {
                    'title': cleaned_title,
                    'artist': channel if is_artist_channel else 'Unknown Artist',
                    'album': '',
                    'source': 'youtube_fallback'
                }
                
                print(f"[EXTRACT DEBUG] Using fallback: '{metadata['title']}' by '{metadata['artist']}'")
                return metadata
                
        except Exception as e:
            print(f"[EXTRACT DEBUG] Error extracting metadata: {e}")
            return None
    
    def _clean_title_for_metadata(self, title: str) -> str:
        """Clean YouTube title for use as song title metadata"""
        import re
        
        # Remove common YouTube decorations
        patterns_to_remove = [
            r'\(official\s*(video|audio|music\s*video)\)',
            r'\[official\s*(video|audio|music\s*video)\]',
            r'\(official\)',
            r'\[official\]',
            r'\(music\s*video\)',
            r'\[music\s*video\]',
            r'\(audio\)',
            r'\[audio\]',
            r'\(lyric\s*video\)',
            r'\[lyric\s*video\]',
            r'\(lyrics\)',
            r'\[lyrics\]',
            r'\(hd\)',
            r'\[hd\]',
            r'\(4k\)',
            r'\[4k\]'
        ]
        
        cleaned = title
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.rstrip(' -')
        
        return cleaned
        
        if success:
            self.status_label.setText(f"Download complete: {os.path.basename(result)}")
            self.progress_bar.setValue(100)
            
            # Show success message
            QMessageBox.information(
                self,
                "Download Complete",
                f"Successfully downloaded:\n{os.path.basename(result)}\n\nSaved to:\n{os.path.dirname(result)}"
            )
            
            # Animate back to results view after success
            self._animate_back_to_results()
        else:
            self.status_label.setText(f"Download failed: {result}")
            self.progress_bar.setValue(0)
            
            # Show error message
            QMessageBox.critical(
                self,
                "Download Failed",
                f"Failed to download: {result}"
            )
        
        # Clean up worker
        if self.download_worker:
            self.download_worker.deleteLater()
            self.download_worker = None
