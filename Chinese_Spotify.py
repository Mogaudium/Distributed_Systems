import subprocess
import sys

def run_script(script_name):
    subprocess.Popen([sys.executable, script_name])

if __name__ == "__main__":
    # Scripts to be started
    scripts = ["Run_Servers.py", "Run_Microservices.py", "Load_Balancer.py"]

    # Start each script in a separate process
    for script in scripts:
        run_script(script)
        print(f"Started {script}")

    print("Chinese Spotify setup is complete.")
