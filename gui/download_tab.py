"""
Download tab for the main application window
"""

import os
import logging
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QProgressBar, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush

from downloader import Downloader, AudioQuality
from search_youtube import YouTubeSearch
from search_spotify import SpotifySearch, search_track_on_spotify
from process_text import clean_filename, extract_song_info, clean_search_query
from utils.config import Config

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
        
        # Current search results
        self.youtube_results = []
        self.spotify_results = []
        
        # Current selected track info
        self.selected_youtube_index = -1
        self.selected_spotify_index = -1
        
        # Download worker
        self.download_worker = None
        
        # Set background image
        self.bg_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bg_main.jpg")
        if os.path.exists(self.bg_image_path):
            self.setAutoFillBackground(True)
            palette = self.palette()
            pixmap = QPixmap(self.bg_image_path)
            brush = QBrush(pixmap)
            palette.setBrush(QPalette.ColorRole.Window, brush)
            self.setPalette(palette)
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Create large spacer to push search bar to lower third of window
        main_layout.addStretch(3)
        
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
        search_layout.addWidget(self.search_input)
        
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
        
        # Add the search container to the main layout with auto-centering
        search_container_layout = QHBoxLayout()
        search_container_layout.addStretch(1)
        search_container_layout.addWidget(search_container)
        search_container_layout.addStretch(1)
        
        main_layout.addLayout(search_container_layout)
        
        # Results section - initially hidden, only shown after search
        self.results_container = QWidget()
        self.results_container.setVisible(False)  # Initially hidden
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 20, 0, 0)
        results_layout.setSpacing(5)
        
        # Results list (similar to your original design in Capture1.PNG)
        self.results_list = QWidget()
        self.results_list.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        results_list_layout = QVBoxLayout(self.results_list)
        results_list_layout.setContentsMargins(0, 0, 0, 0)
        results_list_layout.setSpacing(8)
        
        # We'll add result items dynamically here after a search
        # Each result will be a row with album art on left and song info on right
        
        results_layout.addWidget(self.results_list)
        results_layout.addStretch()  # Push results to the top
        
        # Add results container to main layout
        results_container_layout = QHBoxLayout()
        results_container_layout.addStretch(1)
        results_container_layout.addWidget(self.results_container, 7)  # Take 70% of width 
        results_container_layout.addStretch(1)
        
        main_layout.addLayout(results_container_layout)
        
        # Download options
        options_layout = QHBoxLayout()
        
        quality_label = QLabel("Quality:")
        options_layout.addWidget(quality_label)
        
        self.quality_dropdown = QComboBox()
        self.quality_dropdown.addItem("Best (320k)", AudioQuality.BEST)
        self.quality_dropdown.addItem("High (256k)", AudioQuality.HIGH)
        self.quality_dropdown.addItem("Medium (192k)", AudioQuality.MEDIUM)
        self.quality_dropdown.addItem("Low (128k)", AudioQuality.LOW)
        options_layout.addWidget(self.quality_dropdown)
        
        options_layout.addStretch()
        
        self.download_location_label = QLabel(f"Download location: {self.download_location}")
        options_layout.addWidget(self.download_location_label)
        
        change_location_button = QPushButton("Change")
        change_location_button.clicked.connect(self._change_download_location)
        options_layout.addWidget(change_location_button)
        
        main_layout.addLayout(options_layout)
        
        # Download button
        self.download_button = QPushButton("Download")
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
        main_layout.addStretch()
    
    def _search(self):
        """Handle search button click"""
        query = self.search_input.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Search", "Please enter a search term.")
            return
        
        # Clear previous results and result list widget
        self.youtube_results = []
        self.spotify_results = []
        self.selected_youtube_index = -1
        self.selected_spotify_index = -1
        self.download_button.setEnabled(False)
        
        # Clear the results list
        self._clear_results_list()
        
        # Show loading indicator (could add a spinner here)
        self.status_label.setText("Searching...")
        self.status_label.setVisible(True)
        
        # Search YouTube
        self.youtube_results = self.youtube.search(query)
        
        # Hide loading indicator
        self.status_label.setVisible(False)
        
        # If no results found
        if not self.youtube_results:
            QMessageBox.information(self, "No Results", "No results found for your search term.")
            return
            
        # Show results container if we have results
        self.results_container.setVisible(True)
        
        # Populate results list with YouTube results
        for i, result in enumerate(self.youtube_results):
            # Create result item similar to original app design
            self._add_result_item(i, result)
            
            # Search Spotify for first result only
            if i == 0:
                self._search_spotify_metadata(result['title'])
                
        # Set first result as selected
        if self.youtube_results:
            self._select_result(0)
    
    def _clear_results_list(self):
        """Clear all results from the list"""
        # Get the layout
        layout = self.results_list.layout()
        
        # Remove all widgets from the layout
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _add_result_item(self, index: int, result: Dict[str, Any]):
        """
        Add a result item to the results list
        
        Args:
            index: Result index
            result: Result data from YouTube search
        """
        # Create result item widget
        result_item = QWidget()
        result_item.setObjectName(f"result_item_{index}")
        result_item.setProperty("resultIndex", index)
        result_item.setCursor(Qt.CursorShape.PointingHandCursor)
        result_item.setStyleSheet("""
            QWidget[resultIndex] {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 4px;
                padding: 8px;
            }
            QWidget[resultIndex]:hover {
                background-color: rgba(255, 255, 255, 1.0);
            }
        """)
        
        # Create layout for result item
        item_layout = QHBoxLayout(result_item)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # Album art (placeholder for now)
        album_art = QLabel()
        album_art.setFixedSize(60, 60)
        album_art.setStyleSheet("""
            background-color: #e0e0e0;
            border-radius: 4px;
        """)
        item_layout.addWidget(album_art)
        
        # Result details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(10, 0, 0, 0)
        details_layout.setSpacing(5)
        
        # Title
        title_label = QLabel(f"{index + 1}: {result['title']}")
        title_label.setStyleSheet("""
            font-weight: bold;
            color: #333333;
        """)
        details_layout.addWidget(title_label)
        
        # Additional info (channel/duration)
        info_label = QLabel(f"Channel: {result['channel']}")
        info_label.setStyleSheet("""
            color: #666666;
            font-size: 12px;
        """)
        details_layout.addWidget(info_label)
        
        item_layout.addWidget(details_widget)
        
        # Add to results list
        self.results_list.layout().addWidget(result_item)
        
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
        for i in range(self.results_list.layout().count()):
            widget = self.results_list.layout().itemAt(i).widget()
            if widget:
                if i == index:
                    widget.setStyleSheet("""
                        QWidget {
                            background-color: rgba(255, 255, 255, 1.0);
                            border-radius: 4px;
                            border-left: 4px solid #e63b19;
                            padding: 8px;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QWidget {
                            background-color: rgba(255, 255, 255, 0.9);
                            border-radius: 4px;
                            padding: 8px;
                        }
                        QWidget:hover {
                            background-color: rgba(255, 255, 255, 1.0);
                        }
                    """)
        
        # Search Spotify for metadata if needed
        if 0 <= index < len(self.youtube_results):
            self._search_spotify_metadata(self.youtube_results[index]['title'])
    
    def _search_spotify_metadata(self, video_title: str):
        """
        Search Spotify for metadata based on video title
        
        Args:
            video_title: YouTube video title
        """
        # Clean title for better Spotify search
        clean_title = clean_search_query(video_title)
        
        # Extract artist and song name
        artist, song_name = extract_song_info(clean_title)
        
        # Create search query
        if artist and song_name:
            spotify_query = f"{artist} {song_name}"
        else:
            spotify_query = clean_title
        
        # Search Spotify
        self.spotify_results = self.spotify.search_track(spotify_query)
        
        # Select first Spotify result if available
        if self.spotify_results:
            self.selected_spotify_index = 0
    
    def _change_download_location(self):
        """Change download location through parent window"""
        # This will trigger the parent window's _set_download_location method
        # which will update our download_location through update_download_location
        self.window().findChild(QAction, "Set Download Location").trigger()
    
    def update_download_location(self, new_location: str):
        """
        Update download location
        
        Args:
            new_location: New download location path
        """
        self.download_location = new_location
        self.download_location_label.setText(f"Download location: {new_location}")
    
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
        
        # Get metadata from Spotify if selected
        metadata = None
        if self.selected_spotify_index >= 0 and self.selected_spotify_index < len(self.spotify_results):
            spotify_track = self.spotify_results[self.selected_spotify_index]
            track_id = spotify_track['id']
            metadata = self.spotify.get_track_metadata(track_id)
        
        # Show progress bar and status
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Preparing download...")
        self.status_label.setVisible(True)
        
        # Disable UI elements during download
        self.download_button.setEnabled(False)
        self.search_input.setEnabled(False)
        self.youtube_results_table.setEnabled(False)
        self.spotify_results_table.setEnabled(False)
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
        self.download_button.setEnabled(True)
        self.search_input.setEnabled(True)
        self.youtube_results_table.setEnabled(True)
        self.spotify_results_table.setEnabled(True)
        self.quality_dropdown.setEnabled(True)
        
        if success:
            self.status_label.setText(f"Download complete: {os.path.basename(result)}")
            self.progress_bar.setValue(100)
            
            # Show success message
            QMessageBox.information(
                self,
                "Download Complete",
                f"Successfully downloaded:\n{os.path.basename(result)}\n\nSaved to:\n{os.path.dirname(result)}"
            )
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
