import sys
import os
import tempfile
import pygame
from mutagen.mp3 import MP3
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QMessageBox, QSlider, QLabel
from PyQt5.QtCore import pyqtSlot, Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

# Initialize the Pygame mixer for audio playback# Initialize the Pygame mixer for audio playback
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

# Class for handling file download in a separate thread
class DownloadThread(QThread):
    # Signals to communicate with the main thread
    download_completed = pyqtSignal(str)
    download_failed = pyqtSignal(str)

    # Constructor to initialize the thread
    def __init__(self, url, safe_file_name):
        QThread.__init__(self)
        self.url = url # URL of the file to download
        self.safe_file_name = safe_file_name # File name for saving

     # The main logic of the thread
    def run(self):
        try:
            response = requests.get(self.url, stream=True) # Send a GET request to the URL
            if response.status_code == 200: # Check if the request was successful (HTTP 200 OK)
                temp_file_path = os.path.join(tempfile.gettempdir(), self.safe_file_name + '.mp3') # Generate a temporary file path for downloading

                # Open the temporary file for writing binary data
                with open(temp_file_path, 'wb') as tmp_file:
                    for chunk in response.iter_content(4096):
                        tmp_file.write(chunk)
                # Emit the download_completed signal with the file path
                self.download_completed.emit(temp_file_path)
            else:
                # Emit the download_failed signal with an error message
                self.download_failed.emit('Failed to download file.')
        except Exception as e:
            self.download_failed.emit(str(e)) # If an exception occurs, emit the download_failed signal with the exception message

# Class for the login window (Everythig is kind of self explanatory)
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

    # Method to handle login attempts
    @pyqtSlot()
    def attempt_login(self):
        username = self.username_entry.text() # Username entry
        password = self.password_entry.text() # Password entry
        response = requests.post('http://192.168.1.6:8000/login', data={'username': username, 'password': password}) # POST method for username and password
        if response.status_code == 200: # If the response is 200, log in the user and open MainAppWindow
            self.main_app_window = MainAppWindow()
            self.main_app_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Login failed', 'Incorrect username or password') 

    # Method to handle registration attempts
    @pyqtSlot()
    def attempt_register(self):
        username = self.username_entry.text() # Username entry
        password = self.password_entry.text() # Password entry
        response = requests.post('http://192.168.1.6:8000/register', data={'username': username, 'password': password}) # POST method for username and password
        if response.status_code == 200: # If the response is 200, register the user
            QMessageBox.information(self, 'Registration successful', 'You can now log in with your new credentials.')
        else:
            QMessageBox.warning(self, 'Registration failed', 'The registration process has failed.')

