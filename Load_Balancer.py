import socket  
from http.server import BaseHTTPRequestHandler, HTTPServer  

# List of backend servers (Flask instances) with their IP addresses and ports
BACKEND_SERVERS = ['192.168.1.6:5000', '192.168.1.6:5001' , '192.168.1.6:5002']
current_server = 0  # Index to keep track of the current server for load balancing

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    # Handler class to forward HTTP requests to backend servers
    def forward_request(self):
        global current_server  

        # Round Robin Load Balancing: Choose the next server to forward the request to
        server_address = BACKEND_SERVERS[current_server]
        current_server = (current_server + 1) % len(BACKEND_SERVERS)
        backend_ip, backend_port = server_address.split(':')  # Split the server address into IP and port
        backend_port = int(backend_port)  # Convert the port to an integer

        # Create a socket and connect to the chosen backend server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((backend_ip, backend_port))
        sock.sendall(self.raw_requestline)  # Send the initial request line (e.g., "GET / HTTP/1.1")

        # Forward all headers received from the client to the backend server
        for key, value in self.headers.items():
            sock.sendall(f"{key}: {value}\r\n".encode())
        sock.sendall(b'\r\n')  # Send a blank line to indicate the end of headers

        # If there's a request body (e.g., in a POST request), forward it to the backend server
        content_length = self.headers.get('Content-Length')
        if content_length:
            content_length = int(content_length)
            body = self.rfile.read(content_length)
            sock.sendall(body)

        # Receive the response from the backend server and forward it back to the client
        while True:
            backend_data = sock.recv(4096)
            if not backend_data:
                break
            self.wfile.write(backend_data)

        sock.close()  # Close the socket after forwarding the response

    def do_GET(self):
        self.forward_request()  # Forward GET requests

    def do_POST(self):
        self.forward_request()  # Forward POST requests

if __name__ == '__main__':
    # Set up the load balancer's HTTP server
    load_balancer_address = ('192.168.1.6', 8000)  # Load balancer's IP address and port
    httpd = HTTPServer(load_balancer_address, ProxyHTTPRequestHandler)
    print(f"Starting load balancer on {load_balancer_address[0]}:{load_balancer_address[1]}")
    httpd.serve_forever()  # Start the server and handle requests indefinitely
