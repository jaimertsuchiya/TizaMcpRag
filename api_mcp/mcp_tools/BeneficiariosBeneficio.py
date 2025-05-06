
from mcp_base import MCP_Base
import logging

logger = logging.getLogger('BeneficiariosBeneficio')

class BeneficiariosBeneficio(MCP_Base):
    def execute(self, parametros):
        # Executar a procedure e obter os resultados
        results = self.executar_procedure('interface.ObterBeneficiariosPorCobertura', parametros)
        
        # Logar os resultados para debug
        logger.info(f"Resultados da procedure: {results}")
        
        # Se não houver resultados, retornar uma mensagem amigável
        if not results:
            return [{"type": "text", "text": "Nenhum beneficiário encontrado para os parâmetros informados."}]
        
        # Como os resultados já estão formatados corretamente, retornar diretamente
        return results
