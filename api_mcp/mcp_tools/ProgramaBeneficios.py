
import requests
import logging

class ProgramaBeneficios:
    def execute(self, parametros):
        # Configurar logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        
        # Validar parâmetros obrigatórios
        if not parametros.get("codigoUsuario"):
            logger.error("Parâmetro 'codigoUsuario' não fornecido")
            raise ValueError("Parâmetro 'codigoUsuario' é obrigatório")

        # Obter a pergunta (opcional conforme schema)
        message = parametros.get("pergunta", "")
        if not message:
            logger.warning("Nenhuma pergunta fornecida, usando mensagem vazia")

        # Preparar payload para a API RAG
        payload = {
            "workspaceId": "tiza",
            "pergunta": message,
            "chatHistory": [],
            "metadata": {
                "codigoUsuario": parametros["codigoUsuario"]
            }
        }
        
        logger.debug(f"Enviando requisição para API RAG: {payload}")

        # Chamar a API RAG
        try:
            response = requests.post(
                "http://tizamcprag-api-rag:8000/ask",
                json=payload,
                timeout=120  # Timeout de 120 segundos
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"Resposta da API RAG: {result}")

            if not result.get("resposta"):
                logger.warning("API RAG retornou resposta sem campo 'resposta'")
                return [{
                    "type": "text",
                    "text": "Desculpe, não consegui processar sua pergunta."
                }]

            # Formatar a resposta como texto
            return [{
                "type": "text",
                "text": result["resposta"]
            }]

        except requests.exceptions.Timeout:
            logger.error("Timeout ao comunicar com a API RAG")
            raise ValueError("Timeout ao comunicar com a API RAG. Por favor, tente novamente.")
            
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com a API RAG")
            raise ValueError("Não foi possível conectar à API RAG. Verifique se o serviço está disponível.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao comunicar com a API RAG: {str(e)}")
            raise ValueError(f"Erro ao comunicar com a API RAG: {str(e)}")
