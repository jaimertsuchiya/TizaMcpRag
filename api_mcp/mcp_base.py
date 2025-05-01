
import pymssql
import os

class MCP_Base:
    def executar_procedure(self, nome_proc, parametros):
        server = os.getenv("SQLSERVER_HOST")
        user = os.getenv("SQLSERVER_USER")
        password = os.getenv("SQLSERVER_PASSWORD")
        database = os.getenv("SQLSERVER_DATABASE")
        port = os.getenv("SQLSERVER_PORT", "1433")

        conn = pymssql.connect(server=server, user=user, password=password, database=database, port=int(port))
        cursor = conn.cursor(as_dict=True)

        placeholders = ', '.join([f"@{k} = %s" for k in parametros.keys()])
        sql = f"EXEC {nome_proc} {placeholders}"
        values = list(parametros.values())

        cursor.execute(sql, values)
        result = cursor.fetchall()

        conn.close()

        return result
