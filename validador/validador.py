#validador.py
from flask import Flask, request
import socket
import requests
import time
import datetime
import threading
import sqlite3

def find_available_port(): # ACHA UMA PORTA DISPONÍVEL PARA O VALIDADOR
    port = 5001  # Porta inicial
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            return port
        except OSError:
            port += 1
        finally:
            sock.close()

def get_conta_by_id(conta_id): # Função que se conecta ao banco de dados e Seleciona a conta de acordo com o ID informado
    conn = sqlite3.connect('C:\\Users\\Ale\\Desktop\\Cripto_simulation\\SimulacaoCripto-main\\Contas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas_cripto WHERE id=?", (conta_id,))
    conta = cursor.fetchone()
    conn.close()
    return conta

def solicitar_id(): # Função que solicita o ID ao iniciar o validador
    while True:
        try:
            conta_id = int(input("Informe o ID da conta: "))
            conta = get_conta_by_id(conta_id)
            if conta:
                print(f"Conta encontrada: {conta}")
                return conta_id
            else:
                print("ID não encontrado. Tente novamente.")
        except ValueError:
            print("ID inválido. Por favor, insira um número inteiro.")

app = Flask(__name__)

delta_relogio = datetime.timedelta()
relogio_atual = ""

def atualizar_relogio(): # Função para o relógio ficar contando a cada segundo (passando o tempo no terminal)
    global relogio_atual, delta_relogio
    while True:
        relogio_atual = (datetime.datetime.now() + delta_relogio).strftime("%H:%M:%S")
        print(relogio_atual)
        time.sleep(1)

def enviar_dados():
    global conta_id
    minha_rota = f'http://127.0.0.1:{port}/'  # Define a rota do validador (Talvez esteja acontecendo algum problema ao definir rota)
    print("Enviando dados...")

    while True:
        try:
            response = requests.post('http://127.0.0.1:5000/receber_informacoes', json={'id': conta_id, 'rota': minha_rota})
            if response.status_code == 200:
                print("Dados enviados com sucesso para o seletor.")
                break
            else:
                print(f"Falha ao enviar dados para o seletor: {response.json().get('erro')}")
                conta_id = solicitar_id()  # Solicita um novo ID
        except requests.exceptions.RequestException as e:
            print("Erro de conexão:", e)
        time.sleep(2)  # Ajustar o tempo de espera conforme necessário

@app.route('/obter_relogio', methods=['GET'])
def obter_relogio():
    global relogio_atual
    return {'relogio': relogio_atual}

@app.route('/receber_novo_relogio', methods=['POST']) # Rota que faz o ajuste de tempo de acordo com o necessário
def receber_novo_relogio():
    global relogio_atual, delta_relogio
    data = request.json
    tempo_recebido = data.get('diferenca_relogio')
    print("Tempo recebido:", tempo_recebido)
    sinal = tempo_recebido[0]
    tempo = tempo_recebido[1:]
    horas, minutos, segundos = map(int, tempo.split(':'))
    delta = datetime.timedelta(hours=horas, minutes=minutos, seconds=segundos)
    if sinal == '+':
        delta_relogio += delta
    elif sinal == '-':
        delta_relogio -= delta
    print("Relógio atualizado")
    return "Relógio atualizado com sucesso"

if __name__ == '__main__':
    conta_id = solicitar_id()
    port = find_available_port()
    print(f"PORTA: {port}")
    #INICIAR O SERVIOD FLASK
    # Envia os dados para o seletor e só continua se o ID for aceito
    
    thread_enviar_dados = threading.Thread(target=enviar_dados)
    thread_enviar_dados.start()

    # Inicia a thread do relógio apenas após a aceitação do ID
    thread_relogio = threading.Thread(target=atualizar_relogio)
    thread_relogio.start()

    app.run(host='127.0.0.1', port=port)

    #a