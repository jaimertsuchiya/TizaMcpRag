
import pymssql
import os
import logging

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_base')

class MCP_Base:
    def executar_procedure(self, nome_proc, parametros):
        try:
            # Obter as variáveis de ambiente para conexão com o banco de dados
            server = os.getenv("SQLSERVER_HOST")
            user = os.getenv("SQLSERVER_USER")
            password = os.getenv("SQLSERVER_PASSWORD")
            database = os.getenv("SQLSERVER_DATABASE")
            port = os.getenv("SQLSERVER_PORT", "1433")
            
            # Logar informações de conexão (sem a senha)
            logger.info(f"Conectando ao banco de dados: {server}:{port}, database={database}, user={user}")
            
            # Tentar estabelecer a conexão com o banco de dados
            try:
                # Adicionando charset='utf8' para resolver problemas de codificação de caracteres
                conn = pymssql.connect(server=server, user=user, password=password, database=database, port=int(port), charset='utf8')
                logger.info("Conexão com o banco de dados estabelecida com sucesso")
            except Exception as e:
                logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
                raise
            
            cursor = conn.cursor(as_dict=True)
            
            # Construir a consulta SQL
            placeholders = ', '.join([f"@{k} = %s" for k in parametros.keys()])
            sql = f"EXEC {nome_proc} {placeholders}"
            values = list(parametros.values())
            
            logger.info(f"Executando procedure: {nome_proc} com parâmetros: {parametros}")
            
            # Executar a consulta
            try:
                cursor.execute(sql, values)
                result = cursor.fetchall()
                logger.info(f"Procedure {nome_proc} executada com sucesso. Retornando {len(result)} registros")
            except Exception as e:
                logger.error(f"Erro ao executar procedure {nome_proc}: {str(e)}")
                raise
            finally:
                conn.close()
                logger.info("Conexão com o banco de dados fechada")
            
            return result
        except Exception as e:
            logger.error(f"Erro geral na execução da procedure {nome_proc}: {str(e)}")
            raise
