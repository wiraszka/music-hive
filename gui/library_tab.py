"""
Library tab for the main application window
"""

import os
import logging
import threading
from typing import List, Dict, Any, Optional, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, 
    QFileDialog, QMessageBox, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor

from search_spotify import SpotifySearch
from utils.config import Config
from library.scanner import LibraryScanner
from library.metadata import MetadataManager

logger = logging.getLogger(__name__)

class ScanWorker(QThread):
    """Worker thread for scanning music library"""
    # Define signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_file
    scan_complete = pyqtSignal(list)  # track_list
    
    def __init__(self, music_dir: str):
        """
        Initialize scan worker
        
        Args:
            music_dir: Directory to scan for music files
        """
        super().__init__()
        self.music_dir = music_dir
        
    def run(self):
        """Execute the scan task"""
        try:
            scanner = LibraryScanner()
            tracks = scanner.scan_directory(self.music_dir, self.progress_updated.emit)
            self.scan_complete.emit(tracks)
        except Exception as e:
            logger.error(f"Scan worker error: {str(e)}")
            self.scan_complete.emit([])


class MetadataWorker(QThread):
    """Worker thread for updating track metadata"""
    # Define signals
    progress_updated = pyqtSignal(int, int, str)  # current, total, current_track
    metadata_complete = pyqtSignal(dict, str)  # metadata, file_path
    
    def __init__(self, file_path: str, search_query: str):
        """
        Initialize metadata worker
        
        Args:
            file_path: Path to the music file
            search_query: Query to search on Spotify
        """
        super().__init__()
        self.file_path = file_path
        self.search_query = search_query
        
    def run(self):
        """Execute the metadata fetch task"""
        try:
            spotify = SpotifySearch()
            
            if not spotify.is_available:
                self.metadata_complete.emit({}, self.file_path)
                return
                
            # Search for track
            self.progress_updated.emit(0, 1, f"Searching for: {self.search_query}")
            results = spotify.search_track(self.search_query, limit=1)
            
            if not results:
                self.metadata_complete.emit({}, self.file_path)
                return
                
            # Get metadata for top result
            self.progress_updated.emit(1, 2, f"Fetching metadata...")
            track_id = results[0]['id']
            metadata = spotify.get_track_metadata(track_id)
            
            self.metadata_complete.emit(metadata or {}, self.file_path)
            
        except Exception as e:
            logger.error(f"Metadata worker error: {str(e)}")
            self.metadata_complete.emit({}, self.file_path)


