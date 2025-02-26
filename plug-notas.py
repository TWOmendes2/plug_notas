import json
import csv
import requests
from decimal import Decimal

URL_NFSE = "https://api.sandbox.plugnotas.com.br/nfse"

TOKEN = "2da392a6-79d2-4304-a8b7-959572c7e44d"

CNPJ_SERVICO = "08187168000160"
RAZAO_SOCIAL = "ISOS SOLUÇÕES EDUCACIONAIS LTDA"
INSCRICAO_MUNICIPAL = "123456" 
NOME_FANTASIA = "SISTEMA ISOS"


SERIE_RPS = "10"
NUMERO_RPS = "3056"
LOTE_RPS = "3275"


def processar_clientes(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                nome = row.get("Nome", "").strip()
                if not nome:
                    print(f"❌ Nome ausente para CPF/CNPJ: {row.get('CPF/CNPJ', 'Desconhecido')}")
                    continue

                valor_total = 220.00

                
                nfse_payload = [{
                    "idIntegracao": "206530",  
                    "emitente": {
                        "cpfCnpj": CNPJ_SERVICO,
                        "razaoSocial": RAZAO_SOCIAL,
                        "inscricaoMunicipal": INSCRICAO_MUNICIPAL,
                        "nomeFantasia": NOME_FANTASIA
                    },
                    "prestador": {
                        "cpfCnpj": CNPJ_SERVICO,
                        "razaoSocial": RAZAO_SOCIAL,
                        "inscricaoMunicipal": INSCRICAO_MUNICIPAL
                    },
                    "tomador": {
                        "cpfCnpj": row["CPF/CNPJ"],
                        "razaoSocial": nome,
                        "endereco": {
                            "logradouro": row["Logradouro"],
                            "numero": row["Número"],
                            "bairro": row["Bairro"],
                            "codigoMunicipio": row["Código Município"],
                            "uf": row["UF"],
                            "cep": row["CEP"]
                        }
                    },
                    "servico": [{
                        "descricao": "Consultoria em Tecnologia",
                        "aliquota": 5.00,
                        "valor": round(valor_total, 2),  
                        "codigoMunicipio": row["Código Município"],
                        "issRetido": False,  
                        "responsavelRetencao": None,  
                        "itemListaServico": "0107",  
                        "discriminacao": "Serviços de consultoria em tecnologia da informação",
                        "codigoTributacaoMunicipio": "0107", 
                        "cidadePrestacao": {
                            "codigoMunicipio": row["Código Município"],
                            "descricaoMunicipio": "São Paulo"  
                        }
                    }],
                    "rps": {
                        "serie": SERIE_RPS,
                        "numero": NUMERO_RPS,
                        "lote": LOTE_RPS
                    },
                    "ambiente": "Homologacao",  
                    "enviarEmail": False,  
                    "naturezaTributacao": 1,  
                    "regimeApuracaoTributaria": 1  
                }]

                
                print("\n🔹 JSON da NFS-e:", json.dumps(nfse_payload, indent=4, ensure_ascii=False))

                
                print(f"📤 Enviando NFS-e para {nome}")
                enviar_para_plugNotas(nfse_payload, URL_NFSE, "serviço", CNPJ_SERVICO)

            except Exception as e:
                print(f"❌ Erro ao processar cliente {row.get('Nome', 'Desconhecido')}: {e}")


def enviar_para_plugNotas(payload, url, tipo_item, cnpj):
    headers = {
        "X-API-KEY": TOKEN,
        "Content-Type": "application/json"
    }

    response = None 
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✔ {tipo_item.capitalize()} enviado com sucesso para CNPJ {cnpj}!")
        print("Resposta da API:", response.json())
    except requests.exceptions.Timeout:
        print(f"⏳ Tempo limite excedido ao enviar {tipo_item} (CNPJ: {cnpj})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao enviar {tipo_item} (CNPJ: {cnpj}): {e}")
        if response is not None:  
            print("Resposta da API:", response.text)


if __name__ == "__main__":
    processar_clientes("clientes_teste.csv")