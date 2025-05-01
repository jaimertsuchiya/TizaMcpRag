using System;
using System.IO;

namespace McpClient.ConsoleApp
{
    public static class FileLogger
    {
        private static readonly string logPath = "/tmp/mcp_client_log.txt";

        public static void Log(string message)
        {
            try
            {
                using (var writer = File.AppendText(logPath))
                {
                    writer.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - {message}");
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Erro ao gravar log em arquivo: " + ex.ToString());
            }
        }
    }
}