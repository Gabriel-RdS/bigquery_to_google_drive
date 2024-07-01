### README.md

```markdown
# BigQuery to Google Drive

Uma solução Python para exportar dados de uma consulta BigQuery para o Google Drive. O script executa uma query no BigQuery, salva os resultados em um arquivo CSV com um sufixo de timestamp e faz upload para uma pasta específica no Google Drive, seguindo as melhores práticas de desenvolvimento.

## Estrutura do Repositório

```
bigquery_to_google_drive/
│
├── credentials/
│   └── credentials.json
│
├── sql/
│   └── query.sql
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Configuração e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/Gabriel-RdS/bigquery_to_google_drive.git
cd bigquery_to_google_drive
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Credenciais

Coloque o arquivo `credentials.json` na pasta `credentials/`. Esse arquivo deve conter as credenciais da conta de serviço com permissões para acessar o BigQuery e o Google Drive.

### 4. Configurar o Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
PROJECT_ID=sandbox
FOLDER_ID=1A2B3C4D5E6F
GOOGLE_APPLICATION_CREDENTIALS=credentials/credentials.json
```

Substitua `sandbox` pelo ID do seu projeto no Google Cloud e `1A2B3C4D5E6F` pelo ID da pasta no Google Drive.

### 5. Criar a Query SQL

Adicione a query SQL ao arquivo `sql/query.sql`. Por exemplo:

```sql
SELECT * FROM sandbox.user_gabriel_ramos.poc_check_provedores_regionais LIMIT 10;
```

### 6. Adicionar `.gitignore`

Adicione um arquivo `.gitignore` com o seguinte conteúdo:

```gitignore
# Ignorar credenciais e arquivos de ambiente
credentials/
.env

# Ignorar arquivos e pastas do Python
__pycache__/
*.pyc

# Ignorar arquivos de log
*.log
```

### 7. Executar a Aplicação

```bash
python main.py
```