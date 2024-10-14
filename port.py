import socket

def check_port(ip, port):
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)  # Set a timeout of 5 seconds

    try:
        # Try to connect to the specified IP and port
        s.connect((ip, port))
        s.close()
        return True
    except (socket.timeout, socket.error):
        return False

# Test the function
ip_address = '8.8.8.8'  # Replace with the target IP address
port = 53  # Replace with the target port

if check_port(ip_address, port):
    print(f"Port {port} on {ip_address} is open.")
else:
    print(f"Port {port} on {ip_address} is closed or unreachable.")
