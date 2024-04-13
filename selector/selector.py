# selector.py

from flask import Flask, request, jsonify
import asyncio
import socket
import hashlib
import os
import requests
import json

rotas = []
relogios = []

app = Flask(__name__)

@app.route('/receber_informacoes', methods=['GET', 'POST'])
def receber_informacoes():
    if request.method == 'POST':
        dados = request.json
        nova_rota = dados.get('rota')
        novo_relogio = dados.get('relogio')

        if nova_rota:
            rotas.append(nova_rota)
            print(f'Rotas recebida: {rotas}')
        if novo_relogio:
            relogios.append(novo_relogio)
            print(f'Relógios recebidos: {relogios}')
            
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
