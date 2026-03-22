import typer
from rich.console import Console

app = typer.Typer(
    name="statma",
    help="stat your agent.",
    no_args_is_help=True,
)

console = Console()


@app.command()
def run(
    target: str = typer.Option(..., help="Target to benchmark. e.g. ollama:llama3.1:8b or http://localhost:7341"),
    only: str = typer.Option(None, help="Run a single dimension only."),
    save_as: str = typer.Option(None, help="Save result as a named baseline."),
    compare_to: str = typer.Option(None, help="Compare against a saved baseline."),
):
    """Score an agent or model across four behavioural dimensions."""
    console.print(f"[bold]statma[/bold] · target: {target}")
    console.print("[yellow]not implemented yet[/yellow]")


@app.command()
def serve(
    entrypoint: str = typer.Argument(..., help="Path to your agent Python file."),
    port: int = typer.Option(7341, help="Port to serve on."),
    fn: str = typer.Option(None, help="Entry function name if not auto-detected."),
):
    """Wrap a local agent file and serve it on localhost."""
    console.print(f"[bold]statma serve[/bold] · {entrypoint} → http://localhost:{port}")
    console.print("[yellow]not implemented yet[/yellow]")


@app.command()
def matrix(
    target: str = typer.Option(..., help="Agent target to benchmark against."),
    models: list[str] = typer.Option(..., help="Models to compare."),
):
    """Run the same agent against multiple models and rank them."""
    console.print(f"[bold]statma matrix[/bold] · {len(models)} models")
    console.print("[yellow]not implemented yet[/yellow]")


@app.command()
def compare(
    baseline: str = typer.Option(..., help="Baseline target."),
    target: str = typer.Option(..., help="Target to compare against baseline."),
):
    """Compare a raw model against an agent wrapper."""
    console.print(f"[bold]statma compare[/bold] · {baseline} vs {target}")
    console.print("[yellow]not implemented yet[/yellow]")


@app.command()
def suite(
    action: str = typer.Argument(..., help="list | run-case | add | validate"),
    dimension: str = typer.Option(None, help="Dimension to operate on."),
    file: str = typer.Option(None, help="YAML file for add/validate."),
    id: str = typer.Option(None, help="Case ID for run-case."),
):
    """Manage the test suite."""
    console.print(f"[bold]statma suite[/bold] · {action}")
    console.print("[yellow]not implemented yet[/yellow]")


if __name__ == "__main__":
    app()
