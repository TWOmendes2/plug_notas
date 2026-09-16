import os
import argparse
from decimal import Decimal, ROUND_HALF_UP
import csv
import requests







def load_config():
    names = ('PLUGNOTAS_API_KEY', 'CNPJ_SERVICO', 'CNPJ_PRODUTO',
             'INSCRICAO_MUNICIPAL', 'INSCRICAO_ESTADUAL', 'SERVICE_SHARE',
             'ISS_RATE', 'PIS_RATE', 'COFINS_RATE', 'PIS_CST',
             'SERVICE_DESCRIPTION', 'PRODUCT_DESCRIPTION')
    config = {name: os.environ.get(name, '').strip() for name in names}
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise ValueError('Variáveis ausentes: ' + ', '.join(missing))
    for name in ('SERVICE_SHARE', 'ISS_RATE', 'PIS_RATE', 'COFINS_RATE'):
        value = Decimal(config[name])
        limit = Decimal(1) if name == 'SERVICE_SHARE' else Decimal(100)
        if not value.is_finite() or not 0 <= value <= limit:
            raise ValueError('Configuração numérica inválida: ' + name)
        config[name] = value
    return config


def processar_clientes(csv_file, config, send=False):
    TOKEN = config['PLUGNOTAS_API_KEY']
    CNPJ_SERVICO = config['CNPJ_SERVICO']
    CNPJ_PRODUTO = config['CNPJ_PRODUTO']
    URL_NFE = 'https://api.sandbox.plugnotas.com.br/nfe'
    URL_NFSE = 'https://api.sandbox.plugnotas.com.br/nfse' 
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                nome = row.get("Nome", "").strip()
                if not nome:
                    raise ValueError('Nome ausente')

                try:
                    valor_total = Decimal(row["Valor Total da Venda"])
                    if not valor_total.is_finite() or valor_total <= 0:
                        raise ValueError('Valor inválido')
                    valor_total = valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valor_servico = (valor_total * config['SERVICE_SHARE']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valor_produto = valor_total - valor_servico
                except ValueError:
                    raise ValueError('Valor inválido') from None

               
                nfse_payload = [{
                    "prestador": {
                        "cpfCnpj": CNPJ_SERVICO,
                        "inscricaoMunicipal": config['INSCRICAO_MUNICIPAL']
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
                        "descricao": config['SERVICE_DESCRIPTION'],
                        "aliquota": float(config['ISS_RATE']),
                        "valor": float(valor_servico),  
                        "codigoMunicipio": row["Código Município"]
                    }
                }]

                
                nfe_payload = [{
                    "emitente": {
                        "cpfCnpj": CNPJ_PRODUTO,
                        "inscricaoEstadual": config['INSCRICAO_ESTADUAL']
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
                        "descricao": config['PRODUCT_DESCRIPTION'],
                        "ncm": row["NCM"],
                        "cfop": row["CFOP"],
                        "quantidade": 1,
                        "valorUnitarioComercial": float(valor_produto), 
                        "valorUnitarioTributavel": float(valor_produto), 
                        "tributos": {
                            "pis": {
                                "cst": config['PIS_CST'],
                                "baseCalculo": float(valor_produto),
                                "aliquota": float(config['PIS_RATE']),
                                "valor": float((valor_produto * config['PIS_RATE'] / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                            },
                            "cofins": {
                                "cst": row["CST"],
                                "baseCalculo": float(valor_produto),
                                "aliquota": float(config['COFINS_RATE']),
                                "valor": float((valor_produto * config['COFINS_RATE'] / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                            }
                        }
                    }]
                }]



                if send:
                    enviar_para_plugNotas(nfe_payload, URL_NFE, TOKEN)
                    enviar_para_plugNotas(nfse_payload, URL_NFSE, TOKEN)
                print('Linha processada; envio=' + str(send))



            except (ValueError, KeyError, ArithmeticError):
                raise ValueError('CSV inválido; processamento interrompido sem exibir dados pessoais') from None


def enviar_para_plugNotas(payload, url, token):
    try:
        response = requests.post(url, json=payload,
                                 headers={'X-API-KEY': token}, timeout=10,
                                 allow_redirects=False)
        if not 200 <= response.status_code < 300:
            raise RuntimeError('Envio recusado; consulte o painel seguro do provedor')
    except requests.exceptions.RequestException:
        raise RuntimeError('Falha de comunicação; confira o painel antes de reenviar') from None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Integração demonstrativa PlugNotas (sandbox)')
    parser.add_argument('--csv', default='clientes_teste.csv')
    parser.add_argument('--send', action='store_true', help='Enviar explicitamente ao sandbox')
    args = parser.parse_args()
    try:
        processar_clientes(args.csv, load_config(), args.send)
    except (ValueError, RuntimeError, OSError, ArithmeticError):
        parser.exit(1, 'Falha: confira configuração, CSV e painel seguro; nenhum dado sensível será exibido.\n')
