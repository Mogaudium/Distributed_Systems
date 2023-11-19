import sys
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot
import requests
from tempfile import NamedTemporaryFile

# Initialize Pygame's mixer with some common frequency and size
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login and Register')
        self.setGeometry(600, 300, 300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.username_entry = QLineEdit(self)
        self.username_entry.setPlaceholderText('Username')
        layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setPlaceholderText('Password')
        layout.addWidget(self.password_entry)

        login_button = QPushButton('Login', self)
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

        register_button = QPushButton('Register', self)
        register_button.clicked.connect(self.attempt_register)
        layout.addWidget(register_button)

        self.central_widget.setLayout(layout)

    @pyqtSlot()
    def attempt_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        # Here, replace with the actual request to your server
        response = requests.post('http://localhost:5000/login', data={'username': username, 'password': password})
        if response.status_code == 200:
            self.main_app_window = MainAppWindow()
            self.main_app_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Login failed', 'Incorrect username or password')

    @pyqtSlot()
    def attempt_register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        # Here, replace with the actual request to your server
        response = requests.post('http://localhost:5000/register', data={'username': username, 'password': password})
        if response.status_code == 200:
            QMessageBox.information(self, 'Registration successful', 'You can now log in with your new credentials.')
        else:
            QMessageBox.warning(self, 'Registration failed', 'The registration process has failed.')


class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Audio Client')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.play_selected_file)
        layout.addWidget(play_button)

        update_list_button = QPushButton('Update List', self)
        update_list_button.clicked.connect(self.update_file_list)
        layout.addWidget(update_list_button)

        self.central_widget.setLayout(layout)

    def play_selected_file(self):
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            selected_file = selected_item.text()
            url = f'http://localhost:5000/stream/{selected_file}'
            try:
                # Stream the audio file from the server
                with requests.get(url, stream=True) as response:
                    if response.status_code == 200:
                        # Save the streamed audio to a temporary file
                        with NamedTemporaryFile(delete=True, suffix='.mp3') as tmp_file:
                            for chunk in response.iter_content(chunk_size=4096):
                                tmp_file.write(chunk)
                            tmp_file.seek(0)  # Rewind the file
                            # Play the audio file using pygame
                            pygame.mixer.music.load(tmp_file.name)
                            pygame.mixer.music.play()
                    else:
                        QMessageBox.warning(self, 'Stream Error', 'Failed to stream file')
            except Exception as e:
                QMessageBox.warning(self, 'Playback Error', f'An error occurred while trying to play the file: {e}')

    @pyqtSlot()
    def update_file_list(self):
        response = requests.get('http://localhost:5000/list-audio')
        if response.status_code == 200:
            file_list = response.json()
            self.list_widget.clear()
            self.list_widget.addItems(file_list)
        else:
            QMessageBox.warning(self, 'Error', 'Failed to retrieve file list')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
