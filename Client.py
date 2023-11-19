import sys
import tempfile
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot
import requests
import os

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
        self.setWindowTitle('Chinese Spotify')
        self.setGeometry(100, 100, 800, 600)
        self.temp_file_path = None
        self.current_song = None
        self.is_paused = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        play_button = QPushButton('Play', self)
        play_button.clicked.connect(self.play_selected_file)
        layout.addWidget(play_button)

        pause_button = QPushButton('Pause', self)
        pause_button.clicked.connect(self.pause_audio)
        layout.addWidget(pause_button)

        stop_button = QPushButton('Stop', self)
        stop_button.clicked.connect(self.stop_audio)
        layout.addWidget(stop_button)

        update_list_button = QPushButton('Update List', self)
        update_list_button.clicked.connect(self.update_file_list)
        layout.addWidget(update_list_button)

        self.central_widget.setLayout(layout)

    def cleanup(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
            self.temp_file_path = None

    @pyqtSlot()
    def play_selected_file(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            selected_item = self.list_widget.currentItem()
            if selected_item is not None:
                self.current_song = selected_item.text()
                url = f'http://localhost:5000/stream/{self.current_song}'
                response = requests.get(url)
                if response.status_code == 200:
                    temp_dir = tempfile.gettempdir()
                    self.temp_file_path = os.path.join(temp_dir, os.path.basename(self.current_song))
                    with open(self.temp_file_path, 'wb') as tmp_file:
                        tmp_file.write(response.content)
                        pygame.mixer.music.load(self.temp_file_path)
                        pygame.mixer.music.play()
                else:
                    QMessageBox.warning(self, 'Stream Error', 'Failed to stream file')

    @pyqtSlot()
    def pause_audio(self):
        pygame.mixer.music.pause()
        self.is_paused = True

    @pyqtSlot()
    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        self.cleanup()

    @pyqtSlot()
    def update_file_list(self):
        response = requests.get('http://localhost:5000/list-audio')
        if response.status_code == 200:
            self.list_widget.clear()
            self.list_widget.addItems(response.json())
        else:
            QMessageBox.warning(self, 'Error', 'Failed to retrieve file list')

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())
