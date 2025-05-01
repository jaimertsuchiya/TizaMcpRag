import subprocess
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_MODELS = [
    "nomic-embed-text",  # Para embeddings dos documentos
    "gemma3:latest",    # Para geração de respostas da API RAG
    "mistral"           # Para o agente de chat no n8n (requer suporte a tools)
]

def wait_for_ollama():
    """Espera o Ollama ficar disponível"""
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get("http://ollama:11434/api/tags")
            if response.status_code == 200:
                return True
        except:
            pass
        logger.info("Aguardando Ollama iniciar...")
        time.sleep(2)
        attempt += 1
    return False

def pull_models():
    """Baixa os modelos necessários"""
    for model in REQUIRED_MODELS:
        logger.info(f"Verificando modelo {model}...")
        try:
            # Verifica se o modelo já existe
            response = requests.get(f"http://ollama:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if any(m["name"] == model for m in models):
                    logger.info(f"Modelo {model} já instalado")
                    continue
            
            # Baixa o modelo via API
            logger.info(f"Baixando modelo {model}...")
            response = requests.post("http://ollama:11434/api/pull", json={"name": model})
            if response.status_code == 200:
                logger.info(f"Modelo {model} instalado com sucesso")
            else:
                raise Exception(f"Erro ao baixar modelo: {response.text}")
        except Exception as e:
            logger.error(f"Erro ao instalar modelo {model}: {str(e)}")
            raise

def main():
    logger.info("Iniciando verificação de modelos Ollama...")
    
    if not wait_for_ollama():
        logger.error("Ollama não respondeu após várias tentativas")
        return
    
    pull_models()
    logger.info("Todos os modelos necessários estão instalados")

if __name__ == "__main__":
    main()
