#validador.py
from flask import Flask, request
import socket
import requests
import time
import datetime
import threading
import asyncio





#Status da Transação (Servem da camada “Validador” para a camada “Seletor”, assim como da
# camada “Seletor” para a camada “Banco”):
# o 1 = Concluída com Sucesso
# o 2 = Não aprovada (erro)
# o 0 = Não executada


status_aprovacao = 0



#O horário da transação deve ser menor ou igual ao horário atual do sistema e deve ser maior que
# o horário da última transação para ser válida

horario_ultima_transacao = "None"
def validar_horario_ultima_transcao(horario_transacao_atual):
    global relogio_atual
    global horario_ultima_transacao
    temp = horario_ultima_transacao
    print("Horario transação atual->",horario_transacao_atual)
    #if horario_ultima_transacao == None:
    #    horario_ultima_transacao = relogio_atual
    print("relogio atual", relogio_atual)
    if (horario_transacao_atual <= relogio_atual):
        print("relogio transacao atual é menor ou igual ao relogio atual")
        if (horario_transacao_atual > horario_ultima_transacao) or (horario_ultima_transacao == "None"):
            if (horario_ultima_transacao == "None"):
                print("Horario da ultima transacao é nulo, portanto o relógio da ultima trasação será o da transação atual")
            else:
                print("relogio transacao atual é maior do que o relogio atual")
            horario_ultima_transacao = horario_transacao_atual
            print("Horario validado")
            return True
    else:
        horario_ultima_transacao = temp
        print("Horario não validado")
        return False
    
#O remetente deve ter um valor em saldo igual ou maior que o valor da transação, acrescido das
# taxas para a mesma ser válida    

def validar_saldo_remetente(saldo_remetente, valor_transacao):
    
    saldo_mais_taxas = valor_transacao + (valor_transacao*0.015)
    
    if saldo_mais_taxas > saldo_remetente:
        print("Saldo não validado")
        return False
    else:
        print("Saldo validado")
        return True

#Caso o remetente tenha feito mais que 100 transações no último minuto, as transações no
# próximo minuto devem ser invalidas

registro_qnt_transacoes = {}#armazenar jsons dentro de jsons do remetente
blacklist = []

id_ref = ""
#mudar sistema de localizar na lista pois se remover um remetente da lista, o index dele muda
def verificar_spam_transacoes(remetente):
    
    global registro_qnt_transacoes
    global id_ref
    
    
    id_ref = remetente["id_remetente"]
    print("Valor id_ref ->", id_ref)
    
    #verifica se remetente existe no registro_qnt_transacoes
    #Por padrao assume que nao 
    id_remetente_in_remetentes = False
    
    if id_ref in registro_qnt_transacoes:
        id_remetente_in_remetentes = True
        print(f"id {id_ref} existe na fila")
        
    
    if id_remetente_in_remetentes == False:

        #{'id_remetente': 0, 'quantia': 10, 'id_destinatario': 1, 'saldo': 1000, 'horario': '18:02:21'}
        
        registro_qnt_transacoes[id_ref] = {
            "spam": False,
            "transacoes": 100 # se for 101 ele é adicionado a blacklist
        }
        if id_ref not in blacklist:
            _thread_verificar_transacoes_thread = threading.Thread(target=verificar_transacoes_thread, args= str(id_ref))
            _thread_verificar_transacoes_thread.start()
            print("thread iniciado")
    else:
        registro_qnt_transacoes[id_ref]["transacoes"] += 1 


def verificar_transacoes_thread(id_ref):
    global blacklist
    mini_relogio = 0
    while(mini_relogio != 60):
        if registro_qnt_transacoes[id_ref]["transacoes"] > 100:
            if registro_qnt_transacoes[id_ref] not in blacklist:
                blacklist.append(id_ref)
                thread_blacklist_thread = threading.Thread(target=blacklist_thread, args = id_ref)
                thread_blacklist_thread.start()
            break
        else:
            print(f"remetente '{id_ref}' fez {registro_qnt_transacoes[id_ref]["transacoes"]} transações em {mini_relogio}")
            
        mini_relogio += 1
        time.sleep(1)
    del registro_qnt_transacoes[id_ref]
    print(f"remetente '{id_ref}' removido da lista de transações")
    
def blacklist_thread(id_ref):
    print(f"Remetente '{id_ref}' está sendo adicionado a blacklist")
    mini_relogio = 0
    while(mini_relogio != 60):
        time.sleep(1)
        mini_relogio +=1
        print(f"{mini_relogio} segundos restantes para '{id_ref}' ser removido da blacklist")
    blacklist.remove(id_ref)
        
        
    
    
    
    




def find_available_port(): # ACHA UMA PORTA DISPONÍVEL PARA O VALIDADOR
    port = 5002  # Porta inicial
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            return port
        except OSError:
            port += 1
        finally:
            sock.close()

