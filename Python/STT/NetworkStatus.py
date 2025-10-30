import socket

def check_server_connectivity(host="HOST_ADDRESS", port = 80, timeout = 3):
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False