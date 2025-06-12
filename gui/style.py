"""
Application styling
Provides the stylesheet and theming for the application
"""
from enum import Enum
from PyQt6.QtGui import QColor

class Theme(Enum):
    """Application theme"""
    DARK = "dark"
    LIGHT = "light"

# Theme Colors
class Colors:
    """Color definitions for the application"""
    # Dark theme
    DARK_BG_PRIMARY = "#2c3e50"
    DARK_BG_SECONDARY = "#4ca1af"
    DARK_SIDEBAR_BG = "rgba(0, 0, 0, 0.7)"
    DARK_TEXT_PRIMARY = "#FFFFFF"
    DARK_TEXT_SECONDARY = "#CCCCCC"
    
    # Accent colors
    ACCENT_PRIMARY = "#e63b19"
    ACCENT_PRIMARY_HOVER = "#d63013"
    ACCENT_SECONDARY = "#ffbd33"
    
    # Content area
    CONTENT_BG = "rgba(255, 255, 255, 0.95)"
    CONTENT_TEXT = "#333333"
    CONTENT_SUBTEXT = "#666666"
    
    # Status colors
    SUCCESS = "#00b894"
    ERROR = "#d63031"
    WARNING = "#fdcb6e"
    INFO = "#0984e3"
    
    # UI elements
    BORDER_COLOR = "#404040"
    BUTTON_SECONDARY_BG = "#555555"
    BUTTON_SECONDARY_HOVER = "#444444"
    INPUT_BG = "#FFFFFF"
    INPUT_TEXT = "#333333"
    TABLE_HEADER_BG = "#f0f0f0"
    TABLE_ROW_ALTERNATE = "#f9f9f9"
    TABLE_HOVER = "#f5f5f5"

