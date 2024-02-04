# Define a imagem base
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependências para o diretório de trabalho atual e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta em que a aplicação Flask vai rodar
EXPOSE 5000

# Define a variável de ambiente para executar a aplicação em produção
ENV FLASK_ENV=production

# Executa a aplicação Flask
CMD ["flask", "run", "--host=0.0.0.0"]