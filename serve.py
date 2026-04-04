from textual_serve.server import Server

server = Server(
    "uv run --python pypy@3.11 main.py", host="0.0.0.0", public_url="https://dle.heatherspacek.com"
)
server.serve()
