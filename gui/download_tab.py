"""
Download tab for the main application window
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QProgressBar, QComboBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QFileDialog,
    QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QByteArray, QRect, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QBrush, QPainter

from downloader import Downloader, AudioQuality
from search_youtube import YouTubeSearch
from search_spotify import SpotifySearch
from utils.song_filter import SongFilter
from utils.config import Config
from process_text import clean_search_query, extract_song_info

class DownloadWorker(QThread):
    """Worker thread for downloading music"""
    
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
        
        # Initialize services
        self.youtube = YouTubeSearch()
        self.spotify = SpotifySearch()
        self.song_filter = SongFilter()
        
        # State variables
        self.youtube_results = []
        self.processed_results = []
        self.selected_youtube_index = -1
        self.download_worker = None
        self.animation_group = None
        self.ui_state = "initial"  # initial, results, downloading
        
        # Load background image
        self.background_image = None
        self._load_background_image()
        
        # Initialize UI
        self._init_ui()
    
    def _load_background_image(self):
        """Load and prepare background image"""
        bg_path = os.path.join("assets", "downloads_bg_gradient.jpg")
        if os.path.exists(bg_path):
            self.background_image = QPixmap(bg_path)
            print(f"Background image loaded from: {bg_path}")
        else:
            print(f"Background image not found at: {bg_path}")
    
    def paintEvent(self, event):
        """Custom paint event to draw scaled background image"""
        if self.background_image:
            painter = QPainter(self)
            
            # Scale image to fit widget while maintaining aspect ratio
            widget_size = self.size()
            scaled_pixmap = self.background_image.scaled(
                widget_size, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center the image
            x = (widget_size.width() - scaled_pixmap.width()) // 2
            y = (widget_size.height() - scaled_pixmap.height()) // 2
            
            painter.drawPixmap(x, y, scaled_pixmap)
        
        # Call parent paint event
        super().paintEvent(event)
    
    def _init_ui(self):
        """Initialize the dynamic user interface"""
        # Main layout fills entire widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create all UI components
        self._create_ui_components()
        
        # Set initial state with search positioned 20% from bottom
        self._set_initial_state()
    
    def _create_ui_components(self):
        """Create all UI components for different states"""
        # Results area (initially hidden, will animate in from search area)
        self.results_container = QWidget()
        self.results_container.setVisible(False)
        
        # Create responsive layout with minimum width constraints
        self.results_outer_layout = QHBoxLayout(self.results_container)
        self.results_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.results_outer_layout.setSpacing(0)
        
        # Dynamic spacers that shrink when content hits minimum width
        self.results_left_spacer = self.results_outer_layout.addStretch(3)
        
        # Center content area with minimum width constraint
        self.results_center_widget = QWidget()
        self.results_center_widget.setMinimumWidth(600)  # Match controls minimum width
        self.results_layout = QVBoxLayout(self.results_center_widget)
        self.results_layout.setContentsMargins(0, 40, 0, 20)
        self.results_outer_layout.addWidget(self.results_center_widget, 4)
        
        self.results_right_spacer = self.results_outer_layout.addStretch(3)
        
        # Adaptive results list - height adjusts to content, max 10 items
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setMinimumHeight(80)  # Minimum for 1 result
        self.results_scroll.setMaximumHeight(400)  # Maximum for 5 results (scroll after 5)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #cccccc;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #999999;
            }
        """)
        
        self.results_list = QWidget()
        self.results_list.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.results_list_layout = QVBoxLayout(self.results_list)
        self.results_list_layout.setContentsMargins(0, 0, 0, 0)
        self.results_list_layout.setSpacing(2)
        
        self.results_scroll.setWidget(self.results_list)
        self.results_layout.addWidget(self.results_scroll)
        
        # Search/Controls container (dynamic - changes based on state)
        self.controls_container = QWidget()
        self.controls_container.setFixedHeight(120)
        
        # Create layout matching results structure exactly
        self.controls_outer_layout = QHBoxLayout(self.controls_container)
        self.controls_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_outer_layout.setSpacing(0)
        
        # Match results layout: 3:4:3 ratio with same minimum width
        self.controls_left_spacer = self.controls_outer_layout.addStretch(3)
        
        # Center content area with adequate width for 60% search and controls
        self.controls_center_widget = QWidget()
        self.controls_center_widget.setMinimumWidth(600)  # Increased for 60% width elements
        self.controls_layout = QHBoxLayout(self.controls_center_widget)
        self.controls_layout.setContentsMargins(0, 20, 0, 20)
        self.controls_layout.setSpacing(12)  # Space between control elements
        self.controls_outer_layout.addWidget(self.controls_center_widget, 4)  # Same flex ratio as results
        
        self.controls_right_spacer = self.controls_outer_layout.addStretch(3)
        
        # Initial search widget with 55% width layout
        self._create_search_widget_for_controls()
        
        # Download controls (created but hidden initially)
        self._create_download_controls()
        
        # Status/Progress area
        self._create_status_area()
        
        # Add to main layout
        self.main_layout.addWidget(self.results_container)
        self.main_layout.addWidget(self.controls_container)
        self.main_layout.addWidget(self.status_container)
    
    def _create_search_widget(self):
        """Create search widget with 55% width layout"""
        self.search_widget = QWidget()
        
        # Create responsive layout for search (22.5% margins for 55% content)
        search_outer_layout = QHBoxLayout(self.search_widget)
        search_outer_layout.setContentsMargins(0, 0, 0, 0)
        search_outer_layout.setSpacing(0)
        
        # Add spacers for 60% content width
        search_outer_layout.addStretch(200)  # 20% left margin
        
        # Search content area
        search_center_widget = QWidget()
        search_center_widget.setMinimumWidth(600)
        search_layout = QHBoxLayout(search_center_widget)
        search_layout.setContentsMargins(0, 20, 0, 20)
        search_layout.setSpacing(0)  # No spacing for touching edges
        
        self._create_search_elements(search_layout)
        
        search_outer_layout.addWidget(search_center_widget, 600)  # 60% center content
        search_outer_layout.addStretch(200)  # 20% right margin
    
    def _create_search_widget_for_controls(self):
        """Create search widget with 60% width layout for controls area"""
        # Create search container widget with 60% width layout
        search_container = QWidget()
        
        # Create responsive layout for search (20% margins for 60% content)
        search_outer_layout = QHBoxLayout(search_container)
        search_outer_layout.setContentsMargins(0, 0, 0, 0)
        search_outer_layout.setSpacing(0)
        
        # Add spacers for 60% content width
        search_outer_layout.addStretch(200)  # 20% left margin
        
        # Search content area
        search_center_widget = QWidget()
        search_center_widget.setMinimumWidth(600)
        search_layout = QHBoxLayout(search_center_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)  # No spacing for touching edges
        
        # Create fresh search elements
        self._create_search_elements(search_layout)
        
        search_outer_layout.addWidget(search_center_widget, 600)  # 60% center content
        search_outer_layout.addStretch(200)  # 20% right margin
        
        # Add the search container to controls layout
        self.controls_layout.addWidget(search_container)
    
    def _create_search_elements(self, layout):
        """Create search input and button with touching edges"""
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for songs, artists, or albums...")
        self.search_input.setFixedHeight(40)  # Match button height
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border-right: none;
                padding: 8px 12px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
        """)
        self.search_input.returnPressed.connect(self._on_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumWidth(100)  # Ensure adequate width
        self.search_button.setFixedHeight(40)  # Match input field height
        self.search_button.setSizePolicy(self.search_button.sizePolicy().Policy.Preferred, 
                                       self.search_button.sizePolicy().Policy.Fixed)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #333333;
                border: 1px solid #cccccc;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                border-left: none;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 100px;
                height: 40px;
            }
            QPushButton:hover {
                background-color: #d9d9d9;
            }
            QPushButton:pressed {
                background-color: #b3b3b3;
            }
        """)
        self.search_button.clicked.connect(self._on_search)
        
        # Add to layout - input takes most space, button has fixed width
        layout.addWidget(self.search_input, 1)  # Input takes remaining space
        layout.addWidget(self.search_button, 0)  # Button keeps its minimum width
    
    def _create_download_controls(self):
        """Create responsive download controls that adapt to window size"""
        # Back button - responsive design
        self.back_button = QPushButton("←")
        self.back_button.setMinimumSize(40, 40)
        self.back_button.clicked.connect(self._on_back_to_search)
        
        # Quality dropdown - responsive design with symbol and text
        from PyQt6.QtWidgets import QComboBox
        self.quality_dropdown = QComboBox()
        self.quality_dropdown.setMinimumSize(40, 40)
        for quality in AudioQuality:
            self.quality_dropdown.addItem(f"♪ {quality.value}", quality)
        self.quality_dropdown.setCurrentIndex(3)  # Default to BEST
        
        # Location button - responsive design with symbol and text
        self.location_button = QPushButton("📁")
        self.location_button.setMinimumSize(40, 40)
        self.location_button.clicked.connect(self._select_download_location)
        
        # Download button
        self.download_button = QPushButton("Download Selected")
        self.download_button.setFixedHeight(40)
        self.download_button.clicked.connect(self._on_download_selected)
        self.download_button.setEnabled(False)
        
        # Set initial styling
        self._update_responsive_controls()
        
        # Initially hide download controls
        self.back_button.setVisible(False)
        self.quality_dropdown.setVisible(False)
        self.location_button.setVisible(False)
        self.download_button.setVisible(False)
    
    def _create_status_area(self):
        """Create status and progress area"""
        self.status_container = QWidget()
        self.status_container.setVisible(False)
        
        # Create responsive layout with minimum width constraints
        self.status_outer_layout = QHBoxLayout(self.status_container)
        self.status_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.status_outer_layout.setSpacing(0)
        
        # Dynamic spacers that shrink when content hits minimum width
        self.status_left_spacer = self.status_outer_layout.addStretch(3)
        
        # Center content area with minimum width constraint
        self.status_center_widget = QWidget()
        self.status_center_widget.setMinimumWidth(400)  # Match results minimum width
        self.status_layout = QVBoxLayout(self.status_center_widget)
        self.status_layout.setContentsMargins(0, 20, 0, 40)
        self.status_outer_layout.addWidget(self.status_center_widget, 4)
        
        self.status_right_spacer = self.status_outer_layout.addStretch(3)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                padding: 8px;
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                text-align: center;
                font-size: 12px;
                color: #333333;
                background-color: #ffffff;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        self.progress_bar.setVisible(False)
        
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.progress_bar)
    
    def _set_initial_state(self):
        """Set initial UI state with search positioned 20% from bottom"""
        # Clear any existing spacers first
        while self.main_layout.count() > 0:
            item = self.main_layout.takeAt(0)
            if item and item.widget():
                # Don't delete widgets, just remove from layout
                pass
            elif item and item.spacerItem():
                # Delete spacer items
                del item
        
        # Re-add widgets in correct order with fresh spacers
        self.main_layout.addStretch(4)  # 80% space at top
        self.main_layout.addWidget(self.results_container)
        self.main_layout.addWidget(self.controls_container)
        self.main_layout.addWidget(self.status_container)
        self.main_layout.addStretch(1)  # 20% space at bottom
    
    def _on_search(self):
        """Handle search button click with UI transition"""
        try:
            query = self.search_input.text().strip()
            
            if not query:
                QMessageBox.warning(self, "Empty Search", "Please enter a search term.")
                return
            
            # Initialize search components safely
            if not hasattr(self, 'youtube_searcher'):
                self.youtube_searcher = YouTubeSearch()
            if not hasattr(self, 'spotify_searcher'):
                self.spotify_searcher = SpotifySearch()
            if not hasattr(self, 'song_filter'):
                self.song_filter = SongFilter()
            
            # Start UI transition animation
            self._animate_to_results_state()
            
            # Clear previous results
            self.youtube_results = []
            self.selected_youtube_index = -1
            if hasattr(self, 'download_button'):
                self.download_button.setEnabled(False)
            
            # Clear any existing result widgets
            self._clear_results_list()
            
            # Show status
            self.status_container.setVisible(True)
            self.status_label.setText("Searching...")
            
            # Perform search
            self._perform_search(query)
            
        except Exception as e:
            logging.error(f"Search error: {e}")
            QMessageBox.critical(self, "Search Error", f"Failed to start search: {str(e)}")
            self.status_container.setVisible(False)
    
    def _animate_to_results_state(self):
        """Animate UI transition from search state to results state"""
        try:
            if hasattr(self, 'animation_group') and self.animation_group and self.animation_group.state() == QPropertyAnimation.State.Running:
                return
            
            self.ui_state = "results"
            self.animation_group = QParallelAnimationGroup()
            
            # Show results container and animate it sliding up
            self.results_container.setVisible(True)
            self.results_container.setMaximumHeight(0)
            
            results_animation = QPropertyAnimation(self.results_container, b"maximumHeight")
            results_animation.setDuration(600)
            results_animation.setStartValue(0)
            results_animation.setEndValue(500)  # Increased for adaptive height
            results_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Animate search elements morphing into download controls
            self._morph_search_to_controls()
            
            self.animation_group.addAnimation(results_animation)
            self.animation_group.finished.connect(self._on_animation_finished)
            self.animation_group.start()
            
        except Exception as e:
            logging.error(f"Animation error: {e}")
            # Fallback to direct state change without animation
            self.ui_state = "results"
            self.results_container.setVisible(True)
            self._morph_search_to_controls()
    
    def _morph_search_to_controls(self):
        """Morph search elements into download controls"""
        try:
            # Ensure download controls are created
            if not hasattr(self, 'back_button'):
                self._create_download_controls()
            
            # Hide search elements
            if hasattr(self, 'search_input'):
                self.search_input.setVisible(False)
            if hasattr(self, 'search_button'):
                self.search_button.setVisible(False)
            
            # Clear controls layout first to prevent layout conflicts
            while self.controls_layout.count() > 0:
                item = self.controls_layout.takeAt(0)
                if item and item.widget():
                    widget = item.widget()
                    self.controls_layout.removeWidget(widget)
                    widget.setVisible(False)
                    widget.deleteLater()
            
            # Create horizontal container for all controls on same line
            controls_row = QWidget()
            controls_layout = QHBoxLayout(controls_row)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.setSpacing(12)
            
            # Add controls with proper layout - download button expands to fill space
            controls_layout.addWidget(self.back_button)
            controls_layout.addWidget(self.quality_dropdown)  
            controls_layout.addWidget(self.location_button)
            controls_layout.addWidget(self.download_button, 1)  # Download button fills remaining space
            
            # Show controls
            self.back_button.setVisible(True)
            self.quality_dropdown.setVisible(True)
            self.location_button.setVisible(True)
            self.download_button.setVisible(True)
            
            # Add to main layout with full width
            self.controls_layout.addWidget(controls_row)
            
            # Update responsive controls based on current window size
            if hasattr(self, '_update_responsive_controls'):
                self._update_responsive_controls()
                
        except Exception as e:
            logging.error(f"Error in morph controls: {e}")
            # Fallback to simple state change
            if hasattr(self, 'search_input'):
                self.search_input.setVisible(False)
            if hasattr(self, 'search_button'):
                self.search_button.setVisible(False)
    
    def _on_back_to_search(self):
        """Return to search phase from results view - safe implementation"""
        try:
            # Hide results and status containers
            if hasattr(self, 'results_container') and self.results_container:
                self.results_container.setVisible(False)
            if hasattr(self, 'status_container') and self.status_container:
                self.status_container.setVisible(False)
            
            # Hide download controls safely
            controls = [
                ('back_button', self.back_button),
                ('quality_dropdown', self.quality_dropdown), 
                ('location_button', self.location_button),
                ('download_button', self.download_button)
            ]
            
            for name, widget in controls:
                try:
                    if hasattr(self, name) and widget and not widget.isHidden():
                        widget.setVisible(False)
                except RuntimeError:
                    # Widget was already deleted, skip
                    continue
            
            # Clear layout safely without deleting widgets
            if hasattr(self, 'controls_layout') and self.controls_layout:
                while self.controls_layout.count():
                    item = self.controls_layout.takeAt(0)
                    if item and item.widget():
                        item.widget().setParent(None)
            
            # Recreate search interface
            self._create_search_widget_for_controls()
            
            # Show search elements safely
            if hasattr(self, 'search_input') and self.search_input:
                self.search_input.setVisible(True)
            if hasattr(self, 'search_button') and self.search_button:
                self.search_button.setVisible(True)
                
        except Exception as e:
            print(f"Error in back button: {e}")
            # Fallback: recreate the entire search interface
            self._set_initial_state()
        
        # Clear search input for new search
        self.search_input.clear()
        self.search_input.setFocus()
        
        # Clear any selected result
        self.selected_result = None
        
        # Reset state
        self.youtube_results = []
        self.selected_youtube_index = -1
        
        # Safe widget access with existence check
        if hasattr(self, 'download_button') and self.download_button is not None:
            try:
                self.download_button.setEnabled(False)
            except RuntimeError:
                # Widget has been deleted, ignore
                pass
        
        # Clear results list safely
        self._clear_results_list()
        
        # Return to initial state layout
        self._set_initial_state()
    
    def _update_responsive_controls(self):
        """Update controls based on window size"""
        # Get available width for controls (approximate)
        available_width = self.width() - 200  # Account for margins and spacing
        
        # Threshold for switching between compact and expanded view
        compact_threshold = 800
        
        is_compact = available_width < compact_threshold
        
        if is_compact:
            # Compact mode: square buttons with symbols only
            self._style_compact_controls()
        else:
            # Expanded mode: rectangular buttons with symbols and text
            self._style_expanded_controls()
    
    def _style_compact_controls(self):
        """Style controls for compact/small window view"""
        # Back button stays square (40x40)
        self.back_button.setFixedSize(40, 40)
        self.back_button.setText("←")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
        """)
        
        # Quality dropdown: square with gear symbol only in compact mode
        self.quality_dropdown.setFixedSize(40, 40)
        
        # Clear and rebuild dropdown with quality values for proper menu display
        self.quality_dropdown.clear()
        for quality in AudioQuality:
            self.quality_dropdown.addItem(f"⚙ {quality.value}", quality)
        self.quality_dropdown.setCurrentIndex(3)  # Default to BEST
        
        # Set tooltip to show current quality
        current_quality = list(AudioQuality)[3]  # BEST
        self.quality_dropdown.setToolTip(f"Audio Quality: {current_quality.value}")
        
        # Style to show only gear symbol in compact mode
        self.quality_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                padding: 0px;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 0px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox:hover {
                background-color: #5A5A5A;
                color: white;
            }
            QComboBox:pressed {
                background-color: #4A4A4A;
            }
            QComboBox QAbstractItemView {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                selection-background-color: #5A5A5A;
            }
        """)
        
        # Force display text to show only gear symbol
        self.quality_dropdown.setEditable(True)
        self.quality_dropdown.lineEdit().setReadOnly(True)
        self.quality_dropdown.lineEdit().setText("⚙")
        self.quality_dropdown.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Connect to update tooltip when selection changes
        def update_quality_tooltip():
            selected_quality = self.quality_dropdown.currentData()
            if selected_quality:
                self.quality_dropdown.setToolTip(f"Audio Quality: {selected_quality.value}")
        
        try:
            self.quality_dropdown.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.quality_dropdown.currentIndexChanged.connect(update_quality_tooltip)
        
        # Style with custom text display - show only symbol, hide text
        self.quality_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #8E8E8E;
                color: #F5F5F5;
                border: 1px solid #666666;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                padding-left: 8px;
            }
            QComboBox:hover {
                background-color: #7A7A7A;
            }
            QComboBox::drop-down {
                border: none;
                width: 14px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #F5F5F5;
                margin-right: 2px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #666666;
                selection-background-color: #4A90E2;
                selection-color: white;
                min-width: 100px;
                font-size: 14px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                height: 25px;
                padding: 5px 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #4A90E2;
                color: white;
            }
        """)
        
        # Make combo box editable to control display text
        self.quality_dropdown.setEditable(True)
        self.quality_dropdown.setEditText("♪")
        line_edit = self.quality_dropdown.lineEdit()
        if line_edit:
            line_edit.setReadOnly(True)
            line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: transparent;
                    border: none;
                    color: #F5F5F5;
                    font-weight: bold;
                    font-size: 16px;
                }
            """)
        
        # Location button: square with symbol
        self.location_button.setFixedSize(40, 40)
        self.location_button.setText("📁")
        self.location_button.setToolTip("Download Location")
        self.location_button.setStyleSheet("""
            QPushButton {
                background-color: #8E8E8E;
                color: #F5F5F5;
                border: 1px solid #666666;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7A7A7A;
                color: white;
            }
            QPushButton:pressed {
                background-color: #6A6A6A;
            }
        """)
        
        # Download button styling - optimized for compact mode with maximum width
        self.download_button.setMinimumWidth(120)  # Ensure reasonable minimum
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #6B8E23;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 6px 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #556B2F;
            }
            QPushButton:pressed {
                background-color: #4F7942;
            }
            QPushButton:disabled {
                background-color: #9CAF88;
                color: #D3D3D3;
            }
        """)
    
    def _style_expanded_controls(self):
        """Style controls for expanded/large window view"""
        # Back button stays square (40x40)
        self.back_button.setFixedSize(40, 40)
        self.back_button.setText("←")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
        """)
        
        # Quality dropdown: rectangle with gear symbol and text in expanded mode
        self.quality_dropdown.setFixedSize(120, 40)
        
        # Clear and rebuild dropdown for expanded mode
        self.quality_dropdown.clear()
        for quality in AudioQuality:
            self.quality_dropdown.addItem(f"⚙ {quality.value}", quality)
        self.quality_dropdown.setCurrentIndex(3)  # Default to BEST
        
        # Style for expanded mode with full text display
        self.quality_dropdown.setStyleSheet("""
            QComboBox {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding-left: 8px;
                padding-right: 20px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #555555;
                background-color: #6B6B6B;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #F5F5F5;
                margin: 2px;
            }
            QComboBox:hover {
                background-color: #5A5A5A;
                color: white;
            }
            QComboBox:pressed {
                background-color: #4A4A4A;
            }
            QComboBox QAbstractItemView {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                selection-background-color: #5A5A5A;
            }
        """)
        
        # Reset to non-editable for expanded mode
        self.quality_dropdown.setEditable(False)
        
        # Set tooltip
        current_quality = list(AudioQuality)[3]  # BEST
        self.quality_dropdown.setToolTip(f"Audio Quality: {current_quality.value}")
        
        # Location button: rectangular in expanded mode
        self.location_button.setFixedSize(140, 40)
        self.location_button.setText("📁 Choose Location")
        self.location_button.setStyleSheet("""
            QPushButton {
                background-color: #6B6B6B;
                color: #F5F5F5;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
                padding-left: 8px;
                padding-right: 20px;
            }
            QComboBox:hover {
                background-color: #7A7A7A;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid #F5F5F5;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #8E8E8E;
                color: #F5F5F5;
                border: 1px solid #666666;
                selection-background-color: #7A7A7A;
                selection-color: white;
            }
        """)
        
        # Location button: rectangle with symbol and text
        self.location_button.setFixedSize(120, 40)
        self.location_button.setText("📁 Location")
        self.location_button.setToolTip("Download Location")
        self.location_button.setStyleSheet("""
            QPushButton {
                background-color: #8E8E8E;
                color: #F5F5F5;
                border: 1px solid #666666;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
                padding-left: 8px;
            }
            QPushButton:hover {
                background-color: #7A7A7A;
                color: white;
            }
            QPushButton:pressed {
                background-color: #6A6A6A;
            }
        """)
        
        # Download button styling - adapts width in expanded mode
        self.download_button.setMinimumWidth(150)  # Larger minimum for expanded mode
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #6B8E23;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                padding: 6px 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #556B2F;
            }
            QPushButton:pressed {
                background-color: #4F7942;
            }
            QPushButton:disabled {
                background-color: #9CAF88;
                color: #D3D3D3;
            }
        """)
    
    def resizeEvent(self, event):
        """Handle window resize to update responsive controls"""
        super().resizeEvent(event)
        if hasattr(self, 'quality_dropdown'):
            self._update_responsive_controls()
    
    def _on_animation_finished(self):
        """Called when transition animation completes"""
        if self.animation_group:
            self.animation_group.deleteLater()
            self.animation_group = None
    
    def _perform_search(self, query):
        """Perform the actual search operation"""
        try:
            raw_youtube_results = self.youtube.search(query, limit=15)
            filtered_youtube_results = self.song_filter.filter_youtube_results(raw_youtube_results, query)
            
            if len(filtered_youtube_results) > 5:
                filtered_youtube_results = filtered_youtube_results[:5]
            
            if not filtered_youtube_results:
                self.status_label.setText("No results found")
                QMessageBox.information(self, "No Results", "No song results found for your search term.")
                return
            
            # Process results with Spotify matching
            self.youtube_results = []
            self.processed_results = []
            
            for result in filtered_youtube_results:
                spotify_track, better_youtube = self._search_spotify_for_youtube_result(result)
                
                # Use better YouTube result if found, otherwise use original
                final_youtube_result = better_youtube if better_youtube else result
                
                should_include, reason, confidence = self.song_filter.should_include_result(
                    final_youtube_result, spotify_track, query
                )
                
                if should_include:
                    self.youtube_results.append(final_youtube_result)
                    self.processed_results.append({
                        'youtube_result': final_youtube_result,
                        'spotify_track': spotify_track,
                        'reason': reason,
                        'confidence': confidence,
                        'improved_match': better_youtube is not None
                    })
                    
                    # Continue until we have 10 results or run out of filtered results
                    if len(self.processed_results) >= 10:
                        break
            
            self.status_container.setVisible(False)
            
            if not self.youtube_results:
                QMessageBox.information(self, "No Valid Results", 
                                      "No matching songs found. Try refining your search query.")
                return
            
            # Populate results
            self._populate_results()
            
        except Exception as e:
            self.status_container.setVisible(False)
            QMessageBox.critical(self, "Search Error", f"An error occurred during search: {str(e)}")
    
    def _populate_results(self):
        """Populate the results list with search results"""
        for i, processed_result in enumerate(self.processed_results):
            result_widget = self._create_result_widget(i, processed_result)
            self.results_list_layout.addWidget(result_widget)
        
        # Add stretch to prevent cutoff of last result
        self.results_list_layout.addStretch()
        
        # Adjust scroll area height based on number of results
        self._adjust_results_height()
    
    def _adjust_results_height(self):
        """Adjust the results scroll area height based on number of results"""
        num_results = len(self.processed_results)
        result_height = 80  # Each result is 80px tall
        
        if num_results == 0:
            return
        
        # Calculate ideal height: number of results * height per result
        ideal_height = num_results * result_height
        
        # Show up to 5 results without scrolling, then scroll for more
        min_height = 80   # At least 1 result visible
        max_height = 400  # At most 5 results visible (scroll for 6-10)
        
        adjusted_height = max(min_height, min(ideal_height, max_height))
        
        # Set the height
        self.results_scroll.setFixedHeight(adjusted_height)
    
    def _create_result_widget(self, index: int, processed_result: Dict[str, Any]) -> QWidget:
        """Create a widget for displaying a search result"""
        result = processed_result['youtube_result']
        spotify_track = processed_result['spotify_track']
        reason = processed_result['reason']
        confidence = processed_result['confidence']
        
        # Main result container
        result_widget = QWidget()
        result_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                margin: 1px 0px;
            }
            QWidget:hover {
                background-color: #f5f5f5;
                border-color: #cccccc;
            }
        """)
        result_widget.setFixedHeight(80)
        result_widget.setProperty("index", index)
        
        # Horizontal layout with cover art on left, text on right
        layout = QHBoxLayout(result_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # Album cover art
        cover_label = QLabel()
        cover_label.setFixedSize(64, 64)
        cover_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f0f0f0;
            }
        """)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_label.setScaledContents(True)
        result_widget.cover_label = cover_label
        layout.addWidget(cover_label)
        
        # Text info container
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Song title
        if spotify_track and isinstance(spotify_track, dict):
            title = spotify_track.get('name', result.get('title', 'Unknown') if isinstance(result, dict) else str(result))
            artists = spotify_track.get('artists', [])
            if isinstance(artists, list) and artists:
                artist = ', '.join([a.get('name', 'Unknown') for a in artists if isinstance(a, dict)])
            else:
                artist = 'Unknown Artist'
        else:
            title = result.get('title', 'Unknown') if isinstance(result, dict) else str(result)
            artist = result.get('channel', 'Unknown Artist') if isinstance(result, dict) else 'Unknown Artist'
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
            }
        """)
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)
        
        # Channel and duration
        duration = result.get('duration', 'Unknown') if isinstance(result, dict) else 'Unknown'
        subtitle_text = artist
        if duration != 'Unknown':
            subtitle_text += f" - {duration}"
        
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
            }
        """)
        info_layout.addWidget(subtitle_label)
        
        info_layout.addStretch()
        layout.addWidget(info_widget, 1)
        
        # Selection indicator
        select_label = QLabel("✓")
        select_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #4CAF50;
                background-color: transparent;
                border: none;
                font-weight: bold;
            }
        """)
        select_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        select_label.setVisible(False)
        result_widget.select_indicator = select_label
        layout.addWidget(select_label)
        
        # Load cover art if available
        cover_url = None
        if spotify_track and isinstance(spotify_track, dict):
            # Check for direct album_art URL (simplified format)
            if spotify_track.get('album_art'):
                cover_url = spotify_track['album_art']
            # Check for nested album.images format (full API format)
            elif spotify_track.get('album', {}).get('images'):
                cover_url = spotify_track['album']['images'][0]['url']
        
        if cover_url:
            self._load_cover_art_async(result_widget, cover_url)
        else:
            self._set_no_metadata_image(cover_label)
        
        # Click handler
        def on_click(event, idx=index):
            self._select_result(idx)
        
        result_widget.mousePressEvent = on_click
        
        return result_widget
    
    def _load_cover_art_async(self, result_widget: QWidget, cover_url: str):
        """Load cover art asynchronously"""
        try:
            response = requests.get(cover_url, timeout=3)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    result_widget.cover_label.setPixmap(pixmap)
        except Exception:
            self._set_no_metadata_image(result_widget.cover_label)
    
    def _set_no_metadata_image(self, cover_label: QLabel):
        """Set a placeholder image for results without cover art"""
        cover_label.setText("♪")
        cover_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                color: #999;
                background-color: rgba(240, 240, 240, 0.8);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
        """)
    
    def _select_result(self, index: int):
        """Select a result from the search results"""
        if index < 0 or index >= len(self.processed_results):
            return
        
        # Clear previous selection
        for i in range(self.results_list_layout.count()):
            item = self.results_list_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'select_indicator'):
                    widget.select_indicator.setVisible(False)
                widget.setStyleSheet("""
                    QWidget {
                        background-color: #ffffff;
                        border: 1px solid #e0e0e0;
                        margin: 2px 0px;
                    }
                    QWidget:hover {
                        background-color: #f5f5f5;
                        border-color: #cccccc;
                    }
                """)
        
        # Select current result
        self.selected_youtube_index = index
        item = self.results_list_layout.itemAt(index)
        if item and item.widget():
            widget = item.widget()
            if hasattr(widget, 'select_indicator'):
                widget.select_indicator.setVisible(True)
            widget.setStyleSheet("""
                QWidget {
                    background-color: #e3f2fd;
                    border: 1px solid #2196f3;
                    margin: 2px 0px;
                }
            """)
        
        # Enable download button
        self.download_button.setEnabled(True)
    
    def _select_download_location(self):
        """Open file dialog to select download location"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Location", 
            self.download_location
        )
        
        if directory:
            self.download_location = directory
            self.config.download_location = directory
            self.location_button.setText(f"📁 {os.path.basename(directory)}")
    
    def _on_download_selected(self):
        """Handle download button click"""
        if self.selected_youtube_index < 0 or self.selected_youtube_index >= len(self.processed_results):
            QMessageBox.warning(self, "No Selection", "Please select a song to download.")
            return
        
        # Get selected result
        processed_result = self.processed_results[self.selected_youtube_index]
        youtube_result = processed_result['youtube_result']
        
        # Get metadata based on confidence level
        metadata = None
        if processed_result['reason'] in ['high_confidence_spotify', 'medium_confidence_spotify']:
            # Use Spotify metadata for high-confidence matches
            metadata = processed_result['spotify_track']
        elif processed_result['reason'] == 'youtube_only':
            # Extract basic metadata from YouTube title
            metadata = self._extract_youtube_metadata(youtube_result)
        
        # Get quality selection
        quality_data = self.quality_dropdown.currentData()
        quality = quality_data if quality_data else AudioQuality.BEST
        
        # Start download
        self._start_download(youtube_result['url'], metadata, quality)
    
    def _clear_results_list(self):
        """Clear all items from results list"""
        while self.results_list_layout.count():
            child = self.results_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _start_download(self, video_url: str, metadata: Optional[Dict[str, Any]], quality: AudioQuality):
        """Start download process"""
        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.warning(self, "Download in Progress", "Please wait for the current download to complete.")
            return
        
        # Show progress
        self.status_container.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        
        # Disable download button
        self.download_button.setEnabled(False)
        
        # Create and start download worker
        self.download_worker = DownloadWorker(
            video_url, 
            self.download_location, 
            metadata, 
            quality
        )
        self.download_worker.progress_updated.connect(self._update_progress)
        self.download_worker.download_complete.connect(self._on_download_complete)
        self.download_worker.start()
    
    def _update_progress(self, progress: float, status: str):
        """Update download progress"""
        self.progress_bar.setValue(int(progress))
        self.status_label.setText(status)
    
    def _on_download_complete(self, success: bool, result: str):
        """Handle download completion"""
        self.download_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(f"Download complete: {os.path.basename(result)}")
            QMessageBox.information(self, "Download Complete", f"Successfully downloaded: {os.path.basename(result)}")
        else:
            self.status_label.setText("Download failed")
            QMessageBox.critical(self, "Download Error", f"Download failed: {result}")
        
        # Hide status after a delay
        QTimer.singleShot(3000, lambda: self.status_container.setVisible(False))
    
    def _search_spotify_for_youtube_result(self, youtube_result: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Search Spotify metadata for a YouTube result and return (spotify_track, better_youtube_result)"""
        try:
            video_title = youtube_result.get('title', '')
            
            # Extract artist and song name
            clean_title = clean_search_query(video_title)
            artist, song_name = extract_song_info(clean_title)
            
            search_queries = []
            
            if artist and song_name:
                search_queries.append(f'artist:"{artist}" track:"{song_name}"')
                search_queries.append(f"{artist} {song_name}")
                search_queries.append(f'track:"{song_name}"')
            
            search_queries.append(clean_title)
            simplified_title = self._simplify_youtube_title(video_title)
            if simplified_title != clean_title:
                search_queries.append(simplified_title)
            
            # Try each search strategy
            for query in search_queries:
                spotify_results = self.spotify.search_track(query, limit=3)
                
                if spotify_results:
                    best_match = self._find_best_spotify_match(spotify_results, youtube_result)
                    if best_match:
                        # Check if duration mismatch > 5 seconds and we have artist/song info
                        duration_mismatch = self._check_duration_mismatch(best_match, youtube_result)
                        
                        if duration_mismatch > 5 and artist and song_name:
                            # Search for better YouTube video using artist - song format
                            better_youtube = self._search_better_youtube_video(artist, song_name, best_match)
                            return best_match, better_youtube
                        
                        return best_match, None
            
            return None, None
                    
        except Exception as e:
            print(f"Spotify search failed: {str(e)}")
            return None, None
    
    def _simplify_youtube_title(self, title: str) -> str:
        """Remove YouTube-specific decorations from title"""
        import re
        
        patterns = [
            r'\[.*?\]',
            r'\(.*?\)',
            r'official.*?video',
            r'official.*?audio',
            r'lyrics?',
            r'hd',
            r'4k',
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return ' '.join(cleaned.split()).strip()
    
    def _find_best_spotify_match(self, spotify_results: List[Dict[str, Any]], 
                                youtube_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the best Spotify match from search results"""
        if not spotify_results:
            return None
        
        youtube_duration = self._parse_duration_to_seconds(youtube_result.get('duration', '0:00'))
        
        best_match = None
        best_score = 0
        
        for track in spotify_results:
            score = 0
            
            # Duration matching (strict for quality)
            spotify_duration = track.get('duration_ms', 0) // 1000
            if spotify_duration > 0:  # Only check duration if available
                duration_diff = abs(spotify_duration - youtube_duration)
                if duration_diff <= 5:  # Tight duration matching
                    score += 0.6  # High score for good duration match
                elif duration_diff <= 15:  # Moderate tolerance
                    score += 0.3
                else:
                    score += 0.1  # Low score for poor duration match
            else:
                score += 0.3  # Neutral score if duration unavailable
            
            # Popularity scoring
            popularity = track.get('popularity', 0)
            score += (popularity / 100) * 0.3
            
            # Basic metadata completeness
            if track.get('name') and track.get('artists'):
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = track
        
        return best_match if best_score > 0.4 else None
    
    def _check_duration_mismatch(self, spotify_track: Dict[str, Any], youtube_result: Dict[str, Any]) -> int:
        """Check duration mismatch between Spotify and YouTube in seconds"""
        try:
            spotify_duration = spotify_track.get('duration_ms', 0) // 1000
            youtube_duration = self._parse_duration_to_seconds(youtube_result.get('duration', '0:00'))
            return abs(spotify_duration - youtube_duration)
        except:
            return 0
    
    def _search_better_youtube_video(self, artist: str, song_name: str, spotify_track: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search for a better YouTube video using artist - song format when duration mismatch > 5s"""
        try:
            search_query = f"{artist} - {song_name}"
            print(f"Duration mismatch detected, searching YouTube for: '{search_query}'")
            
            # Use the YouTube searcher to find better match
            if hasattr(self, 'youtube') and self.youtube:
                search_results = self.youtube.search(search_query, limit=5)
                
                if search_results:
                    spotify_duration = spotify_track.get('duration_ms', 0) // 1000
                    
                    # Find the result with closest duration match
                    best_youtube = None
                    best_duration_diff = float('inf')
                    
                    for result in search_results:
                        youtube_duration = self._parse_duration_to_seconds(result.get('duration', '0:00'))
                        duration_diff = abs(spotify_duration - youtube_duration)
                        
                        if duration_diff < best_duration_diff and duration_diff <= 5:
                            best_duration_diff = duration_diff
                            best_youtube = result
                    
                    if best_youtube and best_duration_diff <= 5:
                        print(f"Found better YouTube match with {best_duration_diff}s duration difference")
                        return best_youtube
            
            return None
            
        except Exception as e:
            print(f"Error searching for better YouTube video: {e}")
            return None
    
    def _parse_duration_to_seconds(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        try:
            if ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = parts
                    return int(minutes) * 60 + int(seconds)
                elif len(parts) == 3:
                    hours, minutes, seconds = parts
                    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            return 0
        except:
            return 0
    
    def _extract_youtube_metadata(self, youtube_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract basic metadata from YouTube video title and info"""
        try:
            title = youtube_result.get('title', '')
            
            # Clean the title for metadata
            clean_title = self._clean_title_for_metadata(title)
            
            # Try to extract artist and song from title
            if ' - ' in clean_title:
                parts = clean_title.split(' - ', 1)
                artist = parts[0].strip()
                song = parts[1].strip()
            elif ' by ' in clean_title.lower():
                parts = clean_title.lower().split(' by ', 1)
                song = parts[0].strip()
                artist = parts[1].strip()
            else:
                # Fallback: use channel as artist if available
                artist = youtube_result.get('channel', 'Unknown Artist')
                song = clean_title
            
            metadata = {
                'name': song,
                'artists': [{'name': artist}],
                'album': {'name': 'Unknown Album'},
                'duration_ms': self._parse_duration_to_ms(youtube_result.get('duration', '0:00'))
            }
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting YouTube metadata: {e}")
            return None
    
    def _clean_title_for_metadata(self, title: str) -> str:
        """Clean YouTube title for use as song title metadata"""
        import re
        
        # Remove common YouTube decorations
        patterns = [
            r'\[.*?\]',  # Remove anything in square brackets
            r'\(.*?\)',  # Remove anything in parentheses
            r'【.*?】',  # Remove anything in these brackets
            r'official.*?video',  # Remove "official video" etc
            r'official.*?audio',  # Remove "official audio" etc
            r'lyrics?',  # Remove "lyrics" or "lyric"
            r'hd',  # Remove "HD"
            r'4k',  # Remove "4K"
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def _parse_duration_to_ms(self, duration_str: str) -> int:
        """Parse duration string to milliseconds"""
        try:
            if ':' in duration_str:
                parts = duration_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = parts
                    return (int(minutes) * 60 + int(seconds)) * 1000
                elif len(parts) == 3:
                    hours, minutes, seconds = parts
                    return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000
            return 0
        except:
            return 0