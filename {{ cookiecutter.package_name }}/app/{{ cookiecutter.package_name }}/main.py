"""Main entrypoint for {{ cookiecutter.project_name }} pipeline."""

import typer

app = typer.Typer(name="{{ cookiecutter.package_name }}")


@app.command()
def run() -> None:
    """Run the {{ cookiecutter.project_name }} pipeline."""
    # Chain your Tesseracts here. For example, once you have built a component
    # (`make new <mytess>` then `make build <mytess>`):
    #
    #     from tesseract_core import Tesseract
    #
    #     with Tesseract.from_image("{{ cookiecutter.package_name }}_<mytess>") as tess:
    #         result = tess.apply({"example_input": ...})
    #     typer.echo(result)
    #
    # See app/chain.ipynb for an interactive version.
    typer.echo("Running {{ cookiecutter.project_name }} pipeline...")


def entrypoint() -> None:
    """CLI entrypoint for the application."""
    app()


if __name__ == "__main__":
    entrypoint()
