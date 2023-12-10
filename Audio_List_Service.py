import os

def list_audio_files(audio_directory):
    files = os.listdir(audio_directory)
    return files
