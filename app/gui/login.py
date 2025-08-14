
import sys, os, pymysql

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QFrame, QGroupBox, QHBoxLayout,
                             QVBoxLayout, QPushButton, QListWidget, QSpacerItem, QSizePolicy, 
                             QMessageBox, QDesktopWidget, QAction, QLineEdit, QMainWindow, QDialog)
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QGuiApplication)
from PyQt5.QtCore import (Qt, QSize, QThread, pyqtSignal)
from PyQt5 import (QtWidgets, QtCore, uic)

from ultralytics import YOLO
from ..database import DatabaseConnection

from .. import __version__
print(f"App Version: {__version__}")

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.pro_id = None  # Store the pro_id here
        
        self.db = DatabaseConnection(use_local=True)

        base_path = os.path.dirname(os.path.abspath(__file__)) 
        ui_path = base_path + "\\ui"
        resources_path = base_path + "\\resources\\icon"

        uic.loadUi(f"{ui_path}\\login.ui", self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.showFullScreen()

        self.version_label.setText(f"version: {__version__}")

        # Create an action with an icon
        user_icon = QIcon(f"{resources_path}\\user.svg")  # Path to your icon
        password_icon = QIcon(f"{resources_path}\\lock.svg")

        user_action = QAction(user_icon, "", self.username)
        password_action = QAction(password_icon, "", self.password)

        # Add the action to the line edit (left side)
        self.username.addAction(user_action, QLineEdit.LeadingPosition)
        self.password.addAction(password_action, QLineEdit.LeadingPosition)

        self.usersIcon.setPixmap(QPixmap(f"{resources_path}\\logo2.png"))

        self.logo.setPixmap(QPixmap(f"{resources_path}\\the_project.png"))
        self.login.clicked.connect(self.check_login)
        self.exit.clicked.connect(self.handle_exit)


    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.check_login()
        else:
            super().keyPressEvent(event)

    def check_login(self):
        username = self.username.text()
        password = self.password.text()

        pro_id = self.validate_login(username, password)

        if pro_id is not None:
            self.pro_id = pro_id  # ✅ Save pro_id for later access
            QMessageBox.information(self, "Success", "Login Successful.")
            self.accept()
        else:
            QMessageBox.critical(self, "Failure", "Invalid username or password.")

    def validate_login(self, username, password):
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT pro_id FROM account_info WHERE u_name = %s AND p_word = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()

                if result:
                    return result[0]  # Return the pro_id
                else:
                    return None
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()

        return None

    def handle_exit(self):
        print("test")
        self.close()
    
def run_login_window():
    app = QApplication(sys.argv)
    login_window = Login()
    
    result = login_window.exec_()
    #print(f"Login dialog closed with result: {result}")  # Debugging statement

    if result == 1:  # 0 means success (accepted)
        return login_window.pro_id
    else:
        return None
