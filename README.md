# 📌 Emissor de Nota Fiscal de Serviço Eletrônica (NFS-e) usando a API PlugNotas

## 📋 Descrição
Este projeto em Python permite a emissão automática de Notas Fiscais de Serviço Eletrônica (NFS-e) utilizando a **API da PlugNotas**. Ele lê os dados de um arquivo CSV, separa a nota em **70% serviço e 30% produto**, e envia os dados para a API da PlugNotas para emissão.

---

## 🚀 Funcionalidades
- Leitura de notas fiscais a partir de um **arquivo CSV**.
- Cálculo automático de **70% como serviço e 30% como produto**.
- Montagem do JSON conforme as exigências da API PlugNotas.
- Envio da requisição para a API e exibição da resposta.

---

## 📌 Como Usar

### 1️⃣ **Configurar dependências**
Instale as bibliotecas necessárias:
```sh
pip install requests
```

### 2️⃣ **Criar o arquivo CSV**
Crie um arquivo `notas.csv` no seguinte formato:
```csv
cpf_cnpj,nome,descricao,codigo_servico,codigo_produto,valor_total
12345678900,João Silva,Curso de Matemática,1001,5001,2000.00
98765432100,Maria Souza,Curso de Português,1002,5002,1500.00
```

### 3️⃣ **Definir a chave da API**
No arquivo Python, substitua **SUA_CHAVE_DA_API** pela chave real da API PlugNotas.
```python
API_KEY = "SUA_CHAVE_DA_API"
```

### 4️⃣ **Executar o código**
```sh
python emissor_nfse.py
```

---

## 📜 Estrutura do Código
### 🔹 **Leitura do CSV**
A função `ler_csv()` carrega os dados do arquivo CSV.
```python
def ler_csv(arquivo):
    notas = []
    with open(arquivo, mode="r", encoding="utf-8") as file:
        leitor = csv.DictReader(file)
        for linha in leitor:
            notas.append(linha)
    return notas
```

### 🔹 **Montagem dos Dados para a API**
Os valores da nota são divididos:
```python
valor_total = float(nota["valor_total"])
valor_servico = round(valor_total * 0.70, 2)  # 70% do valor total
valor_produto = round(valor_total * 0.30, 2)  # 30% do valor total
```

A estrutura JSON da nota fiscal:
```python
dados_nfse = {
    "tomador": {
        "cpfCnpj": nota["cpf_cnpj"],
        "razaoSocial": nota["nome"],
        "endereco": {
            "codigoMunicipio": "2704302",  # Maceió (AL)
            "uf": "AL"
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
            "ncm": "49019900",
            "quantidade": 1,
            "valorUnitario": valor_produto
        }
    ],
    "valor": valor_total
}
```

### 🔹 **Envio da Nota para a API**
A função `emitir_nfse()` faz a requisição HTTP:
```python
def emitir_nfse(dados):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(URL, json=dados, headers=headers)
    if response.status_code == 201:
        print("NFS-e emitida com sucesso!")
    else:
        print("Erro ao emitir NFS-e:", response.text)
```

### 🔹 **Processamento das Notas**
```python
notas = ler_csv("notas.csv")
for nota in notas:
    emitir_nfse(dados_nfse)
```

---

## 📌 Referências
- [PlugNotas - Documentação Oficial](https://docs.plugnotas.com.br/)

