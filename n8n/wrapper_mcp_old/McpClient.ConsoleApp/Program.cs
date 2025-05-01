using System;
using System.IO;
using System.Linq.Expressions;
using System.Net.Http;
using System.Text.Json;

namespace McpClient.ConsoleApp
{
    class Program
    {
        static readonly HttpClient httpClient = new HttpClient();
        static readonly string baseUrl = Environment.GetEnvironmentVariable("MCP_BASE_URL") ?? "http://192.168.68.110/mcp";

        static void Main(string[] args)
        {
            string line;
            while ((line = Console.ReadLine()) != null)
            {
                try
                {
                    FileLogger.Log("Entrada recebida: " + line);
                    var input = JsonSerializer.Deserialize<JsonElement>(line);

                    if (input.TryGetProperty("method", out var method))
                    {
                        if (!input.TryGetProperty("id", out var idElement))
                        {
                            switch (method.GetString())
                            {
                                case "notifications/initialized":
                                    FileLogger.Log("Notificação: Servidor inicializado.");
                                    break;

                                case "notifications/cancelled":
                                    FileLogger.Log("Notificação: Operação cancelada.");
                                    break;

                                default:
                                    FileLogger.Log("Notificação desconhecida: " + method.GetString());
                                    break;
                            }
                            continue;  // notificação tratada, segue o loop
                        }

                        var id = input.GetProperty("id").GetInt32();

                        switch (method.GetString())
                        {
                            case "initialize":
                                Respond(id, new
                                {
                                    protocolVersion = "2024-11-05",
                                    capabilities = new { prompts = new { }, resources = new { }, tools = new { } },
                                    serverInfo = new { name = "McpClient-Server", version = "1.0.0" }
                                });
                                break;

                            case "tools/list":
                                var toolsJson = httpClient.GetStringAsync($"{baseUrl}/tools").Result;
                                var toolsList = JsonSerializer.Deserialize<JsonElement>(toolsJson);

                                // Ajustar estrutura para ter inputSchema no lugar de parameters
                                var toolsListAdjusted = toolsList.EnumerateArray().Select(tool => new
                                {
                                    name = tool.GetProperty("name").GetString(),
                                    description = tool.GetProperty("description").GetString(),
                                    inputSchema = tool.GetProperty("parameters")
                                }).ToList();

                                // Retornar no padrão correto exigido pelo n8n
                                Respond(id, new { tools = toolsListAdjusted });

                                // Notificação adicional APENAS aqui
                                var notification = new
                                {
                                    jsonrpc = "2.0",
                                    method = "notifications/toolsListUpdated",
                                    @params = new
                                    {
                                        tools = toolsList.EnumerateArray().Select(tool => tool.GetProperty("name").GetString())
                                    }
                                };
                                var notificationJson = JsonSerializer.Serialize(notification);
                                Console.WriteLine(notificationJson);
                                FileLogger.Log("Notificação enviada (toolsListUpdated): " + notificationJson);
                                break;

                            case "tools/call":
                                var toolName = input.GetProperty("params").GetProperty("name").GetString();
                                var parametros = input.GetProperty("params").GetProperty("arguments").ToString();
                                var response = httpClient.PostAsync($"{baseUrl}/tools/{toolName}/execute", new StringContent(parametros, System.Text.Encoding.UTF8, "application/json")).Result;

                                var contentJson = response.Content.ReadAsStringAsync().Result;

                                // Faz o ajuste do retorno
                                var dadosRetornados = JsonSerializer.Deserialize<JsonElement>(contentJson);

                                // Monta o payload no formato que o n8n espera
                                var payload = new
                                {
                                    content = dadosRetornados.GetProperty("resultado").EnumerateArray().ToList()
                                };

                                // Retorna
                                Respond(id, payload);
                                break;

                            case "shutdown":
                                FileLogger.Log("Shutdown solicitado.");
                                Respond(id, new { message = "Servidor encerrado com sucesso." });
                                return;

                            case "listResources":
                                Respond(id, new[] { "resource1", "resource2" });
                                break;

                            case "readResource":
                                var resourceId = input.GetProperty("params").GetProperty("id").GetString();
                                Respond(id, new { id = resourceId, content = "Conteúdo do recurso." });
                                break;

                            case "listPrompts":
                                Respond(id, new[] { "prompt1", "prompt2" });
                                break;

                            case "getPrompt":
                                var promptId = input.GetProperty("params").GetProperty("id").GetString();
                                Respond(id, new { id = promptId, prompt = "Texto do prompt solicitado." });
                                break;

                            default:
                                RespondError(id, "Método não encontrado.");
                                break;
                        }
                    }   
                }
                catch (Exception ex)
                {
                    FileLogger.Log("ERRO EXECUCAO: " + ex.Message);
                }
            }
        }

        static void Respond(int id, object result)
        {
            var response = new { jsonrpc = "2.0", id, result };
            var json = JsonSerializer.Serialize(response);
            Console.WriteLine(json);
            FileLogger.Log("Resposta enviada: " + json);
        }

        static void RespondError(int id, string errorMessage)
        {
            var response = new { jsonrpc = "2.0", id, error = new { message = errorMessage } };
            var json = JsonSerializer.Serialize(response);
            Console.WriteLine(json);
            FileLogger.Log("Erro enviado: " + json);
        }
    }
}