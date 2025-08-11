# hover_widget.py
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QMainWindow, QTableWidgetItem, QFrame, QGroupBox,QHBoxLayout, QStyleOptionTabWidgetFrame,
                             QListWidget, QSpacerItem, QSizePolicy, QMessageBox, QHeaderView, QTableWidget)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(f"{self.BASE_DIR}/ui/dashboard.ui", self)  
        
        self.dashboard = self.findChild(QWidget, "dashboard")
        self.saved_record = self.findChild(QPushButton, "saved_record")
        self.live_detection_btn = self.findChild(QPushButton, "live_detection_btn")
        self.user_name_label = self.findChild(QLabel, "user_name_label")
        self.logout = self.findChild(QPushButton, "logout")

        self.logo.setPixmap(QPixmap("icon/logo3.png"))
        self.live_detection_btn.setIcon(QIcon("icon/camera.svg"))
        self.live_detection_btn.setIconSize(QSize(20, 15))
        self.saved_record.setIcon(QIcon("icon/bookmark.svg"))
        self.saved_record.setIconSize(QSize(20, 15))
        self.settings.setIcon(QIcon("icon/settings.svg"))
        self.settings.setIconSize(QSize(20, 15))
        self.logout.setIcon(QIcon("icon/log-out.svg"))
        self.logout.setIconSize(QSize(20, 15))

        
 
