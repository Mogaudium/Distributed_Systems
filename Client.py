import sys
import os
import tempfile
import pygame
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QMessageBox, QSlider
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Initialize Pygame
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

# Threading subclass
class DownloadThread(QThread):
    download_completed = pyqtSignal(str)
    download_failed = pyqtSignal(str)

    def __init__(self, url, safe_file_name):
        QThread.__init__(self)
        self.url = url
        self.safe_file_name = safe_file_name

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            if response.status_code == 200:
                temp_file_path = os.path.join(tempfile.gettempdir(), self.safe_file_name + '.mp3')
                with open(temp_file_path, 'wb') as tmp_file:
                    for chunk in response.iter_content(4096):
                        tmp_file.write(chunk)
                self.download_completed.emit(temp_file_path)
            else:
                self.download_failed.emit('Failed to download file.')
        except Exception as e:
            self.download_failed.emit(str(e))

# Login window that leads to the main window
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

    # Sends the data to server for verification 
    @pyqtSlot()
    def attempt_login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        response = requests.post('http://localhost:8000/login', data={'username': username, 'password': password})
        if response.status_code == 200:
            self.main_app_window = MainAppWindow()
            self.main_app_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Login failed', 'Incorrect username or password')

    # Send the registration data to the server
    @pyqtSlot()
    def attempt_register(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        response = requests.post('http://localhost:8000/register', data={'username': username, 'password': password})
        if response.status_code == 200:
            QMessageBox.information(self, 'Registration successful', 'You can now log in with your new credentials.')
        else:
            QMessageBox.warning(self, 'Registration failed', 'The registration process has failed.')

# Main window with play and etc methods
class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chinese Spotify')
        self.setGeometry(100, 100, 800, 600)
        self.channel = pygame.mixer.Channel(0)  # Create a Channel object
        self.temp_file_path = None
        self.current_song = None
        self.is_paused = False

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Playback controls layout
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)

        # Playback control buttons
        self.play_button = QPushButton(QIcon(r'C:\Users\annao\OneDrive\Έγγραφα\GitHub\Distributed_Systems\control_layout/play.png'), '')
        self.play_button.setIconSize(QSize(40, 40))
        self.play_button.clicked.connect(self.play_selected_file)
        controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton(QIcon(r'C:\Users\annao\OneDrive\Έγγραφα\GitHub\Distributed_Systems\control_layout/pause.png'), '')
        self.pause_button.setIconSize(QSize(40, 40))
        self.pause_button.clicked.connect(self.pause_audio)
        controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton(QIcon(r'C:\Users\annao\OneDrive\Έγγραφα\GitHub\Distributed_Systems\control_layout/stop.png'), '')
        self.stop_button.setIconSize(QSize(40, 40))
        self.stop_button.clicked.connect(self.stop_audio)
        controls_layout.addWidget(self.stop_button)

        self.update_list_button = QPushButton(QIcon(r'C:\Users\annao\OneDrive\Έγγραφα\GitHub\Distributed_Systems\control_layout/update.png'), '')
        self.update_list_button.setIconSize(QSize(40, 40))
        self.update_list_button.clicked.connect(self.update_file_list)
        controls_layout.addWidget(self.update_list_button)

        # Playback slider
        self.playback_slider = QSlider(Qt.Horizontal, self)
        self.playback_slider.setMinimum(0)
        self.playback_slider.setMaximum(100)  
        controls_layout.addWidget(self.playback_slider)

        self.central_widget.setLayout(layout)

    # Update existing songs
    @pyqtSlot()
    def update_file_list(self):
        response = requests.get('http://localhost:8000/list-audio')
        if response.status_code == 200:
            self.list_widget.clear()
            self.list_widget.addItems(response.json())
        else:
            QMessageBox.warning(self, 'Error', 'Failed to retrieve file list')

    # Play selected song
    @pyqtSlot()
    def play_selected_file(self):
        if self.is_paused:
            self.channel.unpause()
            self.is_paused = False
        else:
            selected_item = self.list_widget.currentItem()
            if selected_item is not None:
                self.current_song = selected_item.text()
                url = f'http://localhost:8000/stream/{self.current_song}'
                safe_file_name = self.current_song.replace(" ", "_").replace("-", "_")
                self.download_thread = DownloadThread(url, safe_file_name)
                self.download_thread.download_completed.connect(self.on_download_complete)
                self.download_thread.download_failed.connect(self.on_download_failed)
                self.download_thread.start()

    # Check if the download was successful
    @pyqtSlot(str)
    def on_download_complete(self, file_path):
        sound = pygame.mixer.Sound(file_path)
        self.channel.play(sound)  # Play the sound on the channel
        self.temp_file_path = file_path
        
    @pyqtSlot(str)
    def on_download_failed(self, error_message):
        QMessageBox.warning(self, 'Download Error', error_message)

    # Pause audio method
    @pyqtSlot()
    def pause_audio(self):
        if self.channel.get_busy():  # Check if the channel is playing
            self.channel.pause()  # Pause the channel
            self.is_paused = True

    # Stop audio method
    @pyqtSlot()
    def stop_audio(self):
        self.channel.stop()  # Stop the channel
        self.is_paused = False
        self.cleanup()  # Perform cleanup after stopping

    # Delete temp file
    def cleanup(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.remove(self.temp_file_path)  # Attempt to delete the temporary file
            except Exception as e:
                print(f"Error deleting file: {e}")
            self.temp_file_path = None

    # Close event method
    def closeEvent(self, event):
        self.cleanup()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())