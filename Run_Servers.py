import subprocess
import sys

def run_server(port):
    subprocess.Popen([sys.executable, "Server.py", str(port)])

if __name__ == "__main__":
    ports = [5000, 5001, 5002]  # 3 Different ports, for 3 instances of Flask app
    for port in ports:
        run_server(port)
