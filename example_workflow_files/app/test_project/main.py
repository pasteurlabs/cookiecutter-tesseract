import numpy as np
import typer
from tesseract_core import Tesseract

app = typer.Typer(name="test_project")
tess = Tesseract.from_image("test_project_scaler")


@app.command()
def run() -> None:
    """Run the Test Project pipeline."""
    typer.echo("Running Test Project pipeline...")
    testinput = {"vector": np.array([1, 2, 3]), "scale_factor": 2.0}
    with tess:
        res = tess.apply(testinput)
    typer.echo(res)


def entrypoint() -> None:
    """CLI entrypoint for the application."""
    app()


if __name__ == "__main__":
    entrypoint()
