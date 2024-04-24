# validador.py

from flask import Flask, request, jsonify
import socket
import hashlib
import os
import requests
import json
import time

import threading

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
    print(relogio)

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

@app.route('/receber_novo_relogio', methods=['POST'])
def receber_novo_relogio():
    data = request.json
    diferenca_relogio = data.get('diferenca_relogio')
    print("Diferença de relógio recebida:", diferenca_relogio)
    return "Relógio recebido com sucesso"

if __name__ == '__main__':
    port = find_available_port()
    print(f"Using port: {port}")

    enviar_dados_thread = threading.Thread(target=enviar_dados) #usa multi threading para executar 2 funces ao mesmo tempo
    enviar_dados_thread.start()
        
    app.run(host='localhost', port=port)
