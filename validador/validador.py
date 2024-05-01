from flask import Flask, request, jsonify
import socket
import hashlib
import os
import requests
import json
import time
import datetime
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

def atualizar_relogio():
    global relogio_atual
    while True:
        relogio_atual = datetime.datetime.now().strftime("%H:%M:%S")
        print(relogio_atual)
        time.sleep(1)

def enviar_dados():
    global relogio_atual
    minha_rota = f'http://localhost:{port}/'  # Obtenha a porta atual do validador.py
    print("Enviando dados...")
    
    try:
        response = requests.post('http://localhost:5000/receber_informacoes', json={'rota': minha_rota, 'relogio': relogio_atual})
        if response.status_code == 200:
            print("Dados enviados com sucesso para o seletor.")
        else:
            print("Falha ao enviar dados para o seletor. Tentando novamente...")
    except requests.exceptions.RequestException as e:
        print("Erro de conexão:", e)
    time.sleep(5)

@app.route('/receber_novo_relogio', methods=['POST'])
def receber_novo_relogio():
    global relogio_atual
    data = request.json
    tempo_recebido = data.get('diferenca_relogio')
    print("Tempo recebido:", tempo_recebido)
    sinal = tempo_recebido[0]  # Obtem se eh positivo ou negativo
    tempo = tempo_recebido[1:]  # Remove o primeiro caractere (sinal)
    horas, minutos, segundos = map(int, tempo.split(':'))
    delta = datetime.timedelta(hours=horas, minutes=minutos, seconds=segundos)
    if sinal == '+':
        relogio_atual = (datetime.datetime.strptime(relogio_atual, "%H:%M:%S") + delta).strftime("%H:%M:%S")
    elif sinal == '-':
        relogio_atual = (datetime.datetime.strptime(relogio_atual, "%H:%M:%S") - delta).strftime("%H:%M:%S")
    print("Relógio atualizado:", relogio_atual)
    return "Relógio atualizado com sucesso"

if __name__ == '__main__':
    port = find_available_port()
    print(f"PORTA: {port}")

    thread_relogio = threading.Thread(target=atualizar_relogio)
    thread_relogio.start()

    enviar_dados_thread = threading.Thread(target=enviar_dados)
    enviar_dados_thread.start()
        
    app.run(host='localhost', port=port)
