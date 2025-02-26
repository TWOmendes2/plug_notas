import json
import csv
import requests


URL_NFE = "https://api.sandbox.plugnotas.com.br/nfe"
URL_NFSE = "https://api.sandbox.plugnotas.com.br/nfse"


TOKEN = "2da392a6-79d2-4304-a8b7-959572c7e44d"


CNPJ_SERVICO = "08187168000160"
CNPJ_PRODUTO = "08187168000160"

def processar_clientes(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                nome = row.get("Nome", "").strip()
                if not nome:
                    print(f"❌ Nome ausente para CPF/CNPJ: {row.get('CPF/CNPJ', 'Desconhecido')}")
                    continue

                try:
                    valor_total = float(row["Valor Total da Venda"])
                    valor_servico = round(float(valor_total) * 0.7, 2)
                    valor_produto = round(float(valor_total) * 0.3, 2)
                except ValueError:
                    print(f"❌ Erro ao converter valores para {nome}")
                    continue

             
                if not isinstance(valor_servico, (int, float)) or not isinstance(valor_produto, (int, float)):
                    print(f"❌ Erro: Valores inválidos para {nome}")
                    continue

               
                nfse_payload = [{
                    "prestador": {
                        "cpfCnpj": CNPJ_SERVICO,
                        "inscricaoMunicipal": "123456"
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
                    "servico": {  
                        "descricao": "Consultoria em Tecnologia",
                        "aliquota": 5.00,
                        "valor": float(valor_servico),  
                        "codigoMunicipio": row["Código Município"]
                    }
                }]

                
                nfe_payload = [{
                    "emitente": {
                        "cpfCnpj": CNPJ_PRODUTO,
                        "inscricaoEstadual": "123456789"
                    },
                    "destinatario": {
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
                    "itens": [{
                        "descricao": "Produto Exemplo",
                        "ncm": row["NCM"],
                        "cfop": row["CFOP"],
                        "quantidade": 1,
                        "valorUnitarioComercial": float(valor_produto), 
                        "valorUnitarioTributavel": float(valor_produto), 
                        "tributos": {
                            "pis": {
                                "cst": "01",
                                "baseCalculo": float(valor_produto),
                                "aliquota": 1.65,
                                "valor": round(valor_produto * 0.0165, 2)
                            },
                            "cofins": {
                                "cst": row["CST"],
                                "baseCalculo": float(valor_produto),
                                "aliquota": 7.60,
                                "valor": round(valor_produto * 0.076, 2)
                            }
                        }
                    }]
                }]

               
                print("\n🔹 JSON da NFe:", json.dumps(nfe_payload, indent=4, ensure_ascii=False))
                print("\n🔹 JSON da NFS-e:", json.dumps(nfse_payload, indent=4, ensure_ascii=False))

                
                print(f"📤 Enviando NFe para Produto (30%) - Cliente: {nome}")
                enviar_para_plugNotas(nfe_payload, URL_NFE, "produto", CNPJ_PRODUTO)

             
                print(f"📤 Enviando NFS-e para Serviço (70%) - Cliente: {nome}")
                enviar_para_plugNotas(nfse_payload, URL_NFSE, "serviço", CNPJ_SERVICO)

            except Exception as e:
                print(f"❌ Erro ao processar cliente {row.get('Nome', 'Desconhecido')}: {e}")


def enviar_para_plugNotas(payload, url, tipo_item, cnpj):
    headers = {
        "X-API-KEY": TOKEN,
        "Content-Type": "application/json"
    }

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
