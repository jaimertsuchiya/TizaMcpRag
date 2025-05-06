# Carregar variáveis de ambiente primeiro
import sys
import os
from pathlib import Path

# Adiciona o diretório atual ao path para importar load_env
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Importa e executa o carregamento das variáveis de ambiente
import load_env

from fastapi import FastAPI, HTTPException
from models import ExecuteRequest, AuthRequest
import importlib

app = FastAPI()

# Definindo os schemas das tools
TOOL_SCHEMAS = {
    "ConsultarBeneficiosAtivas": {
        "name": "ConsultarBeneficiosAtivas",
        "description": "Consulta os benefícios ativos de um cliente no sistema de benefícios, retornando todos os dados disponíveis para o ambiente e usuário informados.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoAmbiente": {"type": "integer", "description": "Código do ambiente do cliente."},
                "codigoUsuario": {"type": "integer", "description": "Código do usuário solicitante."}
            },
            "required": ["codigoAmbiente", "codigoUsuario"]
        }
    },
    "BeneficiariosBeneficio": {
        "name": "BeneficiariosBeneficio",
        "description": "Obtém a lista de beneficiários de um benefício ativa de um ambiente do sistema de benefícios.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoBeneficio": {"type": "integer", "description": "Código do benefício do usuário solicitante."}
            },
            "required": ["codigoBeneficio"]
        }
    },
    "ObterSolicitacoesPendentes": {
        "name": "ObterSolicitacoesPendentes",
        "description": "Obtém as solicitacoes pendentes do usuario.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoUsuario": {"type": "integer", "description": "Código do usuario solicitante."}
            },
            "required": ["codigoUsuario"]
        }
    },
    "SaldoDisponivelReembolso": {
        "name": "SaldoDisponivelReembolso",
        "description": "Obtém o saldo disponivel do usuario para reembolso no periodo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoUsuario": {"type": "integer", "description": "Código do usuario solicitante."}
            },
            "required": ["codigoUsuario"]
        }
    },
    "MeusDependentes": {
        "name": "MeusDependentes",
        "description": "Obtém os dependentes cadastrados do usuario.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoUsuario": {"type": "integer", "description": "Código do usuario solicitante."}
            },
            "required": ["codigoUsuario"]
        }
    },
    "ProgramaBeneficios": {
        "name": "ProgramaBeneficios",
        "description": "Obtém informações sobre o programa de benefícios",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codigoUsuario": {"type": "integer", "description": "Código do usuario solicitante."},
                "pergunta": {"type": "string", "description": "Pergunta sobre o programa de benefícios"}
            },
            "required": ["codigoUsuario"]
        }
    }
}

# Registrando as tools
TOOLS = {
    "ConsultarBeneficiosAtivas": "mcp_tools.ConsultarBeneficiosAtivas",
    "BeneficiariosBeneficio": "mcp_tools.BeneficiariosBeneficio",
    "MeusDependentes": "mcp_tools.MeusDependentes",
    "SaldoDisponivelReembolso": "mcp_tools.SaldoDisponivelReembolso",
    "ObterSolicitacoesPendentes": "mcp_tools.ObterSolicitacoesPendentes",
    "ProgramaBeneficios": "mcp_tools.ProgramaBeneficios"
}

@app.post("/mcp/auth")
def authenticate(request: AuthRequest):
    if request.username == "admin" and request.password == "admin":
        return {"token": "fake-token"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/mcp/tools")
def list_tools():
    return list(TOOLS.keys())

@app.get("/mcp/tools/schema")
def get_tools_schema():
    return list(TOOL_SCHEMAS.values())

@app.post("/mcp/tools/{tool_name}/execute")
def execute_tool(tool_name: str, request: ExecuteRequest):
    if tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail="Tool not found")
    module_path = TOOLS[tool_name]
    module = importlib.import_module(module_path)
    tool_class = getattr(module, tool_name)
    tool_instance = tool_class()
    try:
        result = tool_instance.execute(request.parametros)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
