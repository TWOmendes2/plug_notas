# PlugNotas — integração fiscal demonstrativa

Cliente Python que lê vendas em CSV, divide o valor entre serviço e produto e monta
requisições NFe/NFS-e. Destina-se a estudo de integração; os esquemas e regras fiscais
precisam de homologação com o provedor antes de qualquer uso operacional.

## Execução

Requer Python 3.11+ e `pip install -r requirements.txt`. Configure no ambiente as
variáveis listadas em `.env.example`; o programa não carrega `.env` automaticamente.
Percentuais tributários são expressos de 0 a 100; SERVICE_SHARE é uma fração de 0 a 1.
Nenhum enquadramento fiscal é presumido. Os exemplos de documentos são fictícios.

```sh
python plug-notas.py --csv clientes_teste.csv
python -m unittest discover -s tests -v
```

A execução padrão apenas monta os dados, sem exibi-los ou enviá-los. `--send` ativa
o envio ao sandbox. O exemplo intencionalmente inválido não serve para emissão.
Use um CSV local autorizado, protegido e ignorado pelo Git para homologação.

## Fluxo e limites

Ambiente → configuração validada → CSV → divisão decimal → payloads → sandbox.
Valores monetários usam Decimal e arredondamento de centavos; o saldo vai para produto.
A integração mantém o formato legado dos payloads, ainda sem validação completa do
contrato fiscal. O primeiro erro de envio interrompe o lote. Não existe transação
entre os dois documentos, deduplicação persistente ou reconciliação automática.

As saídas omitem dados pessoais e respostas do provedor. Consulte [SECURITY.md](SECURITY.md)
para revogação da chave histórica e tratamento dos dados anteriormente publicados.

## Próximas melhorias

Validar contratos do provedor com fixtures oficiais de sandbox; registrar IDs de
integração sem PII; adicionar reconciliação e armazenamento seguro do estado do lote.
