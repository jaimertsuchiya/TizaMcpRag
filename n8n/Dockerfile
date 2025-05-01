FROM n8nio/n8n

# Instala o community node do MCP
USER root

# Instala dependências necessárias
RUN apk add --no-cache git python3 py3-pip make g++ icu-libs py3-requests

# Cria diretórios necessários
RUN mkdir -p /home/node/.n8n/custom && \
    mkdir -p /usr/local/bin/mcp-client && \
    mkdir -p /tmp/mcp-client-logs && \
    chown -R node:node /home/node/.n8n && \
    chmod 750 /home/node/.n8n

# Instala o n8n-nodes-mcp no diretório de custom nodes
WORKDIR /home/node/.n8n/custom
RUN npm init -y && \
    npm install n8n-nodes-mcp@latest && \
    npm cache clean --force && \
    chown -R node:node /home/node/.n8n/custom && \
    mkdir -p node_modules

# Copia os arquivos do wrapper MCP
COPY wrapper_mcp/dist/mcp_wrapper /usr/local/bin/mcp-client/mcp_wrapper
COPY wrapper_mcp/mcp_wrapper.py /usr/local/bin/mcp-client/mcp_wrapper.py

# Configura permissões do wrapper MCP
RUN chmod +x /usr/local/bin/mcp-client/mcp_wrapper && \
    chown -R node:node /usr/local/bin/mcp-client && \
    chown -R node:node /tmp/mcp-client-logs && \
    chmod 755 /usr/local/bin/mcp-client && \
    chmod 755 /tmp/mcp-client-logs

# Volta para o usuário node e diretório padrão
USER node
WORKDIR /data

# Define variáveis de ambiente para carregar custom nodes
ENV N8N_CUSTOM_EXTENSIONS="n8n-nodes-mcp"
ENV NODE_PATH="/home/node/.n8n/custom/node_modules"
