from mcp_base import MCP_Base
import requests

class SaldoDisponivelReembolso(MCP_Base):
    def execute(self, parametros):
        # Extrair apenas o codigoUsuario
        if not parametros.get('codigoUsuario'):
            raise ValueError("Parâmetro 'codigoUsuario' é obrigatório")
            
        params_proc = {
            'codigoUsuario': parametros['codigoUsuario']
        }
        
        # Executar a procedure apenas com o codigoUsuario
        return self.executar_procedure('interface.SaldoDisponivelReembolso', params_proc)
