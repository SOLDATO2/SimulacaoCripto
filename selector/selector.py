import requests

# Definindo o JSON genérico
json_data = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
}

# Enviando o JSON para a rota do Programa 2
#Rota esta sendo definida manualmente, tem que ser automatizada
response = requests.post('http://localhost:5001/receive_json', json=json_data)
print(response.text)