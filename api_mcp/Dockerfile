
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da API
COPY . .

# Criar diretório para o arquivo .env
RUN mkdir -p /app/env_files

# O arquivo .env será montado como volume pelo docker-compose
# mas também criamos um arquivo vazio para evitar erros em desenvolvimento
RUN touch /app/.env

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
