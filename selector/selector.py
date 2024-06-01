import datetime
import random
import threading
import time
import requests
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

def time_to_seconds(t):  
    h, m, s = map(int, t.split(':'))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def get_saldo_by_id(conta_id):
    saldo = banco[conta_id]["saldo"]
    return saldo

def selecionar_validadores(Validadores):
    
    lista_validadores = Validadores
    
    
    lista_ids = [validador["id_validador"] for validador in lista_validadores]
    # Obter saldos dos IDs
    saldos = {vid: get_saldo_by_id(vid) for vid in lista_ids}

    print(saldos)
    # Criar lista de IDs onde cada ID aparece de acordo com o saldo (probabilidade proporcional ao saldo)
    weighted_ids = []
    for vid, saldo in saldos.items():
        if saldo == 0:
            weighted_ids.extend([vid] * int(1))
        elif saldo > 0:
            weighted_ids.extend([vid] * int(saldo))
            
    


    # Selecionar aleatoriamente 3 IDs únicos
    escolhidos = []
    while len(escolhidos) < 3: ############# NAO MUDAR
        escolhido = random.choice(weighted_ids)
        if escolhido not in escolhidos:
            escolhidos.append(escolhido)
    
    print(f"Validadores selecionados: {escolhidos}")
    
    
    
    print("Dentro da funcao selecionar validador, foram escolhidos os validadores: ", escolhidos)
    
    escolhidos_final = []
    
    for id in escolhidos:
        for validador in lista_validadores:
            if id == validador["id_validador"]:
                json = {
                    "id_validador": validador["id_validador"],
                    "rota": validador["rota"]
                }
                escolhidos_final.append(json)
                
    
    
                

            
    
    return escolhidos_final


def enviar_log_banco(info):
    while True:
            try:
                response = requests.post('http://127.0.0.1:5000/receber_log', json={'hora': relogio_atual, 'log': info})
                if response.status_code == 200:
                    print("Dados enviados com sucesso para o seletor.")
                    break
                else:
                    print(f"Falha ao enviar dados para o seletor: {response.json().get('erro')}")
            except requests.exceptions.RequestException as e:
                print("Erro de conexão:", e)
            time.sleep(2)  # Ajustar o tempo de espera conforme necessário
    
    

def reset_variaveis():
    global job
    global aceitado_validadores
    global lista_validador_status_aprovacao
    global ids_validadores_selecionados
    global min_qnt_validadores_atingida
    
    #job = None
    aceitado_validadores = False
    lista_validador_status_aprovacao.clear()
    ids_validadores_selecionados.clear()
    min_qnt_validadores_atingida = False
    
    
def calcular_porcentagem_votos(string,lista_validador_status_aprovacao):
    contador_1 = 0
    contador_2 = 0

    for dicionario in lista_validador_status_aprovacao:
        for chave, valor in dicionario.items():
            if valor == 1:
                contador_1 += 1
            elif valor == 2:
                contador_2 += 1


    total = contador_1 + contador_2


    if total > 0:
        if string == "aprovado":
            p_aprovado = (contador_1 / total) * 100
            return p_aprovado 
        elif string == "reprovado":
            p_reprovado = (contador_2 / total) * 100
            return p_reprovado
    else:
        if string == "aprovado":
            p_aprovado = 0
            return p_aprovado 
        elif string == "reprovado":
            p_reprovado = 0
            return p_reprovado
    


#######################################






Fila_de_espera = []
validadors_que_sairam_da_fila = []

banco = {}
carteira_generica_selector = 0 #carteira ilustrativa


aceitado_validadores = False
job = None


@app.route('/receber_job', methods=['POST'])
def receber_job():
    
    global aceitado_validadores
    global job
    job = request.json
    aceitado_validadores = True
    print("Job recebido")
    
    if len(Fila_de_espera) < 3: # era pra ser 9
        print("Porem não existem validadores suficientes na fila para validar")
        thread_lifetime_job_thread = threading.Thread(target=thread_lifetime_job)
        thread_lifetime_job_thread.start()   
    return "Rota acionada"

def thread_lifetime_job():
    global job
    global min_qnt_validadores_atingida
    x = 60
    while x > 0:
        print(f"{x} Tempo de vida restate para job")
        x-= 1
        time.sleep(1)
        if min_qnt_validadores_atingida == True:
            break
    if min_qnt_validadores_atingida == False:
        job = None
        print("Job apagada")
            
            
    
    

@app.route('/receber_informacoes_validadores', methods=['POST'])
def receber_informacoes(): #para cada validador
    dados = request.json
    nova_rota = dados.get('rota')
    id_validador = dados.get('id_validador')
        
    if id_validador == "None":
        id_gerado = str(uuid.uuid1())
            
        #garante que nao exista id duplicado
        while(id_gerado in banco):
            id_gerado = str(uuid.uuid1())
        saldo = {
        "saldo": 50
        }
        banco[id_gerado] = saldo #registra validador no banco com saldo, caso ele nao exista no banco.
        #cria chave "flag" no dicionario do validador ao inserir no banco
        banco[id_gerado]["flag"] = 0
        id_validador = id_gerado
        
        
        
    
        
    json_validadors = {
        'rota': nova_rota,
        'id_validador': id_validador,

    }
    
    
    
    
        
        
    #Essa rota irá receber os validadores e eles serão armazenados em uma fila        
    Fila_de_espera.append(json_validadors)
    print("Validador adicionado a fila de espera")
    print(Fila_de_espera)
    
    return "Dados recebidos com sucesso", 200



