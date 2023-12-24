import pkg_resources
import subprocess
import sys

# Function to install missing Python dependencies
def install_dependencies():
    required = {'pygame', 'mutagen', 'requests', 'PyQt5', 'Flask', 'flask_mysqldb', 'Werkzeug'}
    installed = {pkg.key for pkg in pkg_resources.working_set} # Checks what dependancies are missing
    missing = required - installed

    if missing:
        print("Installing missing dependencies...")
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', *missing])

install_dependencies()