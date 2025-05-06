# Wrapper MCP

Este diretório contém o wrapper Python que serve como interface entre o n8n e a API MCP.

## Estrutura

- `mcp_wrapper.py`: O script principal do wrapper que processa as requisições do n8n e as encaminha para a API MCP.
- `requirements.txt`: Lista de dependências Python necessárias para o wrapper.
- `build/` e `dist/`: Diretórios gerados durante o processo de build (podem ser ignorados).

## Implantação

O wrapper é copiado para o container n8n durante o build da imagem Docker, conforme definido no arquivo `n8n/Dockerfile`. 

Localizações do wrapper no sistema:

1. **Código fonte principal**: `wrapper_mcp/mcp_wrapper.py` (este diretório)
2. **No container n8n**: 
   - `/usr/local/bin/mcp-client/mcp_wrapper.py` (usado pelo n8n)
   - `/home/node/.n8n/wrapper_mcp/mcp_wrapper.py` (cópia de backup)

## Configuração

O wrapper está configurado para se conectar à API MCP usando o nome do serviço Docker:

```python
MCP_SERVER_URL = "http://tizamcprag-api-mcp:8000"
```

Esta configuração garante que o wrapper possa se comunicar corretamente com a API MCP dentro da rede Docker.

## Logs

Os logs do wrapper são armazenados em `/tmp/mcp-client-logs/wrapper.log` no container n8n.
