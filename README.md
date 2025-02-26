# Integração com a API PlugNotas

Este projeto tem como objetivo integrar a API da PlugNotas para emissão de **NFe (Nota Fiscal Eletrônica)** e **NFS-e (Nota Fiscal de Serviço Eletrônica)**, dividindo o valor total da venda em **70% para serviço** e **30% para produto**.

## 📌 Funcionalidades
- Processa um arquivo CSV contendo informações de clientes e valores de venda.
- Divide automaticamente os valores entre **produto** e **serviço**.
- Envia requisições para emissão de **NFe** e **NFS-e** na API da PlugNotas.
- Exibe o JSON gerado antes do envio para depuração.
- Captura e exibe os erros retornados pela API.

## 🛠️ Tecnologias Utilizadas
- **Python 3.x**
- **Bibliotecas:**
  - `requests` (para comunicação com a API)
  - `csv` (para leitura do arquivo CSV)
  - `json` (para manipulação de dados JSON)

## 📂 Estrutura do Projeto
```
📁 projeto
│-- plug-notas.py  # Código principal para processamento e envio das notas
│-- clientes_teste.csv  # Arquivo CSV com os dados dos clientes
│-- README.md  # Documentação do projeto
```

## ⚙️ Configuração
### 1️⃣ **Instalar dependências**
Se ainda não tiver a biblioteca `requests`, instale com:
```sh
pip install requests
```

### 2️⃣ **Definir o Token da API**
O token de autenticação da PlugNotas deve ser configurado corretamente no código:
```python
TOKEN = "SEU_TOKEN_AQUI"
```
Caso precise de um novo token, acesse o **Painel da PlugNotas**.

### 3️⃣ **Executar o Script**
Para rodar o script, utilize:
```sh
python plug-notas.py
```

## 📥 Formato do Arquivo CSV
O arquivo `clientes_teste.csv` deve conter os seguintes campos:
```csv
Nome,CPF/CNPJ,Logradouro,Número,Bairro,Código Município,UF,CEP,Valor Total da Venda,NCM,CFOP,CST
"Cliente Teste","12345678000123","Rua Exemplo","123","Centro","3550308","SP","01001000","1000.00","49019900","5101","06"
```

## 🚀 Como Funciona
1. O script lê o CSV e separa o valor da venda em **70% serviço e 30% produto**.
2. Gera os JSONs necessários para a API da PlugNotas.
3. Envia requisições para emissão de NFe e NFS-e.
4. Exibe os JSONs enviados e as respostas da API.

## 🛑 Possíveis Erros e Soluções
### ❌ **Erro: "Já existe uma NFe com os parâmetros informados"**
🔹 **Causa:** O mesmo `idIntegracao` foi utilizado antes.
🔹 **Solução:** Gerar um novo ID para cada nota:
```python
import uuid
novo_id_integracao = str(uuid.uuid4())
```

### ❌ **Erro: "Falha na validação do JSON de NFSe"**
🔹 **Causa:** Algum campo obrigatório está ausente ou com valor inválido.
🔹 **Solução:** Verificar se `valor`, `razaoSocial` e `endereco` estão corretos antes de enviar.


