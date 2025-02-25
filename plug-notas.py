import requests
import csv

API_KEY = "SUA_CHAVE_DA_API"
URL = "https://api.plugnotas.com.br/nfse"


def ler_csv(arquivo):
    notas = []
    with open(arquivo, mode="r", encoding="utf-8") as file:
        leitor = csv.DictReader(file)
        for linha in leitor:
            notas.append(linha)
    return notas

def emitir_nfse(dados):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(URL, json=dados, headers=headers)
    
    if response.status_code == 201:
        print("NFS-e emitida com sucesso!")
        print(response.json()) 
    else:
        print("Erro ao emitir NFS-e:", response.text)

notas = ler_csv("notas.csv")

for nota in notas:
    valor_total = float(nota["valor_total"])
    valor_servico = round(valor_total * 0.70, 2)  
    valor_produto = round(valor_total * 0.30, 2)  

   
    dados_nfse = {
        "tomador": {
            "cpfCnpj": nota["cpf_cnpj"],
            "razaoSocial": nota["nome"],
            "endereco": {
                "logradouro": "Rua Exemplo",
                "numero": "123",
                "bairro": "Centro",
                "codigoMunicipio": "",  # Código de Maceió (AL)
                "uf": "AL",
                "cep": "57000000"
            }
        },
        "servico": {
            "discriminacao": nota["descricao"],
            "codigo": nota["codigo_servico"],
            "aliquotaIss": 5.0,
            "valor": valor_servico
        },
        "produtos": [
            {
                "codigo": nota["codigo_produto"],
                "descricao": "Material Didático",
                "ncm": "49019900",  # Exemplo de NCM para livros fisicos
                "quantidade": 1,
                "valorUnitario": valor_produto
            }
        ],
        "valor": valor_total
    }

    # Emitir a NFS-e
    emitir_nfse(dados_nfse)