def get_stylesheet(theme: Theme = Theme.DARK) -> str:
    """
    Get the application stylesheet for the given theme
    
    Args:
        theme: The application theme
        
    Returns:
        The stylesheet as a string
    """
    c = Colors()
    
    return f"""
    /* Main Window */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                  stop: 0 {c.DARK_BG_SECONDARY}, stop: 1 {c.DARK_BG_PRIMARY});
    }}
    
    /* Sidebar */
    QWidget#sidebar {{
        background-color: {c.DARK_SIDEBAR_BG};
        min-width: 200px;
        max-width: 200px;
    }}
    
    QLabel#sidebar_title {{
        color: {c.DARK_TEXT_PRIMARY};
        font-size: 16px;
        font-weight: bold;
        padding: 10px;
    }}
    
    QPushButton#sidebar_button {{
        background-color: transparent;
        color: {c.DARK_TEXT_PRIMARY};
        border: none;
        text-align: left;
        padding: 12px 20px;
        font-size: 14px;
    }}
    
    QPushButton#sidebar_button:hover {{
        background-color: rgba(255, 255, 255, 0.05);
    }}
    
    QPushButton#sidebar_button:checked {{
        background-color: rgba(255, 255, 255, 0.1);
        border-left: 3px solid #cccccc;
        font-weight: bold;
    }}
    
    /* Main Content */
    QWidget#main_content {{
        background: transparent;
    }}
    
    QLabel#page_title {{
        color: {c.DARK_TEXT_PRIMARY};
        font-size: 24px;
        font-weight: bold;
    }}
    
    /* Search Section */
    QLabel#search_label {{
        color: {c.DARK_TEXT_PRIMARY};
        font-size: 16px;
    }}
    
    QLineEdit {{
        background-color: {c.INPUT_BG};
        color: {c.INPUT_TEXT};
        border: none;
        border-radius: 4px 0 0 4px;
        padding: 10px;
        font-size: 14px;
    }}
    
    QPushButton#search_button {{
        background-color: #cccccc;
        color: #333333;
        border: none;
        border-radius: 0 4px 4px 0;
        padding: 10px 20px;
        font-weight: bold;
    }}
    
    QPushButton#search_button:hover {{
        background-color: #d9d9d9;
    }}
    
    /* Results Section */
    QWidget#results_container {{
        background-color: {c.CONTENT_BG};
        border-radius: 5px;
    }}
    
    QTabWidget {{
        background-color: transparent;
        border: none;
    }}
    
    QTabWidget::pane {{
        border: none;
        background-color: {c.CONTENT_BG};
        border-radius: 5px;
    }}
    
    QTabBar::tab {{
        background-color: {c.TABLE_HEADER_BG};
        color: {c.CONTENT_SUBTEXT};
        padding: 10px 20px;
        font-weight: bold;
    }}
    
    QTabBar::tab:selected {{
        background-color: {c.CONTENT_BG};
        color: {c.ACCENT_PRIMARY};
        border-bottom: 2px solid {c.ACCENT_PRIMARY};
    }}
    
    /* Table View */
    QTableView {{
        background-color: white;
        alternate-background-color: {c.TABLE_ROW_ALTERNATE};
        gridline-color: #e0e0e0;
        color: #333333;
    }}
    
    QTableView::item:hover {{
        background-color: {c.TABLE_HOVER};
    }}
    
    QTableView::item:selected {{
        background-color: rgba(9, 132, 227, 0.2);
        color: {c.CONTENT_TEXT};
    }}
    
    QHeaderView::section {{
        background-color: {c.TABLE_HEADER_BG};
        color: {c.CONTENT_SUBTEXT};
        padding: 10px;
        border: none;
        font-weight: bold;
    }}
    
    /* Options Bar */
    QWidget#options_bar {{
        background-color: {c.TABLE_HEADER_BG};
        border-top: 1px solid #e0e0e0;
    }}
    
    QLabel#quality_label {{
        color: {c.CONTENT_SUBTEXT};
        font-weight: bold;
    }}
    
    QComboBox {{
        padding: 6px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
        color: #333333;
    }}
    
    QLabel#location_label {{
        color: {c.CONTENT_SUBTEXT};
    }}
    
    QPushButton#location_button {{
        background-color: #cccccc;
        color: #333333;
        border: none;
        border-radius: 4px;
        padding: 8px 15px;
    }}
    
    QPushButton#location_button:hover {{
        background-color: #d9d9d9;
    }}
    
    QPushButton#download_button {{
        background-color: #cccccc;
        color: #333333;
        border: none;
        border-radius: 4px;
        padding: 10px 25px;
        font-weight: bold;
    }}
    
    QPushButton#download_button:hover {{
        background-color: #d9d9d9;
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        text-align: center;
        color: white;
        height: 20px;
    }}
    
    QProgressBar::chunk {{
        background-color: {c.ACCENT_PRIMARY};
        border-radius: 10px;
    }}
    
    /* Library Tab */
    QPushButton#library_button {{
        background-color: #cccccc;
        color: #333333;
        border: none;
        border-radius: 4px;
        padding: 8px 15px;
        font-weight: bold;
    }}
    
    QPushButton#library_button:hover {{
        background-color: #d9d9d9;
    }}
    
    QWidget#library_filters {{
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 4px;
        padding: 10px;
    }}
    
    QCheckBox {{
        color: {c.DARK_TEXT_PRIMARY};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {c.ACCENT_PRIMARY};
        border: 1px solid {c.ACCENT_PRIMARY};
    }}
    
    /* Status Label */
    QLabel#status_complete {{
        color: {c.SUCCESS};
        font-weight: bold;
    }}
    
    QLabel#status_incomplete {{
        color: {c.ERROR};
        font-weight: bold;
    }}
    
    QPushButton#get_info_button {{
        background-color: {c.ACCENT_PRIMARY};
        color: white;
        border: none;
        border-radius: 3px;
        padding: 2px 8px;
    }}
    
    QPushButton#get_info_button:hover {{
        background-color: {c.ACCENT_PRIMARY_HOVER};
    }}
    
    /* Settings Tab */
    QWidget#settings_container {{
        background-color: {c.CONTENT_BG};
        border-radius: 5px;
        padding: 20px;
    }}
    
    QLabel#settings_section_title {{
        font-size: 18px;
        font-weight: bold;
        color: {c.CONTENT_TEXT};
    }}
    
    QLabel#settings_label {{
        font-weight: bold;
        color: {c.CONTENT_TEXT};
        margin-bottom: 5px;
    }}
    
    QPushButton#save_settings_button {{
        background-color: {c.ACCENT_PRIMARY};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: bold;
    }}
    
    QPushButton#save_settings_button:hover {{
        background-color: {c.ACCENT_PRIMARY_HOVER};
    }}
    
    /* About Tab */
    QWidget#about_container {{
        background-color: {c.CONTENT_BG};
        border-radius: 5px;
        padding: 20px;
    }}
    
    QLabel#about_title {{
        font-size: 18px;
        font-weight: bold;
        color: {c.CONTENT_TEXT};
    }}
    
    QLabel#about_text {{
        color: {c.CONTENT_TEXT};
    }}
    
    QLabel#about_section_title {{
        font-size: 16px;
        font-weight: bold;
        color: {c.CONTENT_TEXT};
        margin-top: 20px;
    }}
    """