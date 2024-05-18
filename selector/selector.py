import sqlite3
import random
import time
import requests
from flask import Flask, request, jsonify

def time_to_seconds(t):  # Função que converte relógio HH:MM:SS para segundos
    h, m, s = map(int, t.split(':'))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):  # Função que converte segundos para relógio HH:MM:SS
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def get_conta_by_id(conta_id):  # Função que se conecta ao banco de dados e Seleciona a conta de acordo com o ID informado
    conn = sqlite3.connect('C:\\Users\\Ale\\Desktop\\Cripto_simulation\\SimulacaoCripto-main\\Contas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contas_cripto WHERE id=?", (conta_id,))
    conta = cursor.fetchone()
    conn.close()
    return conta

def get_saldo_by_id(conta_id):
    conn = sqlite3.connect('C:\\Users\\Ale\\Desktop\\Cripto_simulation\\SimulacaoCripto-main\\Contas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT saldo FROM contas_cripto WHERE id=?", (conta_id,))
    saldo = cursor.fetchone()[0]
    conn.close()
    return saldo

def selecionar_validadores(Validador_ids):
    # Obter saldos dos IDs
    saldos = {vid: get_saldo_by_id(vid) for vid in Validador_ids}

    # Criar lista de IDs onde cada ID aparece de acordo com o saldo (probabilidade proporcional ao saldo)
    weighted_ids = []
    for vid, saldo in saldos.items():
        if saldo > 0:
            weighted_ids.extend([vid] * int(saldo))

    # Verificar se há IDs suficientes para selecionar 3
    if len(set(weighted_ids)) < 3:
        raise ValueError("Não há IDs suficientes para selecionar 3 validadores únicos")

    # Selecionar aleatoriamente 3 IDs únicos
    escolhidos = []
    while len(escolhidos) < 3:
        escolhido = random.choice(weighted_ids)
        if escolhido not in escolhidos:
            escolhidos.append(escolhido)
    
    print(f"Validadores selecionados: {escolhidos}")
    return escolhidos

def solicitar_id():  # Função que solicita o ID ao iniciar o seletor e verifica se o ID (se a conta) existe no banco de dados
    global conta_id_global
    while True:
        try:
            conta_id = int(input("Informe o ID da conta: "))
            conta = get_conta_by_id(conta_id)
            if conta:
                print(f"Conta encontrada: {conta}")
                conta_id_global = conta_id
                break
            else:
                print("ID não encontrado. Tente novamente.")
        except ValueError:
            print("ID inválido. Por favor, insira um número inteiro.")
    return conta_id

app = Flask(__name__)

# Solicita o ID do seletor ao iniciar
id_seletor = solicitar_id()

rotas = []
Validador_ids = []

@app.route('/receber_informacoes', methods=['POST'])
def receber_informacoes():
    global rotas, Validador_ids

    dados = request.json
    novo_id = dados.get('id')
    nova_rota = dados.get('rota')

    if novo_id == id_seletor:
        return jsonify({'erro': 'ID em uso pelo seletor'}), 400
    elif novo_id in Validador_ids:
        return jsonify({'erro': 'ID já em uso por outro validador'}), 400
    else:
        Validador_ids.append(novo_id)
        print(f"IDs em uso {Validador_ids}")

    if nova_rota:
        rotas.append(nova_rota)
        print(f'Rotas recebidas: {rotas}')

    if len(rotas) == 9:
        relogios = []
        for rota in rotas:
            while True:
                try:
                    response = requests.get(rota + '/obter_relogio')
                    if response.status_code == 200:
                        relogios.append(response.json().get('relogio'))
                        print(f"Relogios recebidos: {relogios}")
                        break  # Sai do loop se a solicitação for bem-sucedida
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {rota}: {e}")
                    print("Tentando novamente...")

        if relogios:
            media_seconds = sum(time_to_seconds(t) for t in relogios) / len(relogios)
            media_relogios = seconds_to_time(media_seconds)
            print(f'Média dos relógios: {media_relogios}')

            for rota, relogio in zip(rotas, relogios):
                diff_seconds = time_to_seconds(media_relogios) - time_to_seconds(relogio)
                diff_relogio = seconds_to_time(abs(diff_seconds))

                if diff_seconds >= 0:
                    diff_relogio = '+' + diff_relogio
                else:
                    diff_relogio = '-' + diff_relogio

                try:
                    response = requests.post(rota + '/receber_novo_relogio', json={'diferenca_relogio': diff_relogio})
                    if response.status_code == 200:
                        print(f'Diferença de relógio enviada para {rota}')
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {rota}: {e}")

        # Selecionar os validadores após sincronização dos relógios
        selecionar_validadores(Validador_ids)

        rotas.clear()
        Validador_ids = [id_seletor]
        print("Rotas e IDs limpos")

    return "Dados recebidos com sucesso", 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

    #a