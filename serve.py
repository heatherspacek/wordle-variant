from textual_serve.server import Server

server = Server(
    "pypy3 main.py", host="0.0.0.0", public_url="https://dle.heatherspacek.com"
)
server.serve()
