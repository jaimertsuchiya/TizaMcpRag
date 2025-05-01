
import sys
import json
import requests
import os

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://tizamcprag-api-mcp:8000")

def send_response(response):
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

def handle_initialize():
    return {
        "type": "initialize",
        "serverInfo": {
            "name": "TizaMcpRag Server",
            "version": "1.0.0"
        }
    }

def handle_list_tools():
    response = requests.get(f"{MCP_SERVER_URL}/mcp/tools")
    response.raise_for_status()
    tools = response.json()
    return {
        "type": "tools_list",
        "tools": [{"name": tool} for tool in tools]
    }

def handle_execute_tool(content):
    tool = content["tool"]
    inputs = content.get("inputs", {})
    payload = {"parametros": inputs}
    response = requests.post(f"{MCP_SERVER_URL}/mcp/tools/{tool}/execute", json=payload)
    response.raise_for_status()
    result = response.json()
    return {
        "type": "tool_response",
        "output": result.get("data", {})
    }

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        message = json.loads(line)

        msg_type = message.get("type")
        content = message.get("content", {})

        try:
            if msg_type == "initialize":
                send_response(handle_initialize())
            elif msg_type == "tools/list":
                send_response(handle_list_tools())
            elif msg_type == "tools/execute":
                send_response(handle_execute_tool(content))
            elif msg_type == "shutdown":
                send_response({"type": "shutdown"})
                break
            elif msg_type == "notifications/cancelled":
                send_response({"type": "notifications_acknowledged"})
            else:
                send_response({"type": "error", "message": f"Unknown message type: {msg_type}"})
        except Exception as e:
            send_response({"type": "error", "message": str(e)})

if __name__ == "__main__":
    main()
