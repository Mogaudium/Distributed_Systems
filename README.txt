Chinese Spotify is an audio streaming application developed using Flask microservices, load balancing, and a client interface. The application consists of several components including individual microservices for registration, login, audio listing, audio streaming, a central server, a load balancer, and a client interface.

Requirements:
Python 3.9 or higher
Flask
Flask-MySQLdb
Pygame
Mutagen
PyQt5
Requests

Please note that inside the Chinese_Spotify, there is a script that automatically checks if the dependencies are installed, if not the script will download all the needed dependecies.

Setup and Installation:
Ensure Python 3.9 or higher is installed on your system.
Clone or download the Chinese Spotify repository to your local machine.

Navigate to the downloaded directory.

Running the Application:

Create MySQL database with the following commands:

1. CREATE DATABASE audio_app;

2. USE audio_app;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

3. Register the user with username and password and then log in


Start Microservices: Run Chinese_Spotify.py. This script automatically launches all necessary microservices, servers, the load balancer and a script to download all the required dependecies.

Microservices for registration, login, audio listing, and streaming will start on ports 5003, 5004, 5010, and 5020 respectively.
Server instances will start on ports 5000, 5001, and 5002.
The load balancer operates on port 8000.
Client Interface: Run Client.py to launch the client interface.

The client interface provides functionalities like user registration, login, audio file listing, and streaming.

Usage:
Registration and Login: Users need to register and log in to access the audio streaming services.
Audio Streaming: Once logged in, users can browse through the list of available audio files and stream their choice.

Notes:
The client communicates with the server through the load balancer, ensuring efficient distribution of requests across server instances.
The server redirects requests to appropriate microservices based on the nature of the request (registration, login, audio listing, streaming).
Audio files must be placed in the audio_files directory located in the same directory as the microservices scripts.