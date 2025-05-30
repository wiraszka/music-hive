"""
Main application window
Handles the main window layout with sidebar navigation
"""

import os
import logging
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QLabel, QPushButton, QFileDialog, QMessageBox,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QPixmap

from gui.download_tab import DownloadTab
from gui.library_tab import LibraryTab
from gui.style import get_stylesheet, Theme
from gui.audio_quality_selector import AudioQualitySelector
from utils.config import Config

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config: Config):
        """
        Initialize the main window
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.config = config
        
        # Set window properties
        self.setWindowTitle("Adam's Music Downloader")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Apply stylesheet
        self.setStyleSheet(get_stylesheet(Theme.DARK))
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar, 20)
        
        # Create stacked widget for content pages
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("main_content")
        main_layout.addWidget(self.content_stack, 80)
        
        # Create pages
        self.download_page = DownloadTab(self.config)
        self.library_page = LibraryTab(self.config)
        self.settings_page = self._create_settings_page()
        self.about_page = self._create_about_page()
        
        # Add pages to stack
        self.content_stack.addWidget(self.download_page)
        self.content_stack.addWidget(self.library_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.about_page)
        
        # Create status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Ready")
        
        # Create menu bar
        self._create_menu_bar()
    
    def _create_sidebar(self) -> QWidget:
        """
        Create the sidebar widget with navigation buttons
        
        Returns:
            Sidebar widget
        """
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # App title and icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(15, 20, 15, 20)
        
        # App icon
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.svg")
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path)
            icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        title_layout.addWidget(icon_label)
        
        # App title
        title_label = QLabel("Music Downloader")
        title_label.setObjectName("sidebar_title")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addWidget(title_container)
        layout.addSpacing(10)
        
        # Navigation buttons
        self.nav_buttons = []
        
        # Download button
        download_btn = self._create_sidebar_button("Download", "📥", 0)
        layout.addWidget(download_btn)
        self.nav_buttons.append(download_btn)
        
        # Library button
        library_btn = self._create_sidebar_button("Library", "🎵", 1)
        layout.addWidget(library_btn)
        self.nav_buttons.append(library_btn)
        
        # Settings button
        settings_btn = self._create_sidebar_button("Settings", "⚙️", 2)
        layout.addWidget(settings_btn)
        self.nav_buttons.append(settings_btn)
        
        # About button
        about_btn = self._create_sidebar_button("About", "ℹ️", 3)
        layout.addWidget(about_btn)
        self.nav_buttons.append(about_btn)
        
        # Set the first button as active
        self._set_active_button(0)
        
        # Add stretch to push remaining buttons to the bottom if needed
        layout.addStretch()
        
        return sidebar
    
    def _create_sidebar_button(self, text: str, icon_text: str, page_index: int) -> QPushButton:
        """
        Create a sidebar navigation button
        
        Args:
            text: Button text
            icon_text: Emoji or text to use as icon
            page_index: Index of the page this button should navigate to
            
        Returns:
            The created button
        """
        button = QPushButton(text)
        button.setObjectName("sidebar_button")
        button.setCheckable(True)
        
        # Create layout for button content
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(20, 12, 20, 12)
        button_layout.setSpacing(10)
        
        # Add icon (using emoji for now)
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("nav_icon")
        button_layout.addWidget(icon_label)
        
        # Add text
        text_label = QLabel(text)
        text_label.setObjectName("nav_text")
        button_layout.addWidget(text_label)
        button_layout.addStretch()
        
        # Connect click event
        button.clicked.connect(lambda: self._on_sidebar_button_clicked(page_index))
        
        return button
    
    def _on_sidebar_button_clicked(self, index: int):
        """
        Handle sidebar button click
        
        Args:
            index: Index of the page to show
        """
        self.content_stack.setCurrentIndex(index)
        self._set_active_button(index)
    
    def _set_active_button(self, active_index: int):
        """
        Set the active sidebar button
        
        Args:
            active_index: Index of the button to set as active
        """
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == active_index)
    
    def _create_settings_page(self) -> QWidget:
        """
        Create the settings page
        
        Returns:
            Settings page widget
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Title
        title = QLabel("Settings")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Settings container
        settings_container = QWidget()
        settings_container.setObjectName("settings_container")
        settings_layout = QVBoxLayout(settings_container)
        
        # Download location
        location_title = QLabel("Default Download Location")
        location_title.setObjectName("settings_label")
        settings_layout.addWidget(location_title)
        
        location_container = QWidget()
        location_layout = QHBoxLayout(location_container)
        location_layout.setContentsMargins(0, 0, 0, 0)
        
        location_label = QLabel(self.config.download_location)
        location_layout.addWidget(location_label, 1)
        
        browse_button = QPushButton("Browse")
        browse_button.setObjectName("location_button")
        browse_button.clicked.connect(self._set_download_location)
        location_layout.addWidget(browse_button)
        
        settings_layout.addWidget(location_container)
        settings_layout.addSpacing(20)
        
        # Quality settings
        quality_title = QLabel("Default Audio Quality")
        quality_title.setObjectName("settings_label")
        settings_layout.addWidget(quality_title)
        
        from gui.download_tab import AudioQualitySelector
        quality_selector = AudioQualitySelector()
        quality_selector.set_quality(self.config.default_audio_quality)
        settings_layout.addWidget(quality_selector)
        
        settings_layout.addStretch()
        layout.addWidget(settings_container)
        
        return page
    
    def _create_about_page(self) -> QWidget:
        """
        Create the about page
        
        Returns:
            About page widget
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Title
        title = QLabel("About")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # About container
        about_container = QWidget()
        about_container.setObjectName("about_container")
        about_layout = QVBoxLayout(about_container)
        
        # App info
        app_title = QLabel("Adam's Music Downloader")
        app_title.setObjectName("about_title")
        about_layout.addWidget(app_title)
        
        version_label = QLabel("Version 2.0.0")
        version_label.setObjectName("about_text")
        about_layout.addWidget(version_label)
        
        description = QLabel("A desktop application for downloading music from YouTube with Spotify metadata integration.")
        description.setObjectName("about_text")
        description.setWordWrap(True)
        about_layout.addWidget(description)
        
        author = QLabel("Created by Adam Wiraszka")
        author.setObjectName("about_text")
        about_layout.addWidget(author)
        
        # Libraries section
        libraries_title = QLabel("Libraries Used")
        libraries_title.setObjectName("about_section_title")
        about_layout.addWidget(libraries_title)
        
        libraries_text = QLabel(
            "• PyQt6 - GUI Framework\n"
            "• yt-dlp - YouTube Downloading\n"
            "• Spotipy - Spotify API Integration\n"
            "• Mutagen - Audio Metadata Handling"
        )
        libraries_text.setObjectName("about_text")
        about_layout.addWidget(libraries_text)
        
        about_layout.addStretch()
        layout.addWidget(about_container)
        
        return page
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        if not menu_bar:
            return
            
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Set download location action
        set_location_action = QAction("Set Download Location", self)
        set_location_action.triggered.connect(self._set_download_location)
        file_menu.addAction(set_location_action)
        
        # Scan library action
        scan_library_action = QAction("Scan Music Library", self)
        scan_library_action.triggered.connect(lambda: self.library_page.scan_library())
        file_menu.addAction(scan_library_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: self._on_sidebar_button_clicked(3))
        help_menu.addAction(about_action)
    
    def _set_download_location(self):
        """Open dialog to set download location"""
        current_dir = self.config.download_location
        new_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Directory",
            current_dir
        )
        
        if new_dir:
            self.config.download_location = new_dir
            self.config.save()
            
            # Update download tab with new location
            self.download_page.update_download_location(new_dir)
            self.statusBar().showMessage(f"Download location set to: {new_dir}")
    
    def closeEvent(self, event):
        """Handle window close event to save configuration"""
        # Save any pending configuration changes
        self.config.save()
        event.accept()
