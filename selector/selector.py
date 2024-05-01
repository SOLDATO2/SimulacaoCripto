# selector.py

from flask import Flask, request, jsonify
import socket
import hashlib
import os
import requests
import json
import time


# Lembrar de substituir esses 2 por um json
# que irá armazenar essas 2 informações
rotas = []
relogios = []

app = Flask(__name__)

@app.route('/receber_informacoes', methods=['GET', 'POST'])
def receber_informacoes():
    #global rotas, relogios

    if request.method == 'POST':
        dados = request.json
        nova_rota = dados.get('rota')
        novo_relogio = dados.get('relogio')

        if nova_rota:
            rotas.append(nova_rota)
            print(f'Rotas recebidas: {rotas}')
            
        if novo_relogio:
            relogios.append(novo_relogio)
            print(f'Relogios recebidos: {relogios}')

        # Se recebemos 3 rotas e 3 relógios, calculamos a média dos relógios
        if len(rotas) == 3 and len(relogios) == 3:
            media_seconds = sum(map(lambda t: sum(int(i) * (60 ** index) for index, i in enumerate(reversed(t.split(':')))), relogios)) / len(relogios)
            media_relogios = time.strftime("%H:%M:%S", time.gmtime(media_seconds))
            print(f'Média dos relógios: {media_relogios}')

            # Enviar o novo relógio para cada rota
            for rota, relogio in zip(rotas, relogios):
                diff_seconds = sum(map(lambda t: sum(int(i) * (60 ** index) for index, i in enumerate(reversed(t.split(':')))), [media_relogios])) - sum(map(lambda t: sum(int(i) * (60 ** index) for index, i in enumerate(reversed(t.split(':')))), [relogio]))
                diff_relogio = time.strftime("%H:%M:%S", time.gmtime(abs(diff_seconds)))  # Use abs() para obter o valor absoluto da diferença

                # Determine se o relógio está adiantado ou atrasado em relação à média
                if diff_seconds >= 0:
                    diff_relogio = '+' + diff_relogio  # Se positivo, o relógio está atrasado
                else:
                    diff_relogio = '-' + diff_relogio  # Se negativo, o relógio está adiantado

                response = requests.post(rota + '/receber_novo_relogio', json={'diferenca_relogio': diff_relogio})
                if response.status_code == 200:
                    print(f'Diferença de relógio enviada para {rota}')

            # Limpar as listas para receber novos dados
            rotas.clear()
            print("Rotas limpas")
            relogios.clear()
            print("Relogios limpos")

        return "Dados recebidos com sucesso"

    if len(rotas) == 3 and len(relogios) == 3:
        print("Aguardando dados...")
        return "Aguardando dados..."
    else:
        print("Rotas recebidas:", rotas)
        print("Relógios recebidos:", relogios)
        return jsonify({"rotas": rotas, "relogios": relogios})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
