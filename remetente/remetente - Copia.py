
import requests
import time




def enviar_dados(id_remetente, quantia, id_destinatario, saldo):

    print("Enviando dados...")

    while True:
        try:
            response = requests.post('http://127.0.0.1:5000/receber_informacoes_banco', json={'id_remetente': id_remetente, 'quantia': quantia, 'id_destinatario': id_destinatario, 'saldo': saldo})
            if response.status_code == 200:
                print("Dados enviados com sucesso para o banco.")
                break
            else:
                print(f"Falha ao enviar dados para o banco: {response.json().get('erro')}")
        except requests.exceptions.RequestException as e:
            print("Erro de conexão:", e)
        time.sleep(2)  # Ajustar o tempo de espera conforme necessário





if __name__ == '__main__':
    
    #Valores apenas representativos
    saldo = 1000
    id_remetente = "500"
    quantia = 10
    id_destinatario = "600"
     
    enviar_dados(id_remetente, quantia, id_destinatario, saldo)
    
    
    


    #a