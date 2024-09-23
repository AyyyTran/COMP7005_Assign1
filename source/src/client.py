import socket
import argparse
import os
import sys

buffer_size = 1024

def validate_socket_path(socket_path):
    if not isinstance(socket_path, str) or not socket_path.startswith('/'):
        print(f"Error: '{socket_path}' is not a valid socket path. It must start with '/'.")
        sys.exit(1)

def create_client_socket(socket_path):
        validate_socket_path(socket_path)
        try:    
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.connect(socket_path)
            print("Connected to the server.")
            return client_socket
        except socket.error as e:
            print(f"Error: Could not connect to socket at '{socket_path}'. Please ensure the server is running and the socket path is correct.")
            sys.exit(1)

def send_file_path(client_socket, file_path):
    try:
        client_socket.sendall(file_path.encode())
    except socket.error as e:
        print(f"Error: Failed to send file path '{file_path}'.")
        sys.exit(1)

def receive_response(client_socket):
    try:
        response = client_socket.recv(buffer_size).decode()
        print('Server response:', response)
    except socket.error as e:
        print("Error: Failed to receive response from the server.")
        sys.exit(1)

def cleanup_client(client_socket):
    client_socket.close()

def start_client(socket_path, file_path):
    client_socket = create_client_socket(socket_path)
    try:
        send_file_path(client_socket, file_path)
        receive_response(client_socket)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        cleanup_client(client_socket)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send a file path to a UNIX domain socket server.')
    parser.add_argument('-s', '--socket', type=str, required=True, help='Socket Path')
    parser.add_argument('-f', '--file', type=str, required=True, help='File Path')
    args = parser.parse_args()

    if not os.path.exists(args.socket):
        print(f"Error: Socket path '{args.socket}' does not exist. Please provide a valid socket path.")
        sys.exit(1)

    if not isinstance(args.file, str):
        print("Error: The file path must be a valid string.")
        sys.exit(1)

    start_client(args.socket, args.file)
