import os
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional, Tuple
import sys
from tqdm import tqdm
from google_auth_httplib2 import AuthorizedHttp
import httplib2


# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_environment_variables(env_file: str) -> None:
    """Carrega variáveis de ambiente de um arquivo .env."""
    load_dotenv(env_file)
    required_vars = ['PROJECT_ID', 'FOLDER_ID', 'GOOGLE_APPLICATION_CREDENTIALS']
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            logging.error(f"Variável de ambiente {var} não encontrada. Verifique seu arquivo .env")
            sys.exit(1)
        if var == 'GOOGLE_APPLICATION_CREDENTIALS' and not os.path.isfile(value):
            logging.error(f"O arquivo de credenciais {value} não foi encontrado.")
            sys.exit(1)

def get_bigquery_client(credentials: service_account.Credentials, project_id: str) -> bigquery.Client:
    """Inicializa e retorna um cliente BigQuery."""
    return bigquery.Client(credentials=credentials, project=project_id)

def load_query_from_file(file_path: str) -> str:
    """Carrega a query de um arquivo SQL."""
    path = Path(file_path)
    if path.is_file():
        return path.read_text()
    else:
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

def execute_query(client: bigquery.Client, query: str) -> pd.DataFrame:
    """Executa a query no BigQuery e retorna os resultados como DataFrame."""
    try:
        query_job = client.query(query)
        return query_job.result().to_dataframe()
    except Exception as e:
        logging.error("Erro ao executar a query", exc_info=True)
        raise e

def save_to_csv_buffer(df: pd.DataFrame) -> io.BytesIO:
    """Salva DataFrame como CSV em um buffer."""
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return buffer

def upload_to_drive(service, folder_id: str, csv_buffer: io.BytesIO, filename: str) -> str:
    """Faz upload de um arquivo CSV para o Google Drive e retorna o ID do arquivo."""
    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaIoBaseUpload(csv_buffer, mimetype='text/csv', resumable=True)
        request = service.files().create(body=file_metadata, media_body=media, fields='id')

        # Inicializar barra de progresso
        with tqdm(total=int(csv_buffer.getbuffer().nbytes), unit='B', unit_scale=True, desc='Upload Progress') as pbar:
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pbar.update(status.resumable_progress - pbar.n)

        return response.get('id')
    except Exception as e:
        logging.error("Erro ao fazer upload para o Google Drive", exc_info=True)
        raise e

def initialize_clients(credentials_path: str) -> Tuple[bigquery.Client, 'googleapiclient.discovery.Resource']:
    """Inicializa clientes do BigQuery e Google Drive."""
    try:
        scopes = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/bigquery']
        credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
        project_id = os.getenv('PROJECT_ID')
        bigquery_client = get_bigquery_client(credentials, project_id)

        # Configurar cliente HTTP com tempo de espera estendido
        http = httplib2.Http(timeout=300)  # 5 minutos de timeout
        authed_http = AuthorizedHttp(credentials, http=http)
        drive_service = build('drive', 'v3', http=authed_http)

        return bigquery_client, drive_service
    except Exception as e:
        logging.error("Erro ao inicializar clientes", exc_info=True)
        raise e


def main():
    try:
        # Carregar variáveis de ambiente
        load_environment_variables('.env')

        # Inicializar clientes e configurações
        folder_id = os.getenv('FOLDER_ID')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

        bigquery_client, drive_service = initialize_clients(credentials_path)

        # Carregar e executar a query
        query = load_query_from_file('sql/query.sql')
        results = execute_query(bigquery_client, query)

        # Salvar resultados em CSV
        csv_buffer = save_to_csv_buffer(results)

        # Gerar timestamp e nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f'resultados_{timestamp}.csv'

        # Fazer upload para o Google Drive
        file_id = upload_to_drive(drive_service, folder_id, csv_buffer, filename)

        logging.info(f"File ID: {file_id}")

    except FileNotFoundError as fnf_error:
        logging.error("Arquivo não encontrado", exc_info=True)
    except google.auth.exceptions.GoogleAuthError as auth_error:
        logging.error("Erro de autenticação do Google", exc_info=True)
    except Exception as e:
        logging.error("Ocorreu um erro inesperado", exc_info=True)

if __name__ == "__main__":
    main()
