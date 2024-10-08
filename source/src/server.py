import socket
import os
import threading

BUFFER_SIZE = 4096  # Same buffer size as client

# ---- Utility Functions ----

def count_alphabetic_chars(file_data):
    """Count the number of alphabetic characters in the file data."""
    return sum(c.isalpha() for c in file_data)

def get_local_ip():
    """Retrieve the local IP address of the server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error retrieving local IP address: {e}")
        return "Unable to retrieve local IP."

# ---- Core Server Logic ----

def create_server_socket(port):
    """Create and return a TCP server socket."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Enable address reuse
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)  # Allow up to 5 clients to queue
    print(f"Server is listening on port {port}...")
    return server_socket

def accept_client_connection(server_socket):
    """Accept a client connection."""
    client_socket, client_address = server_socket.accept()
    print(f"Client connected from {client_address}.")
    return client_socket

def receive_file_from_client(client_socket):
    """Receive file data sent by the client."""
    file_data = b""  # Accumulate file data here
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:  # No more data from the client, end of file transfer
            print("No more data from client, file transfer complete.")
            break
        file_data += data  # Append received data
        print(f"Received {len(data)} bytes from client.")  # Debugging line
    print("File data received successfully.")  # Debugging line
    return file_data

def send_response_to_client(client_socket, response):
    """Send response back to the client."""
    print(f"Sending response to client: {response}")  # Debugging line
    client_socket.sendall(response.encode())

def handle_client(client_socket):
    """Handle the communication with a single client."""
    try:
        # Receive the file content from the client
        file_data = receive_file_from_client(client_socket)

        # Try to decode the file data to string
        try:
            file_text = file_data.decode()  # Debugging line to check for errors in decoding
            print("File data decoded successfully.")  # Debugging line
        except UnicodeDecodeError as e:
            print(f"Error decoding file data: {e}")
            client_socket.close()
            return

        # Count the number of alphabetic characters
        letter_count = count_alphabetic_chars(file_text)
        print(f'Counted {letter_count} alphabetic characters in the received file.')

        # Send the letter count back to the client
        response = f"Alphabetic character count: {letter_count}"
        send_response_to_client(client_socket, response)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print("Client connection closed.")

# ---- Server Control Flow ----

def start_server(port):
    """Start the server and handle client requests."""
    local_ip = get_local_ip()
    print(f"Server IP address: {local_ip}")

    server_socket = create_server_socket(port)
    try:
        while True:
            client_socket = accept_client_connection(server_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

# ---- Entry Point with Argument Parsing ----

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='TCP server for receiving and processing file content.')
    parser.add_argument('--port', type=int, required=True, help='Port number for the server to listen on')

    args = parser.parse_args()
    start_server(args.port)
