
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar curl para healthcheck
RUN apt-get update && \
    apt-get install -y curl

# Copiar arquivos
COPY . .

# Dar permissão de execução ao script de inicialização
RUN chmod +x start.sh

# Usar o script de inicialização
CMD ["/app/start.sh"]
