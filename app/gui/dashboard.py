from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QMainWindow, QTableWidgetItem, QFrame, QGroupBox, QHBoxLayout, QStyleOptionTabWidgetFrame,
                             QListWidget, QSpacerItem, QSizePolicy, QMessageBox, QHeaderView, QTableWidget)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5 import uic
from ..config import UI_PATH, RESOURCES_PATH
import os


class DashboardWidget(QWidget):
    """
    Dashboard widget for the main application interface.
    Loads the dashboard UI, configures button icons, and provides
    access to key UI elements like live detection, saved records, and logout.
    """

    def __init__(self, parent=None):
        """
        Initialize the dashboard UI and set up widgets/icons.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Load dashboard UI from .ui file
        uic.loadUi(os.path.join(UI_PATH, "dashboard.ui"), self)

        # Retrieve important UI elements from the loaded UI
        self.dashboard = self.findChild(QWidget, "dashboard")
        self.saved_record = self.findChild(QPushButton, "saved_record")
        self.live_detection_btn = self.findChild(QPushButton, "live_detection_btn")
        self.user_name_label = self.findChild(QLabel, "user_name_label")
        self.logout = self.findChild(QPushButton, "logout")

        # Set the dashboard logo
        self.logo.setPixmap(QPixmap(os.path.join(RESOURCES_PATH, "logo3.png")))

        # Configure icons for dashboard buttons
        self.live_detection_btn.setIcon(QIcon(os.path.join(RESOURCES_PATH, "camera.svg")))
        self.live_detection_btn.setIconSize(QSize(20, 15))

        self.saved_record.setIcon(QIcon(os.path.join(RESOURCES_PATH, "bookmark.svg")))
        self.saved_record.setIconSize(QSize(20, 15))

        self.settings.setIcon(QIcon(os.path.join(RESOURCES_PATH, "settings.svg")))
        self.settings.setIconSize(QSize(20, 15))

        self.logout.setIcon(QIcon(os.path.join(RESOURCES_PATH, "log-out.svg")))
        self.logout.setIconSize(QSize(20, 15))
