import sys
import os
import tempfile
import pygame
from mutagen.mp3 import MP3
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QMessageBox, QSlider, QLabel
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QThread, pyqtSignal, QTimer
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

        # Initialize timer and elapsed time
        self.time_label = QLabel("00:00", self)
        self.total_duration_label = QLabel("00:00", self)  # Total duration
        self.elapsed_time = 0
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.update_playback)
        self.audio_length = 0

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

        # Time and playback slider layout
        time_slider_layout = QHBoxLayout()
        layout.addLayout(time_slider_layout)

        # Current time label and total duration label
        self.time_label = QLabel("00:00", self)  # Current playback time
        self.total_duration_label = QLabel(" / 00:00", self)  # Total duration
        time_slider_layout.addWidget(self.time_label)
        time_slider_layout.addWidget(self.total_duration_label)

        # Playback slider
        self.playback_slider = QSlider(Qt.Horizontal, self)
        self.playback_slider.setMinimum(0)
        self.playback_slider.setMaximum(100)
        time_slider_layout.addWidget(self.playback_slider)

        # Volume control slider
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)  # Volume range from 0 to 100
        self.volume_slider.setValue(100)  # Default volume set to 100%
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        controls_layout.addWidget(QLabel("Volume:"))
        controls_layout.addWidget(self.volume_slider)

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
            self.resume_playback()
        else:
            self.start_new_playback()

    def start_new_playback(self):
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            self.current_song = selected_item.text()
            url = f'http://localhost:8000/stream/{self.current_song}'
            safe_file_name = self.current_song.replace(" ", "_").replace("-", "_")
            self.download_thread = DownloadThread(url, safe_file_name)
            self.download_thread.download_completed.connect(self.on_download_complete)
            self.download_thread.download_failed.connect(self.on_download_failed)
            self.download_thread.start()
    
    def get_audio_length(self, file_path):
        audio = MP3(file_path)
        audio_length = audio.info.length  # length in seconds
        return int(audio_length)
    
    def update_total_duration_label(self, duration):
        mins, secs = divmod(duration, 60)
        self.total_duration_label.setText(f"{mins:02d}:{secs:02d}")

    # Check if the download was successful
    @pyqtSlot(str)
    def on_download_complete(self, file_path):
        sound = pygame.mixer.Sound(file_path)
        self.channel.play(sound)
        self.temp_file_path = file_path

        self.audio_length = self.get_audio_length(file_path)
        self.playback_slider.setMaximum(self.audio_length)
        self.playback_timer.start(1000)
        self.elapsed_time = 0
        self.update_total_duration_label(self.audio_length)
        
    @pyqtSlot(str)
    def on_download_failed(self, error_message):
        QMessageBox.warning(self, 'Download Error', error_message)

    # Pause audio method
    @pyqtSlot()
    def pause_audio(self):
        if self.channel.get_busy():
            self.channel.pause()
            self.playback_timer.stop()
            self.is_paused = True

    def resume_playback(self):
        self.channel.unpause()
        self.playback_timer.start(1000)
        self.is_paused = False

    # Stop audio method
    @pyqtSlot()
    def stop_audio(self):
        self.channel.stop()
        self.playback_timer.stop()
        self.elapsed_time = 0
        self.playback_slider.setValue(0)
        self.is_paused = False
        self.cleanup()

    def update_playback(self):
        if not self.channel.get_busy():
            self.playback_timer.stop()
            return

        self.elapsed_time += 1
        self.playback_slider.setValue(min(self.elapsed_time, self.audio_length))

        mins, secs = divmod(self.elapsed_time, 60)
        self.time_label.setText(f"{mins:02d}:{secs:02d}")

    def adjust_volume(self, value):
        volume_level = value / 100  # Convert to a range between 0 and 1
        self.channel.set_volume(volume_level)

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