def definir_id():
    global id_validador
    id_validador = input("Digite o seu Id registrado no seletor, caso não tenha, digite 'None': ")



def atualizar_relogio(): # Função para o relógio ficar contando a cada segundo (passando o tempo no terminal)
    global relogio_atual, delta_relogio
    while True:
        relogio_atual = (datetime.datetime.now() + delta_relogio).strftime("%H:%M:%S")
        #print(relogio_atual)
        time.sleep(1)


app = Flask(__name__)
delta_relogio = datetime.timedelta()
relogio_atual = "sem relogio"        

def enviar_status_aprovacao(id_validador, status_aprovacao):
    while True:
        try:
            response = requests.post('http://127.0.0.1:5001/receber_status_aprovacao', json={'id_validador': id_validador, 'status_aprovacao': status_aprovacao})
            if response.status_code == 200:
                print("Dados enviados com sucesso para o seletor.")
                break
            else:
                print(f"Falha ao enviar dados para o seletor: {response.json().get('erro')}")
        except requests.exceptions.RequestException as e:
            print("Erro de conexão:", e)
        time.sleep(2)  # Ajustar o tempo de espera conforme necessário
    

@app.route('/validar_job', methods=['POST'])
def validar_job():
    global status_aprovacao
    #assume que é false e ao decorrer das verificações pode ficar true
    transacao_valida = False
    
    data = request.json
    
    
    remetente = data
            

    
    saldo_remetente = remetente["saldo"]
    valor_transacao = remetente["quantia"]
    horario_job = remetente["horario"]
    
    

    print("ate aqui funciona 1")
    
    transacao_valida = validar_saldo_remetente(saldo_remetente,valor_transacao)
    print("ate aqui funciona 2")
    
    print("Resposta validar_saldo_remetente:", transacao_valida)
    if transacao_valida == True:
        transacao_valida = validar_horario_ultima_transcao(horario_job)
        print("Resposta validar_horario_ultima_transcao:", transacao_valida)
        if transacao_valida == True:
            #verifica se o remetente é spam
            verificar_spam_transacoes(remetente)
            
            print("Print executado antes de verificar se é spam->",registro_qnt_transacoes)

            #sleep necessario pois caso o remetente tenha 100 transações e esse seja a transação 101
            #Ao iniciar o thread verificar_spam_transacoes, ele continua executando a proxima linha, o que não permite com que 
            #de tempo do id ser adicionado a blacklist, retornando um codigo de resposta "1" ao inves de "2"
            #time.sleep está forçando o sistema a esperar os threads estarem em dia. Provavelmente tem uma forma melhor de fazer isso
            #ver depois
            time.sleep(1)
            if remetente["id_remetente"] in blacklist:
                transacao_valida = False
    
    
    if transacao_valida == True:
        status_aprovacao = 1
    else:
        status_aprovacao = 2
    
    #envia resposta da aprovacao para selector
    enviar_status_aprovacao(id_validador, status_aprovacao)
    status = status_aprovacao
    print("Status job", status)
    
    
    #resetar variaveis após validar job
    status_aprovacao = 0
    
    
    #envia os dados novamente para entrar na fila para validar outra job
    #podia ser feito um sistema para primeiro receber uma confirmação do selector que informa que ele recebeu a resposta do validador em questão
    #porem eu acho que ele funciona dessa forma do mesmo jeito
    enviar_dados()
    
    
    
    return str(status)
    
    
    
    

@app.route('/receber_id', methods=['POST'])
def receber_id():
    global id_validador

    data = request.json
    id_validador = data.get('id_gerado')
    print("fiz ate onde eu queria")
    print(id_validador)
    return "fiz ate onde eu queria"
    

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


def enviar_dados():

    minha_rota = f'http://127.0.0.1:{port}/'  #Define a rota do validador 
    print("Enviando dados...")

    while True:
        try:
            response = requests.post('http://127.0.0.1:5001/receber_informacoes_validadores', json={'rota': minha_rota, 'id_validador': id_validador})
            if response.status_code == 200:
                print("Dados enviados com sucesso para o seletor.")
                break
            else:
                print(f"Falha ao enviar dados para o seletor: {response.json().get('erro')}")
        except requests.exceptions.RequestException as e:
            print("Erro de conexão:", e)
        time.sleep(2)  # Ajustar o tempo de espera conforme necessário

    
    
    
if __name__ == '__main__':
    thread_relogio = threading.Thread(target=atualizar_relogio)
    thread_relogio.start()
    
    port = find_available_port()
    print(f"PORTA: {port}")
    
    definir_id()
    
    
    thread_enviar_dados = threading.Thread(target=enviar_dados)
    thread_enviar_dados.start()

    app.run(host='127.0.0.1', port=port)
