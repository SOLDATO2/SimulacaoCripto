# selector.py

from flask import Flask, request, jsonify
import socket
import hashlib
import os
import requests
import json
import time

rotas = []
relogios = []

app = Flask(__name__)

@app.route('/receber_informacoes', methods=['GET', 'POST'])
def receber_informacoes():
    global rotas, relogios

    if request.method == 'POST':
        dados = request.json
        nova_rota = dados.get('rota')
        novo_relogio = dados.get('relogio')

        if nova_rota:
            rotas.append(nova_rota)
            print(f'Rotas recebidas: {rotas}')
            print(f'Relogios recebidos: {relogios}')
        if novo_relogio:
            relogios.append(time.strptime(novo_relogio, "%H:%M:%S"))

        # Se recebemos 3 rotas e 3 relógios, calculamos a média dos relógios
        if len(rotas) == 3 and len(relogios) == 3:
            total_seconds = sum(map(lambda t: t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec, relogios))
            media_relogios = time.strftime("%H:%M:%S", time.gmtime(total_seconds / 3))
            print(f'Média dos relógios: {media_relogios}')

            # Enviar o novo relógio para cada rota
            for rota in rotas:
                response = requests.post(rota + '/receber_novo_relogio', json={'novo_relogio': media_relogios})
                if response.status_code == 200:
                    print(f'Novo relógio enviado para {rota}')

            # Limpar as listas para receber novos dados
            rotas.clear()
            relogios.clear()

        return "Dados recebidos com sucesso"

    if len(rotas) == 0 and len(relogios) == 0:
        print("Aguardando dados...")
        return "Aguardando dados..."
    else:
        print("Rotas recebidas:", rotas)
        print("Relógios recebidos:", relogios)
        return jsonify({"rotas": rotas, "relogios": relogios})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
