import requests

session = requests.Session()

# Initialize
resp = session.post(
    "http://127.0.0.1:8000/mcp",
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    }}
)
print("INIT status:", resp.status_code)
print("INIT:", resp.json())

# Tools list - sprawdźmy surową odpowiedź
resp = session.post(
    "http://127.0.0.1:8000/mcp",
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
)
print("TOOLS status:", resp.status_code)
print("TOOLS headers:", resp.headers.get('content-type'))
print("TOOLS text:", repr(resp.text))
print("TOOLS content:", resp.content)
