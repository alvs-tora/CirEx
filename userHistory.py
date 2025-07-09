from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, 
                             QMainWindow, QTableWidgetItem, QFrame, QGroupBox,QHBoxLayout, QStyleOptionTabWidgetFrame,
                             QListWidget, QSpacerItem, QSizePolicy, QMessageBox, QHeaderView, QTableWidget, QStackedWidget)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os

class userHistorydWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(f"{self.BASE_DIR}/ui/userHistory.ui", self)  

        self.saved_records = self.findChild(QWidget, "saved_records")
        self.operation_tab = self.findChild(QListWidget, "operation_tab")
        self.operation_content = self.findChild(QStackedWidget, "operation_content")