lista_validador_status_aprovacao = []
@app.route('/receber_status_aprovacao', methods=['POST'])
def receber_status_aprovacao():
    
    
    global carteira_generica_selector
    global lista_validador_status_aprovacao
    global ids_validadores_selecionados
    data = request.json
    
    lista_validador_status_aprovacao.append(data)
    
    if len(lista_validador_status_aprovacao) == 3:
        print("####################################")
        print(banco)
        print("####################################")
        
        for validador in lista_validador_status_aprovacao:
            if validador["id_validador"] not in ids_validadores_selecionados:
                validador["status_aprovacao"] = 2 
                print(f"id validador '{validador["id_validador"]}' não existe na lista de validadores selecionados para validação")
                print("Portanto o status de aprovação do validador foi alterado para 2 (não aprovado)")
            
            print(f"validador '{validador["id_validador"]}' respondeu com um status {validador["status_aprovacao"]}")
            
        log = f"Validadores retornaram com estados de aprovação/rejeição de uma job do remetente '{job["id_remetente"]}': {lista_validador_status_aprovacao}"
        enviar_log_banco(log)  
            
        #calculo porcentagens aprovado/reprovado
        p_aprovado = calcular_porcentagem_votos("aprovado",lista_validador_status_aprovacao)
        p_reprovado = calcular_porcentagem_votos("reprovado",lista_validador_status_aprovacao)
        
        print(f"Transação teve %{p_aprovado} de aprovação")
        print(f"Transação teve %{p_reprovado} de reprovação")
        
        if p_aprovado >= p_reprovado:
            print("Transação aprovada")
            for validador in lista_validador_status_aprovacao:
                if validador["status_aprovacao"] == 2:
                    banco[validador["id_validador"]]["flag"] += 1
                    log = f"Validador {banco[validador["id_validador"]]} recebeu uma flag!"
                    enviar_log_banco(log)
        else:
            print("Transação reprovada")
            for validador in lista_validador_status_aprovacao:
                if validador["status_aprovacao"] == 1:
                    banco[validador["id_validador"]]["flag"] += 1
                    log = f"Validador {banco[validador["id_validador"]]} recebeu uma flag!"
                    enviar_log_banco(log)
                    

        
        #cada dict em lista_validador_status_aprovacao está nesse formato:
        #{'id_validador': '386cc4ad-1ba6-11ef-9927-047f0e0fd903', 'status_aprovacao': 1}

        
                    
        taxas = (job["quantia"] * 0.015)
        
        parte_seletor = taxas - (job["quantia"] * 0.005)
        parte_validadores = taxas - (job["quantia"] * 0.010)
        
        carteira_generica_selector += parte_seletor
        log = f"Seletor foi pago {parte_seletor} NoNameCoins referente a uma job do remetente {job["id_remetente"]}"
        enviar_log_banco(log)
        
        parte_validadores = parte_validadores / len(lista_validador_status_aprovacao)
        
        for validador in lista_validador_status_aprovacao:
            banco[validador["id_validador"]]["saldo"] += parte_validadores
            log = f"Validador {validador["id_validador"]} foi pago {parte_validadores} NoNameCoins referente a uma job do remetente {job["id_remetente"]}"
            enviar_log_banco(log)
        
        

        
        print("####################################")
        print(banco)
        print("####################################")
            
        #resetando variaveis para proxima job
        reset_variaveis()
    
        
    
    
 
    
    
        
    return "Recebi o status de aprovação de um validador"
    
    
    
    



