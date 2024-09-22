import socket
import os
import argparse
import sys

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"Error: {message}\n")
        self.print_help()
        sys.exit(2)

def validate_socket_path(socket_path):
    if not isinstance(socket_path, str) or not socket_path.startswith('/'):
        print(f"Error: '{socket_path}' is not a valid socket path. It must start with '/'.")
        sys.exit(1)

def create_server_socket(socket_path):
    validate_socket_path(socket_path)
    if os.path.exists(socket_path):
        os.remove(socket_path)
    try:
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(socket_path)
        server_socket.listen(1)
        print('Server is listening...')
        return server_socket
    except OSError as e:
        print(f"Error creating socket: {e}")
        sys.exit(1)

def accept_client_connection(server_socket):
    try:
        client_socket, _ = server_socket.accept()
        print('Client connected.')
        return client_socket
    except Exception as e:
        print(f"Error accepting client connection: {e}")

def handle_client_request(client_socket):
    try:
        file_path = client_socket.recv(1024).decode()
        print(f'Received file path: {file_path}')
        if os.path.isfile(file_path):
            response = "File exists."
        else:
            response = "File does not exist."
        client_socket.sendall(response.encode())
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print('Client connection closed.')

def cleanup_server(server_socket, socket_path):
    try:
        server_socket.close()
        if os.path.exists(socket_path):
            os.remove(socket_path)
    except Exception as e:
        print(f"Error during cleanup: {e}")

def start_server(socket_path):
    server_socket = create_server_socket(socket_path)
    try:
        while True:
            client_socket = accept_client_connection(server_socket)
            handle_client_request(client_socket)
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        cleanup_server(server_socket, socket_path)

if __name__ == "__main__":
    parser = CustomArgumentParser()
    parser.add_argument('-s', '--socket', type=str, required=True, help='Socket Path')

    args = parser.parse_args()

    start_server(args.socket)
