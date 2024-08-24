from rich import pretty
import typer
from typing import Annotated
from xmlrpc.server import SimpleXMLRPCServer

from semdoc.xmlrpc import server_dispatch

app = typer.Typer()


@app.command()
def run(
    host: Annotated[str, typer.Option()] = "localhost",
    port: Annotated[int, typer.Option()] = 8000,
    ctx: typer.Context = None,
):
    if ctx:
        import semdoc.analyzer.surya

    with SimpleXMLRPCServer((host, port)) as server:
        server.register_function(server_dispatch, "dispatch")
        server.serve_forever()
