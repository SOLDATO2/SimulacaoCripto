import threading
from flask import Flask, request
import json
import time
import socket

def find_available_port():
    """Encontra uma porta disponível."""
    port = 5001  # Porta inicial
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            return port
        except OSError:
            port += 1
        finally:
            sock.close()

app = Flask(__name__)
@app.route('/receive_json', methods=['POST'])
def receive_json():
    if request.json:
        json_data = request.json
        print("JSON received:", json_data)
        return "JSON received successfully"
    
    return "Time exceeded"

if __name__ == '__main__':
    port = find_available_port()
    print(f"Using port: {port}")
    app.run(host='localhost', port=port)
    