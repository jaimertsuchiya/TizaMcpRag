from dotenv import load_dotenv
import os
import logging

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('load_env')

# Caminhos possíveis para o arquivo .env
possible_paths = [
    '/app/.env',              # Caminho montado como volume no container
    './.env',                 # Diretório atual
    '../.env',                # Diretório pai
]

# Tenta carregar o arquivo .env de um dos caminhos possíveis
env_loaded = False
for path in possible_paths:
    if os.path.exists(path):
        logger.info(f"Arquivo .env encontrado em: {path}")
        load_dotenv(path)
        env_loaded = True
        break
    else:
        logger.info(f"Arquivo .env não encontrado em: {path}")

# Se não encontrou em nenhum lugar, usa as variáveis de ambiente já definidas
if not env_loaded:
    logger.info("Nenhum arquivo .env encontrado. Usando variáveis de ambiente já definidas no sistema/container")
    
# Verifica se as variáveis essenciais estão definidas
required_vars = ['SQLSERVER_HOST', 'SQLSERVER_USER', 'SQLSERVER_PASSWORD', 'SQLSERVER_DATABASE']
for var in required_vars:
    value = os.getenv(var)
    if value:
        logger.info(f"Variável {var} está definida")
    else:
        logger.warning(f"AVISO: Variável {var} não está definida!")

logger.info("Carregamento de variáveis de ambiente concluído")

