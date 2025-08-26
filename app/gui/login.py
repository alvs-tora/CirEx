import sys, os, pymysql

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFrame, QGroupBox, QHBoxLayout,
    QVBoxLayout, QPushButton, QListWidget, QSpacerItem, QSizePolicy,
    QMessageBox, QDesktopWidget, QAction, QLineEdit, QMainWindow
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5 import uic

from ultralytics import YOLO
from ..database import DatabaseConnection
from ..config import UI_PATH, RESOURCES_PATH
from .. import __version__


class Login(QMainWindow):
    """
    Login window that handles user authentication via MySQL database.
    Displays a fullscreen login window with username/password input,
    validates the user, and stores the authenticated user's project ID.
    """

    def __init__(self):
        """Initialize the login window, set up UI, icons, and database connection."""
        super().__init__()
        self.pro_id = None  # Store the logged-in user's project ID
        self.login_success = False  # Track if login succeeded
        self.db = DatabaseConnection(use_local=True)

        # Load the login UI file
        uic.loadUi(os.path.join(UI_PATH, "loginWindow.ui"), self)
        self.showMaximized()

        # Show version info
        self.version_label.setText(f"version: {__version__}")

        # Setup icons for username and password fields
        user_icon = QIcon(os.path.join(RESOURCES_PATH, "user.svg"))
        password_icon = QIcon(os.path.join(RESOURCES_PATH, "lock.svg"))

        self.username.addAction(QAction(user_icon, "", self.username), QLineEdit.LeadingPosition)
        self.password.addAction(QAction(password_icon, "", self.password), QLineEdit.LeadingPosition)

        # Set logos
        self.usersIcon.setPixmap(QPixmap(os.path.join(RESOURCES_PATH, "logo2.png")))
        self.logo.setPixmap(QPixmap(os.path.join(RESOURCES_PATH, "the_project.png")))

        # Button click events
        self.login.clicked.connect(self.check_login)
        self.exit.clicked.connect(self.handle_exit)

    def keyPressEvent(self, event):
        """Handle Enter/Return key to trigger login."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.check_login()
        else:
            super().keyPressEvent(event)

    def check_login(self):
        """
        Validate username and password entered by the user.
        If valid, store the pro_id, set success flag, and close window.
        Otherwise, show an error message.
        """
        username = self.username.text()
        password = self.password.text()

        pro_id = self.validate_login(username, password)

        if pro_id is not None:
            self.pro_id = pro_id  # Save pro_id for later access
            self.login_success = True
            QMessageBox.information(self, "Success", "Login Successful.")
            self.close()
        else:
            QMessageBox.critical(self, "Login Error", "Invalid username or password.")

    def validate_login(self, username, password):
        """
        Connect to the database and check if the given username/password exists.
        Returns:
            pro_id (int): User's project ID if login is successful.
            None: If login fails or database error occurs.
        """
        connection = self.db.connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT pro_id FROM account_info WHERE u_name = %s AND p_word = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()

                if result:
                    return result[0]  # Return pro_id
                else:
                    return None
            except pymysql.MySQLError as e:
                print(f"Database query error: {e}")
                return None
            finally:
                connection.close()
        return None

    def handle_exit(self):
        """Close the login window without authentication."""
        self.login_success = False
        self.close()


def run_login_window():
    """
    Run the login window as a standalone application.
    Returns:
        pro_id (int): If login is successful.
        None: If login fails or is cancelled.
    """
    app = QApplication(sys.argv)
    login_window = Login()
    login_window.show()

    app.exec_()  # Wait until window closes

    if login_window.login_success:
        return login_window.pro_id
    else:
        return None
