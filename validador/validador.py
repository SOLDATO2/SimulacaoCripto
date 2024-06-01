#validador.py
from flask import Flask, request
import socket
import requests
import time
from datetime import datetime, timedelta

import threading





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
blacklist = {}


#mudar sistema de localizar na lista pois se remover um remetente da lista, o index dele muda
def verificar_spam_transacoes(remetente):
    global registro_qnt_transacoes
    
    
    id_ref = remetente["id_remetente"]
    print("Valor id_ref ->", id_ref)
    
    #verifica se remetente existe no registro_qnt_transacoes
    #Por padrao assume que nao 
    
    if id_ref in registro_qnt_transacoes:
        print("id_ref existe em registro_qnt_transacoes")
    else:
        #{'id_remetente': 0, 'quantia': 10, 'id_destinatario': 1, 'saldo': 1000, 'horario': '18:02:21'}
        registro_qnt_transacoes[id_ref] = {
            "transacoes": 99, # se for 101 ele é marcado como spam
            "horarioPrimeiroRegistroTransacao": relogio_atual,
            "spam": False,
            "horarioMarcadoComoSpam": None
        }

    horario_transacao = datetime.strptime(registro_qnt_transacoes[id_ref]["horarioPrimeiroRegistroTransacao"], '%H:%M:%S')
    horario_atual = datetime.strptime(relogio_atual, '%H:%M:%S')
    diferenca_tempo = (horario_atual - horario_transacao).total_seconds()






    if registro_qnt_transacoes[id_ref]["horarioMarcadoComoSpam"] != None:
        horario_ultimo_spam = datetime.strptime(registro_qnt_transacoes[id_ref]["horarioMarcadoComoSpam"], '%H:%M:%S')
        diferenca_tempo_ultimo_spam = (horario_atual - horario_ultimo_spam).total_seconds()
        if diferenca_tempo_ultimo_spam > 60:
            registro_qnt_transacoes[id_ref]["horarioMarcadoComoSpam"] = None
            registro_qnt_transacoes[id_ref]["transacoes"] = 1
            registro_qnt_transacoes[id_ref]["spam"] = False
    
    if diferenca_tempo < 60:
        registro_qnt_transacoes[id_ref]["transacoes"] += 1
    else:
        registro_qnt_transacoes[id_ref]["transacoes"] = 1
        registro_qnt_transacoes[id_ref]["horarioPrimeiroRegistroTransacao"] = remetente["horario"]
        
    if registro_qnt_transacoes[id_ref]["transacoes"] > 100:
            registro_qnt_transacoes[id_ref]["horarioMarcadoComoSpam"] = relogio_atual
            registro_qnt_transacoes[id_ref]["spam"] = True
            print("Remetente marcado como spam")
    #######################################################
    
    
    if registro_qnt_transacoes[id_ref]["spam"] == True:
        return False
    else:
        return True
    

    
    
    
    
def validar_transacao(remetente):
    
    saldo_remetente = remetente["saldo"]
    valor_transacao = remetente["quantia"]
    horario_job = remetente["horario"]

    #validar saldo + taxas
    if validar_saldo_remetente(saldo_remetente, valor_transacao) == False:
        print("saldo nao validado")
        return False
    if validar_horario_ultima_transcao(horario_job) == False:
        print("Horario nao validado")
        return False
    if verificar_spam_transacoes(remetente) == False:
        print("Remetente está marcado como spam")
        return False
    return True
    
    
       
    







    
token_verificar_transacoes = True
def verificar_transacoes_thread2():
    global blacklist, token_verificar_transacoes, token_blacklist
    while True:
        while(token_verificar_transacoes == False): #aguarda receber o token para fazer qualquer possivel modificacao em blacklist
            pass
        #for remetente in registro_qnt_transacoes:
        for remetente in list(registro_qnt_transacoes.keys()):
            if registro_qnt_transacoes[remetente]["tempoEmFila"] < 60:
                if registro_qnt_transacoes[remetente]["transacoes"] > 100:
                    registro_qnt_transacoes[remetente]["tempoEmFila"] = 0
                    print(f"Remetente '{remetente}' está sendo adicionado a blacklist")
                    #remetente_dict = {
                    #    remetente: registro_qnt_transacoes[remetente]
                    #}
                    blacklist[remetente] = registro_qnt_transacoes[remetente]
                    del registro_qnt_transacoes[remetente]
                    #break
                    continue
                registro_qnt_transacoes[remetente]["tempoEmFila"] += 1 
                print(f"remetente '{remetente}' fez {registro_qnt_transacoes[remetente]["transacoes"]} transações em {registro_qnt_transacoes[remetente]["tempoEmFila"]}")
            else:
                print(f"{registro_qnt_transacoes[remetente]} deletado da fila")
                print("ANTES***********************")
                print(registro_qnt_transacoes)
                print("***********************")
                del registro_qnt_transacoes[remetente]
                print("DEPOIS***********************")
                #break
                continue
        token_verificar_transacoes = False
        token_blacklist = True       
        time.sleep(1)
    
    
token_blacklist = False
def blacklist_thread2():
    global token_blacklist, token_verificar_transacoes
    while(True):
        while token_blacklist == False: #aguarda receber o token para fazer qualquer possivel modificacao em blacklist
            pass
        #for remetente in blacklist:
        for remetente in list(blacklist.keys()):
            if blacklist[remetente]["tempoEmFila"] < 60:
                blacklist[remetente]["tempoEmFila"] += 1
                print(f"{blacklist[remetente]["tempoEmFila"]} segundos restantes para '{remetente}' ser removido da blacklist")
            else:
                del blacklist[remetente]
                print(f"Remetente {remetente} removido da blacklist")
                #break
                continue
            
        token_blacklist= False
        token_verificar_transacoes = True
        time.sleep(1)
    

        
        
    
    
    
    




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
        relogio_atual = (datetime.now() + delta_relogio).strftime("%H:%M:%S")
        #print(relogio_atual)
        time.sleep(1)


app = Flask(__name__)
delta_relogio = timedelta()
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
            

    
    transacao_valida = validar_transacao(remetente)
    
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
    delta = timedelta(hours=horas, minutes=minutos, seconds=segundos)
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
    
    #thread_verificar_transacoes_thread = threading.Thread(target=verificar_transacoes_thread2)
    #thread_verificar_transacoes_thread.start()
    
    #thread_blacklist_thread = threading.Thread(target=blacklist_thread2)
    #thread_blacklist_thread.start()
    
    thread_enviar_dados = threading.Thread(target=enviar_dados)
    thread_enviar_dados.start()

    app.run(host='127.0.0.1', port=port)
