
from mcp_base import MCP_Base
import requests

class MeusDependentes(MCP_Base):
    def execute(self, parametros):
        # Exemplo de como executar uma procedure
        return self.executar_procedure('interface.MeusDependentes', parametros)
