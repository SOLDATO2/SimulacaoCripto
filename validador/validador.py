# validador.py

from flask import Flask, request, jsonify
import socket
import hashlib
import os
import requests
import json
import time

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

def enviar_dados():
    minha_rota = f'http://localhost:{port}/'  # Obtenha a porta atual do validador.py
    relogio = time.strftime("%H:%M:%S")  # Obtém o horário atual

    try:
        response = requests.post('http://localhost:5000/receber_informacoes', json={'rota': minha_rota, 'relogio': relogio})
        if response.status_code == 200:
            print("Dados enviados com sucesso para o seletor.")
            return True
        else:
            print("Falha ao enviar dados para o seletor. Tentando novamente...")
            return False
    except requests.exceptions.RequestException as e:
        print("Erro de conexão:", e)
        return False

if __name__ == '__main__':
    port = find_available_port()
    print(f"Using port: {port}")

    while not enviar_dados():
        time.sleep(5)  # Espera 5 segundos antes de tentar novamente

    app.run(host='localhost', port=port)
