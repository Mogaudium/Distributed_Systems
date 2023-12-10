import subprocess
import os

# Define a function to start microservices
def start_service(service_name, port):
    subprocess.Popen(["python", service_name, str(port)], start_new_session=True)

if __name__ == "__main__":
    # Define microservices and their respective ports
    services = {
        "Registration_Service.py": 5003,
        "Login_Service.py": 5004,
        "Audio_List_Service.py": 5010,
        "Audio_Stream_Service.py": 5020
    }

    # Start each microservice
    for service, port in services.items():
        start_service(service, port)
        print(f"Started {service} on port {port}")

    print("All microservices have been started.")
