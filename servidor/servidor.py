import datetime
import os
import threading
import time
from flask import Flask, request
import requests
import pprint
app = Flask(__name__)
delta_relogio = datetime.timedelta()
relogio_atual = ""   

def atualizar_relogio(): 
    global relogio_atual, delta_relogio
    while True:
        relogio_atual = (datetime.datetime.now() + delta_relogio).strftime("%H:%M:%S")
        print(relogio_atual)
        time.sleep(1)
        
def esperando_job(job):
    while True:
        if job != None:
            response = requests.post('http://127.0.0.1:5001/receber_job', json=job)
            try:
                if response.status_code == 200:
                    print("Dados enviados com sucesso para o seletor.")
                    break
                else:
                    print(f"Falha ao enviar dados para o seletor: {response.json().get('erro')}")
            except requests.exceptions.RequestException as e:
                print("Erro de conexão:", e)
                time.sleep(2)

#ainda nao esta sendo utilizado
@app.route('/obter_relogio', methods=['GET'])
def obter_relogio():
    global relogio_atual
    return {'relogio': relogio_atual}

job = None
@app.route('/receber_informacoes_banco', methods=['POST'])
def receber_informacoes_banco():
    global job
    data = request.json
    job = data
    job["horario"] = relogio_atual
    print("Informacoes recebidas")
    esperando_job(job)
    return "Informacoes recebidas"


fila_logs = []
@app.route('/receber_log', methods=['POST'])
def receber_log():
    global fila_logs
    dados = request.json
    
    novo_evento_hora = dados.get('hora')
    novo_evento_log = dados.get('log')
    
    pprint.pprint(novo_evento_hora)
    pprint.pprint(novo_evento_log)
    
    fila_logs.append(dados)
    
    return "Novo log"
    
    


def log_manager_thread():
    global fila_logs
    while True:
        if len(fila_logs) > 0:
            for log in fila_logs:
                if os.path.exists("logs.txt"):
                    with open("logs.txt", 'r+') as arquivo:
                        linhas = arquivo.readlines()
                        encontrou_linha_vazia = False
                    
                        for i, linha in enumerate(linhas):
                            if linha.strip() == '':
                                linhas[i] = f"[{log['hora']}]: {log['log']}\n"
                                encontrou_linha_vazia = True
                                break
                        
                        if encontrou_linha_vazia:
                            arquivo.seek(0)
                            arquivo.writelines(linhas)
                        else:
                            arquivo.write(f"[{log['hora']}]: {log['log']}\n")
                else:
                    with open("logs.txt", 'w') as arquivo:
                        arquivo.write(f"[{log['hora']}]: {log['log']}\n")
                fila_logs.remove(log)

                











if __name__ == '__main__':
    
    thread_relogio = threading.Thread(target=atualizar_relogio)
    thread_relogio.start()
    
    thread_log_manager_thread = threading.Thread(target=log_manager_thread)
    thread_log_manager_thread.start()
    
    app.run(host='127.0.0.1', port=5000)