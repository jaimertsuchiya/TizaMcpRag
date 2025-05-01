#!/usr/bin/env python3

import sys
import json
import requests
import os
import logging

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://172.21.0.2:8000")

# Headers para todas as requisições
HEADERS = {"Content-Type": "application/json"}

def send_response(id, result):
    response = {
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    }
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
    logging.debug(f"Resposta enviada: {json.dumps(response)}")

def send_error(id, error_message):
    response = {
        "jsonrpc": "2.0",
        "id": id,
        "error": {
            "message": error_message
        }
    }
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
    logging.debug(f"Erro enviado: {json.dumps(response)}")

def handle_initialize():
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "prompts": {},
            "resources": {},
            "tools": {}
        },
        "serverInfo": {
            "name": "McpClient-Server",
            "version": "1.0.0"
        }
    }

def handle_list_tools():
    logging.debug("Listando ferramentas...")
    try:
        response = requests.get(f"{MCP_SERVER_URL}/mcp/tools", headers=HEADERS)
        logging.debug(f"Status: {response.status_code}")
        logging.debug(f"Response: {response.text}")
        response.raise_for_status()
        tools = response.json()

        # Ajustar estrutura para ter inputSchema para cada ferramenta
        tools_list_adjusted = [{
            "name": tool,
            "description": f"Executa a operação {tool}",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        } for tool in tools]

        result = {"tools": tools_list_adjusted}

        # Enviar notificação adicional
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/toolsListUpdated",
            "params": {
                "tools": [tool["name"] for tool in tools_list_adjusted]
            }
        }
        sys.stdout.write(json.dumps(notification) + "\n")
        sys.stdout.flush()
        logging.debug(f"Notificação enviada (toolsListUpdated): {json.dumps(notification)}")

        return result

    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        raise

def handle_execute_tool(params):
    logging.debug("Executando ferramenta...")
    logging.debug(f"Params: {params}")
    
    tool_name = params["name"]
    arguments = params.get("arguments", {})
    
    # Encapsula os argumentos em "parametros" conforme esperado pela API
    payload = {"parametros": arguments}
    
    logging.debug(f"URL: {MCP_SERVER_URL}/mcp/tools/{tool_name}/execute")
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/{tool_name}/execute", 
            json=payload,
            headers=HEADERS
        )
        logging.debug(f"Status: {response.status_code}")
        logging.debug(f"Response: {response.text}")
        response.raise_for_status()
        
        result = response.json()
        logging.debug(f"Result: {result}")
        
        # Extrai os dados da resposta e garante que seja uma lista
        dados = result.get("data", [])
        if not isinstance(dados, list):
            dados = [dados] if dados else []
            
        return {"content": dados}
        
    except Exception as e:
        logging.error(f"Erro na execução: {str(e)}")
        raise

def main():
    # Configurar logging
    logging.basicConfig(
        filename='/tmp/mcp-client-logs/wrapper.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.debug("Wrapper iniciando...")
    logging.debug(f"MCP_SERVER_URL={MCP_SERVER_URL}")
    logging.debug("HEADERS={}".format(HEADERS))
    
    while True:
        try:
            logging.debug("Aguardando entrada...")
            line = sys.stdin.readline()
            if not line:
                logging.debug("Entrada vazia, finalizando...")
                break
                
            logging.debug(f"Recebido: {line}")
            message = json.loads(line)

            method = message.get("method")
            params = message.get("params", {})
            msg_id = message.get("id")

            # Se não tem ID, é uma notificação
            if msg_id is None:
                if method == "notifications/initialized":
                    logging.debug("Notificação: Servidor inicializado.")
                elif method == "notifications/cancelled":
                    logging.debug("Notificação: Operação cancelada.")
                else:
                    logging.debug(f"Notificação desconhecida: {method}")
                continue

            logging.debug(f"Método: {method}")
            logging.debug(f"Parâmetros: {params}")
            logging.debug(f"ID: {msg_id}")

            try:
                if method == "initialize":
                    response = handle_initialize()
                    send_response(msg_id, response)
                    
                elif method == "tools/list":
                    response = handle_list_tools()
                    send_response(msg_id, response)
                    
                elif method == "tools/call":
                    response = handle_execute_tool(params)
                    send_response(msg_id, response)
                    
                elif method == "shutdown":
                    send_response(msg_id, {"message": "Servidor encerrado com sucesso."})
                    break
                    
                elif method == "listResources":
                    send_response(msg_id, ["resource1", "resource2"])
                    
                elif method == "readResource":
                    resource_id = params["id"]
                    send_response(msg_id, {"id": resource_id, "content": "Conteúdo do recurso."})
                    
                elif method == "listPrompts":
                    send_response(msg_id, ["prompt1", "prompt2"])
                    
                elif method == "getPrompt":
                    prompt_id = params["id"]
                    send_response(msg_id, {"id": prompt_id, "prompt": "Texto do prompt solicitado."})
                    
                else:
                    send_error(msg_id, "Método não encontrado.")
                    
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Erro ao processar mensagem: {error_msg}")
                send_error(msg_id, error_msg)
                
        except Exception as e:
            logging.error(f"Erro no loop principal: {str(e)}")

if __name__ == "__main__":
    main()
