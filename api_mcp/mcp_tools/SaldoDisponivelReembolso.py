from mcp_base import MCP_Base
import logging

logger = logging.getLogger('SaldoDisponivelReembolso')

class SaldoDisponivelReembolso(MCP_Base):
    def execute(self, parametros):
        # Extrair apenas o codigoUsuario
        if not parametros.get('codigoUsuario'):
            logger.error("Parâmetro 'codigoUsuario' não fornecido")
            raise ValueError("Parâmetro 'codigoUsuario' é obrigatório")
            
        params_proc = {
            'codigoUsuario': parametros['codigoUsuario']
        }
        
        # Executar a procedure e obter os resultados
        results = self.executar_procedure('interface.SaldoDisponivelReembolso', params_proc)
        
        # Logar os resultados para debug
        logger.info(f"Resultados da procedure: {results}")
        
        # Se não houver resultados, retornar uma mensagem amigável
        if not results:
            return [{"type": "text", "text": "Nenhum saldo disponível para reembolso encontrado."}]
        
        # Como os resultados já estão formatados corretamente, retornar diretamente
        return results