class LibraryTab(QWidget):
    """Library tab widget"""
    
    def __init__(self, config: Config):
        """
        Initialize library tab
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.config = config
        self.music_dir = config.music_dir or config.download_location
        
        # Track list
        self.tracks = []
        
        # Worker threads
        self.scan_worker = None
        self.metadata_worker = None
        
        # Initialize UI
        self._init_ui()
        
        # Scan library on startup if configured
        if self.config.auto_scan_library:
            self.scan_library()
    
    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header section
        header_layout = QHBoxLayout()
        
        library_title = QLabel("Music Library")
        library_title.setObjectName("sectionTitle")
        header_layout.addWidget(library_title)
        
        header_layout.addStretch()
        
        self.library_path_label = QLabel(f"Library path: {self.music_dir}")
        header_layout.addWidget(self.library_path_label)
        
        set_library_btn = QPushButton("Set Library Path")
        set_library_btn.clicked.connect(self._set_library_path)
        header_layout.addWidget(set_library_btn)
        
        scan_btn = QPushButton("Scan Library")
        scan_btn.clicked.connect(self.scan_library)
        header_layout.addWidget(scan_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.show_incomplete_only = QCheckBox("Show tracks with missing metadata only")
        self.show_incomplete_only.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.show_incomplete_only)
        
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # Library table
        self.library_table = QTableWidget(0, 6)  # rows, columns
        self.library_table.setHorizontalHeaderLabels(["Title", "Artist", "Album", "Year", "Status", "Actions"])
        self.library_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.library_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.library_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.library_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.library_table.verticalHeader().setVisible(False)
        self.library_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.library_table)
    
    def _set_library_path(self):
        """Set music library path"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Music Library Directory",
            self.music_dir
        )
        
        if dir_path:
            self.music_dir = dir_path
            self.config.music_dir = dir_path
            self.config.save()
            self.library_path_label.setText(f"Library path: {dir_path}")
            
            # Ask if user wants to scan the new directory
            reply = QMessageBox.question(
                self,
                "Scan Library",
                "Would you like to scan the new library location now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.scan_library()
    
    def scan_library(self):
        """Scan music library for tracks"""
        if not self.music_dir or not os.path.exists(self.music_dir):
            QMessageBox.warning(
                self,
                "Invalid Library Path",
                "Please set a valid music library path first."
            )
            return
        
        # Clear previous results
        self.tracks = []
        self.library_table.setRowCount(0)
        
        # Show progress bar and status
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning library...")
        self.status_label.setVisible(True)
        
        # Create and start scan worker
        self.scan_worker = ScanWorker(self.music_dir)
        self.scan_worker.progress_updated.connect(self._update_scan_progress)
        self.scan_worker.scan_complete.connect(self._scan_complete)
        self.scan_worker.start()
    
    def _update_scan_progress(self, current: int, total: int, current_file: str):
        """
        Update scan progress
        
        Args:
            current: Current file count
            total: Total file count
            current_file: Current file being processed
        """
        if total > 0:
            percent = (current / total) * 100
            self.progress_bar.setValue(int(percent))
        
        self.status_label.setText(f"Scanning: {os.path.basename(current_file)}")
    
    def _scan_complete(self, tracks: List[Dict[str, Any]]):
        """
        Handle scan completion
        
        Args:
            tracks: List of track information
        """
        self.tracks = tracks
        self.status_label.setText(f"Found {len(tracks)} tracks.")
        
        # Apply filters and populate the table
        self._populate_library_table()
        
        # Clean up worker
        if self.scan_worker:
            self.scan_worker.deleteLater()
            self.scan_worker = None
        
        self.progress_bar.setVisible(False)
    
    def _populate_library_table(self):
        """Populate the library table with tracks"""
        # Clear the table
        self.library_table.setRowCount(0)
        
        # Filter tracks if needed
        filtered_tracks = self._get_filtered_tracks()
        
        # Set row count
        self.library_table.setRowCount(len(filtered_tracks))
        
        # Populate table
        for row, track in enumerate(filtered_tracks):
            # Basic info
            title_item = QTableWidgetItem(track.get('title', 'Unknown'))
            artist_item = QTableWidgetItem(track.get('artist', 'Unknown'))
            album_item = QTableWidgetItem(track.get('album', 'Unknown'))
            year_item = QTableWidgetItem(track.get('year', ''))
            
            # Status
            status = "Complete" if self._is_metadata_complete(track) else "Incomplete"
            status_item = QTableWidgetItem(status)
            
            # Set color based on status
            if status == "Incomplete":
                status_item.setForeground(QColor(255, 0, 0))  # Red for incomplete
            else:
                status_item.setForeground(QColor(0, 128, 0))  # Green for complete
            
            # Add items to table
            self.library_table.setItem(row, 0, title_item)
            self.library_table.setItem(row, 1, artist_item)
            self.library_table.setItem(row, 2, album_item)
            self.library_table.setItem(row, 3, year_item)
            self.library_table.setItem(row, 4, status_item)
            
            # Create update button if metadata is incomplete
            if status == "Incomplete":
                update_btn = QPushButton("Get Info")
                update_btn.clicked.connect(lambda checked, r=row: self._update_track_metadata(r))
                self.library_table.setCellWidget(row, 5, update_btn)
    
    def _get_filtered_tracks(self) -> List[Dict[str, Any]]:
        """
        Get tracks based on current filter settings
        
        Returns:
            Filtered list of tracks
        """
        if self.show_incomplete_only.isChecked():
            return [track for track in self.tracks if not self._is_metadata_complete(track)]
        else:
            return self.tracks
    
    def _apply_filters(self):
        """Apply current filters and update table"""
        self._populate_library_table()
    
    def _is_metadata_complete(self, track: Dict[str, Any]) -> bool:
        """
        Check if track metadata is complete
        
        Args:
            track: Track information dictionary
            
        Returns:
            True if metadata is complete, False otherwise
        """
        # Check for required fields
        required_fields = ['title', 'artist', 'album']
        for field in required_fields:
            if not track.get(field):
                return False
                
        # Check for album art
        if not track.get('has_cover'):
            return False
            
        return True
    
    def _update_track_metadata(self, row: int):
        """
        Update track metadata using Spotify
        
        Args:
            row: Table row index
        """
        # Get track information
        if row < 0 or row >= len(self._get_filtered_tracks()):
            return
            
        track = self._get_filtered_tracks()[row]
        file_path = track.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The file could not be found:\n{file_path}"
            )
            return
        
        # Build search query
        title = track.get('title', '')
        artist = track.get('artist', '')
        
        if title and artist:
            search_query = f"{artist} {title}"
        elif title:
            search_query = title
        else:
            # Use filename without extension as fallback
            filename = os.path.basename(file_path)
            search_query = os.path.splitext(filename)[0]
        
        # Show progress
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Searching for metadata: {search_query}")
        self.status_label.setVisible(True)
        
        # Create and start metadata worker
        self.metadata_worker = MetadataWorker(file_path, search_query)
        self.metadata_worker.progress_updated.connect(self._update_metadata_progress)
        self.metadata_worker.metadata_complete.connect(self._metadata_complete)
        self.metadata_worker.start()
    
    def _update_metadata_progress(self, current: int, total: int, message: str):
        """
        Update metadata progress
        
        Args:
            current: Current step
            total: Total steps
            message: Status message
        """
        if total > 0:
            percent = (current / total) * 100
            self.progress_bar.setValue(int(percent))
        
        self.status_label.setText(message)
    
    def _metadata_complete(self, metadata: Dict[str, Any], file_path: str):
        """
        Handle metadata fetch completion
        
        Args:
            metadata: Track metadata
            file_path: File path
        """
        try:
            # Clean up worker
            if self.metadata_worker:
                self.metadata_worker.deleteLater()
                self.metadata_worker = None
            
            if not metadata:
                self.progress_bar.setVisible(False)
                self.status_label.setText("No metadata found.")
                
                QMessageBox.warning(
                    self,
                    "Metadata Not Found",
                    "No metadata could be found for this track."
                )
                return
            
            # Show metadata and ask for confirmation
            message = f"Title: {metadata.get('title', 'Unknown')}\n"
            message += f"Artist: {metadata.get('artist', 'Unknown')}\n"
            message += f"Album: {metadata.get('album', 'Unknown')}\n"
            message += f"Year: {metadata.get('year', 'Unknown')}\n\n"
            message += "Apply this metadata to the track?"
            
            reply = QMessageBox.question(
                self,
                "Apply Metadata",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Update the track
                self.status_label.setText("Updating metadata...")
                
                # Apply metadata to file
                metadata_manager = MetadataManager()
                success = metadata_manager.update_metadata(file_path, metadata)
                
                if success:
                    self.status_label.setText("Metadata updated successfully.")
                    
                    # Update track in our list
                    for track in self.tracks:
                        if track.get('file_path') == file_path:
                            track.update({
                                'title': metadata.get('title', track.get('title', '')),
                                'artist': metadata.get('artist', track.get('artist', '')),
                                'album': metadata.get('album', track.get('album', '')),
                                'year': metadata.get('year', track.get('year', '')),
                                'has_cover': True  # Assuming cover art was added
                            })
                            break
                    
                    # Update the table
                    self._populate_library_table()
                    
                    QMessageBox.information(
                        self,
                        "Metadata Updated",
                        "Track metadata has been updated successfully."
                    )
                else:
                    self.status_label.setText("Failed to update metadata.")
                    
                    QMessageBox.critical(
                        self,
                        "Update Failed",
                        "Failed to update track metadata."
                    )
            else:
                self.status_label.setText("Metadata update cancelled.")
            
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.setVisible(False)
