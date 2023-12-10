from flask import send_from_directory
from werkzeug.utils import safe_join

def stream_audio_file(app, filename):
    directory = safe_join(app.root_path, 'audio_files')
    return send_from_directory(directory, filename)
