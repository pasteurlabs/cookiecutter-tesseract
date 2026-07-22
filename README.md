# cookiecutter-tesseract

[Tesseract Core](https://github.com/pasteurlabs/tesseract-core) &nbsp;|&nbsp; [Docs](https://docs.pasteurlabs.ai/projects/tesseract-core/latest/) &nbsp;|&nbsp; [Forum](https://si-tesseract.discourse.group/) &nbsp;|&nbsp; [Issues](https://github.com/pasteurlabs/cookiecutter-tesseract/issues) &nbsp;|&nbsp; [Contribute](CONTRIBUTING.md)

A [cookiecutter](https://cookiecutter.readthedocs.io) template for **multi-Tesseract projects**. Provides a monorepo that combines several [Tesseracts](https://github.com/pasteurlabs/tesseract-core) into a pipeline application, with shared code, tests, and CI wired up from the start.

**Use this if** you're building an application out of more than one Tesseract and want a batteries-included layout instead of hand-rolling one. Building a single Tesseract? Use `tesseract init` from Tesseract Core instead.

New to Tesseract? Start with the [Tesseract Core docs](https://docs.pasteurlabs.ai/projects/tesseract-core/latest/).

## Features

- **Monorepo layout** — components (Tesseracts), shared code, and the pipeline app live in one repo with a standardized directory structure.
- **`make` workflow** — `make new`, `build`, `test`, `data`, and `run` wrap the common Tesseract commands so you don't memorize them.
- **Component scaffolding** — `make new <name> [RECIPE=base|jax|pytorch]` spins up a Tesseract, wired to depend on the shared code package.
- **Shared code package** — a place for utilities every Tesseract can import, installed automatically into each component.
- **Regression testing** — JSON test cases per component (`test_cases/*.json`) plus a `pytest` suite for the app, all runnable via `make test`.
- **CI/CD** — GitHub Actions that build components and run the full test suite, plus a pre-commit check.
- **Pre-commit + Ruff** — formatting, linting, and hygiene hooks configured out of the box (isolated from private registries).
- **Example notebook** — `app/chain.ipynb` for running Tesseracts and plotting outputs interactively.
- **License choice** — pick Apache-2.0, MIT, BSD-3-Clause, or Proprietary at generation time.

### Features that are safe to opt out of

Once generated, none of these are load-bearing, so you can drop what you don't need:

- **Pre-commit / Ruff** — delete `.pre-commit-config.yaml` and `ruff.toml`.
- **CI** — remove `.github/workflows/`.
- **Example notebook & app** — delete `app/chain.ipynb`, or the whole `app/` dir if you only ship components.
- **Shared code** — remove `components/shared_code` and drop its line from each `tesseract_requirements.txt`.

## Usage

**Prerequisites:** [Tesseract Core](https://github.com/pasteurlabs/tesseract-core) and a running Docker daemon (Tesseract builds and runs components as containers).

**Platforms:** Linux and macOS are supported. On Windows, use [WSL2](https://learn.microsoft.com/windows/wsl/). The generated `make` workflow assumes a POSIX shell.

Generate a project from the template:

```bash
# Install dependencies (if you haven't already).
# With uv (recommended):
$ uv tool install cookiecutter
$ uv tool install pre-commit
# ...or with pip:
$ pip install cookiecutter pre-commit

# You also need tesseract-core to build and run components.
# (Heads up: the `tesseract` command from Tesseract OCR is an unrelated tool.)
$ uv tool install tesseract-core   # or: pip install tesseract-core

# Spawn a new project that uses this template (gh: is shorthand for github:)
$ cookiecutter gh:pasteurlabs/cookiecutter-tesseract

# Move into the generated project directory
$ cd <your-project-name>

# Install pre-commit hooks
$ cd <your-project> && pre-commit install
```

Then, from inside the generated project:

```bash
# Create a new Tesseract component
$ make new mytess

# Create a component from a recipe (base | jax | pytorch)
$ make new mytess RECIPE=jax

# Build all components
$ make build

# Build a single Tesseract
$ make build mytess

# Test all components + app
$ make test

# Test a single component
$ make test mytess

# Capture a regression test case by running an input payload
$ make gen-tests mytess FILE=payload.json

# Test app only
$ make test app

# Run app end-to-end
$ make run
```

## Project structure

<!-- NOTE: When making changes below, make sure to also update `{{ cookiecutter.package_name }}/README.md` -->

```bash
.
# 🚀 CI / CD
├── .github
│   └── workflows                    # CI/CD workflows
│       ├── pre_commit.yml           # Pre-commit hook checks
│       └── test.yaml                # Build components + run all tests (components & app)
# ✅ Code checks
├── .pre-commit-config.yaml          # Pre-commit configuration
├── ruff.toml                        # Ruff linter configuration
# 🔧 Pipeline code
├── app
│   ├── chain.ipynb                  # Notebook for running tesseracts and plotting outputs
│   ├── pyproject.toml               # App package configuration
│   ├── requirements.txt             # App runtime dependencies
│   ├── <myproject>                  # Main Python package
│   │   ├── __init__.py              # Package initialization
│   │   └── main.py                  # CLI entrypoint with typer
│   └── tests                        # App test suite
│       └── test_main.py             # Example test file
# 🧩 Component code
├── components                       # Tesseract components
│   ├── shared_code                  # Shared utilities across Tesseracts
│   │   ├── pyproject.toml           # Shared code package configuration
│   │   └── <myproject>_shared       # Shared code package
│   └── tesseracts                   # Individual tesseract implementations
│       └── <mytess>                 # Tesseract component, created via `make new`
│           ├── tesseract_api.py     # Tesseract API implementation
│           ├── tesseract_config.yaml # Tesseract configuration
│           ├── tesseract_requirements.txt # Tesseract dependencies
│           └── test_cases           # Regression test cases (*.json) for tesseract
# 📊 Data assets
├── data                             # Data assets directory
│   └── get_data.sh                  # Script to download/fetch data
# 🛠️ Scripts
├── scripts                          # Helper scripts
│   └── gen_test_case.py             # Capture a test case from a payload (used by `make gen-tests`)
# 📁 Auxiliary files
├── LICENSE                          # Project license
├── Makefile                         # Build automation (new, build, test, gen-tests, data, run)
└── README.md                        # Project documentation
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) to get started,
and please note our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This template is licensed under the [Apache License 2.0](LICENSE). Generated
projects pick their own license (Apache-2.0, MIT, BSD-3-Clause, or Proprietary)
at generation time.
