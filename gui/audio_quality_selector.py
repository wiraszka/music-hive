"""
Audio quality selector widget
"""

from PyQt6.QtWidgets import QComboBox
from downloader import AudioQuality

class AudioQualitySelector(QComboBox):
    """Widget for selecting audio quality"""
    
    def __init__(self, parent=None):
        """
        Initialize the audio quality selector
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Add quality options
        self.addItem("Best (320k)", AudioQuality.BEST.value)
        self.addItem("High (256k)", AudioQuality.HIGH.value)
        self.addItem("Medium (192k)", AudioQuality.MEDIUM.value)
        self.addItem("Low (128k)", AudioQuality.LOW.value)
        
    def get_quality(self) -> str:
        """
        Get the selected quality value
        
        Returns:
            The selected quality value
        """
        return self.currentData()
    
    def set_quality(self, quality: str):
        """
        Set the selected quality
        
        Args:
            quality: Quality value to select
        """
        index = self.findData(quality)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            # Default to best quality if not found
            self.setCurrentIndex(0)