# Main window with play and other methods
class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chinese Spotify') # Set the title of the app
        self.setGeometry(100, 100, 800, 600) # Set the position and size of the window (x, y, width, height)

        self.channel = pygame.mixer.Channel(0)  # Create a Channel object

        # Initialize timer and elapsed time
        self.time_label = QLabel("00:00", self) # Label for showing the current elapsed time of the song
        self.total_duration_label = QLabel("00:00", self)  # Total duration
        self.elapsed_time = 0 # Variable to track the elapsed time of the currently playing song
        self.playback_timer = QTimer(self) # Elapsed time of the song playing 
        self.playback_timer.timeout.connect(self.update_playback) # Connect the timer's timeout signal to the update_playback method
        self.audio_length = 0 # Variable to store the total length of the current song

        self.temp_file_path = None # Variable to store the path of the currently playing song file
        self.current_song = None # Variable to store the name of the currently playing song
        self.is_paused = False # Boolean flag to track whether the current song is paused

        # Setup UI
        self.setup_ui()

    # Method to set up the user interface
    def setup_ui(self):

        # Get the directory of the current script
        script_dir = os.path.dirname(__file__)

        # Define relative paths to the icons
        play_icon_path = os.path.join(script_dir, 'control_layout', 'play.png')
        pause_icon_path = os.path.join(script_dir, 'control_layout', 'pause.png')
        stop_icon_path = os.path.join(script_dir, 'control_layout', 'stop.png')
        update_icon_path = os.path.join(script_dir, 'control_layout', 'update.png')
 
        self.central_widget = QWidget() # Create a central widget for the main window
        self.setCentralWidget(self.central_widget) # Set the created widget as the central widget of the main window
        layout = QVBoxLayout() # Create a vertical box layout

        self.list_widget = QListWidget(self) # Create a QListWidget to display a list of songs
        layout.addWidget(self.list_widget) # Add the list widget to the vertical layout

        # Playback controls layout
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)

        # Playback control buttons
        self.play_button = QPushButton(QIcon(play_icon_path), ' Play')
        self.play_button.setIconSize(QSize(40, 40))
        self.play_button.clicked.connect(self.play_selected_file)
        controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton(QIcon(pause_icon_path), ' Pause')
        self.pause_button.setIconSize(QSize(40, 40))
        self.pause_button.clicked.connect(self.pause_audio)
        controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton(QIcon(stop_icon_path), ' Stop')
        self.stop_button.setIconSize(QSize(40, 40))
        self.stop_button.clicked.connect(self.stop_audio)
        controls_layout.addWidget(self.stop_button)

        self.update_list_button = QPushButton(QIcon(update_icon_path), ' Update song list')
        self.update_list_button.setIconSize(QSize(40, 40))
        self.update_list_button.clicked.connect(self.update_file_list)
        controls_layout.addWidget(self.update_list_button)

        # Time and volume controls layout
        time_volume_layout = QHBoxLayout()
        layout.addLayout(time_volume_layout)

        # Time labels
        time_volume_layout.addWidget(self.time_label)
        time_volume_layout.addWidget(self.total_duration_label)

        # Playback slider
        self.playback_slider = QSlider(Qt.Horizontal, self)
        self.playback_slider.setMinimum(0)
        self.playback_slider.setMaximum(100)
        time_volume_layout.addWidget(self.playback_slider)

        # Volume control slider
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        time_volume_layout.addWidget(QLabel("Volume:"))
        time_volume_layout.addWidget(self.volume_slider)

        self.central_widget.setLayout(layout)

    # Update existing songs
    @pyqtSlot()
    def update_file_list(self):
        response = requests.get('http://192.168.1.6:8000/list-audio')
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

    # Method to start playing a new song
    def start_new_playback(self):
        selected_item = self.list_widget.currentItem() # Retrieve the currently selected item from the list widget
        if selected_item is not None:
            self.current_song = selected_item.text()
            url = f'http://192.168.1.6:8000/stream/{self.current_song}' # Form the URL to stream the selected song
            safe_file_name = self.current_song.replace(" ", "_").replace("-", "_") # Replace spaces and hyphens in the song name for safe file naming

            # Initialize a new download thread with the URL and safe file name
            self.download_thread = DownloadThread(url, safe_file_name)
            self.download_thread.download_completed.connect(self.on_download_complete) # Connect a signal to a slot for download completion
            self.download_thread.download_failed.connect(self.on_download_failed) # Connect a signal to a slot for download failure
            self.download_thread.start() # Start the download thread.
    
    # Method to retrieve the length of an audio file
    def get_audio_length(self, file_path):
        audio = MP3(file_path) # Load the MP3 file from the given file path
        audio_length = audio.info.length  # length in seconds
        return int(audio_length) # Convert the length to an integer and return it
    
    # Method to update the total duration label
    def update_total_duration_label(self, duration):
        mins, secs = divmod(duration, 60) # Divide the duration in seconds by 60 to get minutes and seconds
        self.total_duration_label.setText(f"{mins:02d}:{secs:02d}") # Update the label text with the formatted time

    # Check if the download was successful
    @pyqtSlot(str)
    def on_download_complete(self, file_path):
        sound = pygame.mixer.Sound(file_path) # Load the downloaded audio file into a Pygame mixer Sound object
        self.channel.play(sound) # Play the loaded sound through the previously created Pygame mixer Channel
        self.temp_file_path = file_path  # Store the file path of the downloaded audio file

        self.audio_length = self.get_audio_length(file_path) # Retrieve the length of the audio file in seconds
        self.playback_slider.setMaximum(self.audio_length) # Set the maximum value of the playback slider to the length of the audio file
        self.playback_timer.start(1000) # Start a timer to update the playback position every second (1000 milliseconds)
        self.elapsed_time = 0 # Reset the elapsed time for the new audio track
        self.update_total_duration_label(self.audio_length) # Update the label showing the total duration of the track

    # Method called when a download fails  
    @pyqtSlot(str)
    def on_download_failed(self, error_message):
        QMessageBox.warning(self, 'Download Error', error_message) 

    # Method to pause the audio (It is also self explanatory)
    @pyqtSlot()
    def pause_audio(self):
        if self.channel.get_busy():
            self.channel.pause()
            self.playback_timer.stop()
            self.is_paused = True

    # Method to resume playback after pausing (It is also self explanatory)
    def resume_playback(self):
        self.channel.unpause()
        self.playback_timer.start(1000)
        self.is_paused = False

    # Method to stop the audio (It is also self explanatory)
    @pyqtSlot()
    def stop_audio(self):
        self.channel.stop()
        self.playback_timer.stop()
        self.elapsed_time = 0
        self.playback_slider.setValue(0)
        self.is_paused = False
        self.cleanup()

    # Method to update elapsed time of the song 
    def update_playback(self):
        if not self.channel.get_busy(): # Check if the audio channel is still playing the sound
            self.playback_timer.stop() # If the channel is no longer playing, stop the timer
            return

        self.elapsed_time += 1 # Increment the elapsed time by one second
        self.playback_slider.setValue(min(self.elapsed_time, self.audio_length)) # Update the playback slider position

        mins, secs = divmod(self.elapsed_time, 60) # Convert elapsed time to minutes and seconds
        self.time_label.setText(f"{mins:02d}:{secs:02d}") # Update the time label to show the current playback time

    # Method to adjust the volume
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