def devolver_informacoes_validadores(lista_validadores): 
    validadores = lista_validadores
    global relogio_atual
    


    print(f'Rotas coletadas da fila: {len(validadores)}')
    

    if len(validadores) >= 3: #especificacao do projet diz que tem q ser 9
        
        
        #############################################################################################
        #sync inicial de relogios dos seletores e validadores utilizando o relogio do servidor(banco)
        while True:
                try:
                    response = requests.get("http://127.0.0.1:5000/obter_relogio") # rota para pegar relogio do banco
                    if response.status_code == 200:
                        
                        #substitui relogio seletor pelo do servidor
                        relogio_atual = response.json().get('relogio')
                        
                        #envia o relogio do seletor (que era do servidor(banco) para os validadores)
                        for validador in validadores:
                            while True: 
                                try:
                                    response = requests.post(validador["rota"] + '/receber_novo_relogio', json={'diferenca_relogio': relogio_atual})
                                    if response.status_code == 200:
                                        print(f'Diferença de relógio enviada para {validador["rota"]}')
                                        break
                                except requests.exceptions.RequestException as e:
                                    print(f"Erro ao conectar à rota {validador["rota"]}: {e}")
                        
                        print("Validadores sincronizados com o relogio do banco(servidor)!")
                        log = f"Os seguintes validadores foram sincronizados com o relogio fornecido pelo banco(servidor): {lista_validadores}"
                        enviar_log_banco(log)
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        break  # Sai do loop se a solicitação for bem-sucedida
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {validador["rota"]}: {e}")
                    print("Tentando novamente...")
        #############################################################################################
        
        
        
        log = f"foram coletados os seguintes validadores da fila de espera: {lista_validadores}"
        enviar_log_banco(log)
        
        
        
        
        
        relogios = []
        rotas = []
        ##########Sync relogios

        ######## obtem relogios dos validadores
        for validador in validadores:
            while True:
                try:
                    response = requests.get(validador["rota"] + '/obter_relogio')
                    if response.status_code == 200:
                        relogios.append(response.json().get('relogio'))
                        
                        
                    
                        
                        print(f"Relogios recebidos: {relogios}")
                        
                        
                        rotas.append(validador["rota"])
                        
                        break  # Sai do loop se a solicitação for bem-sucedida
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {validador["rota"]}: {e}")
                    print("Tentando novamente...")
        ###########            

        ################### Calcula média relógios modelo bert
        if rotas:
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
        #####################
        log = f"Relogios dos seguintes validadores foram sincronizados usando o modelo de bertley: {lista_validadores}"
        enviar_log_banco(log)   
        
        # Devolvendo ids gerados            
        for validador in validadores:
            while True:
                try:
                    response = requests.post(validador["rota"] + '/receber_id', json={'id_gerado': validador["id_validador"]})
                    if response.status_code == 200:
                        print(f"Id enviado para {validador["rota"]}")
                        break 
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {validador["rota"]}: {e}")
                    print("Tentando novamente...")
        log = f"IDs foram distribuidos para os seguintes validadores: {lista_validadores}"
        enviar_log_banco(log)   
                    
                    
                                
        # retorna json com id_validador e rota
        validadores_escolhidos = selecionar_validadores(validadors_que_sairam_da_fila) # retorna json dos validadores escolhidos
        
        log = f"Foram escolhidos os seguintes validadores para validar a job do remetente '{job["id_remetente"]}': {lista_validadores}"
        enviar_log_banco(log)   
        print(validadores_escolhidos)
        #adicionando validadores que nao foram escolhidos no inicio da fila de espera
        for validador in lista_validadores:
            existe = any(dicionario.get("id_validador") == validador["id_validador"] for dicionario in validadores_escolhidos)
            if not existe:
                print(f"validador {validador['id_validador']} não foi escolhido, portanto irá ser inserido no início da fila novamente")
                Fila_de_espera.insert(0, validador)
        
        
        #mandar job para validadores escolhidos
        print("Validadores escolhidos que estão recebendo a job", validadores_escolhidos)
        for validador in validadores_escolhidos:
            while True:
                try:
                    response = requests.post(validador["rota"] + '/validar_job', json=job)
                    if response.status_code == 200:
                        print(f"Id enviado para {validador["rota"]}")
                        break 
                except requests.exceptions.RequestException as e:
                    print(f"Erro ao conectar à rota {validador["rota"]}: {e}")
                    print("Tentando novamente...")
        
        log = f"A job do remetente '{job["id_remetente"]}' foi enviada para os seguintes validadores: {lista_validadores}"
        enviar_log_banco(log)
                 
        
        
        

        

        



#manager de fila
def verificar_fila():
    global min_qnt_validadores_atingida, aceitado_validadores
    min_qnt_validadores_atingida = False
    while True:
        if aceitado_validadores == True:
            if len(Fila_de_espera) >= 3:
                min_qnt_validadores_atingida = True
                print("Fila de espera validadores possui o minimo de validadores para validar!")
                x = len(Fila_de_espera)
                max = 0
                while(x > 0 and max < 5):
                    validadors_que_sairam_da_fila.append(Fila_de_espera[0])
                    Fila_de_espera.pop(0)
                    x -=1
                    max +=1
                print("Validadores que sairam da fila", validadors_que_sairam_da_fila)
                if len(validadors_que_sairam_da_fila) >= 3:
                    for validador in validadors_que_sairam_da_fila:
                        #guarda ids para verificar se o id existe no banco ao receber a resposta da validacao 
                        ids_validadores_selecionados.append(validador["id_validador"])
                    
                    aceitado_validadores = False
                        
                    devolver_informacoes_validadores(validadors_que_sairam_da_fila)
                    validadors_que_sairam_da_fila.clear()
                

ids_validadores_selecionados = []

            
            
delta_relogio = datetime.timedelta()
relogio_atual = "sem relogio" 
def atualizar_relogio():
    global relogio_atual, delta_relogio
    while True:
        relogio_atual = (datetime.datetime.now() + delta_relogio).strftime("%H:%M:%S")
        time.sleep(1)


if __name__ == '__main__':
    
    thread_relogio = threading.Thread(target=atualizar_relogio)
    thread_relogio.start()
    
    
    thread_verificar_fila = threading.Thread(target=verificar_fila)
    thread_verificar_fila.start()
    
    
    
    app.run(host='127.0.0.1', port=5001) 
    

    #a