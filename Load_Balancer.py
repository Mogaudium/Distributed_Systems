import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

BACKEND_SERVERS = ['127.0.0.1:5000', '127.0.0.1:5001' , '127.0.0.1:5002']  # Flask instances
current_server = 0

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def forward_request(self):
        global current_server

        # Choose the next server for load balancing (Round Robin)
        server_address = BACKEND_SERVERS[current_server]
        current_server = (current_server + 1) % len(BACKEND_SERVERS)
        backend_ip, backend_port = server_address.split(':')
        backend_port = int(backend_port)

        # Connect to the chosen backend server (Flask instance)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((backend_ip, backend_port))
        sock.sendall(self.raw_requestline)

        # Forward data
        for key, value in self.headers.items():
            sock.sendall(f"{key}: {value}\r\n".encode())
        sock.sendall(b'\r\n')

        # Forward the request body if present (for POST requests)
        content_length = self.headers.get('Content-Length')
        if content_length:
            content_length = int(content_length)
            body = self.rfile.read(content_length)
            sock.sendall(body)

        # Send the response back to the client
        while True:
            backend_data = sock.recv(4096)
            if not backend_data:
                break
            self.wfile.write(backend_data)

        sock.close()

    def do_GET(self):
        self.forward_request()

    def do_POST(self):
        self.forward_request()

if __name__ == '__main__':
    load_balancer_address = ('', 8000)  # Load balancer's address
    httpd = HTTPServer(load_balancer_address, ProxyHTTPRequestHandler)
    print(f"Starting load balancer on {load_balancer_address[0]}:{load_balancer_address[1]}")
    httpd.serve_forever()
