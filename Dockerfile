# Usar a imagem oficial do Ubuntu como base
FROM ubuntu:latest

# Instalar as dependências necessárias
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto para o contêiner
COPY . /app

# Comando padrão ao iniciar o contêiner
CMD ["python3"]
