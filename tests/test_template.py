"""Structural tests for the generated project.

These render the template into a temporary directory and assert invariants that
do not require Docker or the Tesseract daemon: correct rendering, name
propagation, license selection, version pinning, and that the generated app is
a valid, installable Python package whose own test suite passes.

The Docker-dependent end-to-end flow (``make new`` / ``build`` / ``test`` /
``run`` and the recipe matrix) lives in ``test_e2e.py``.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

REPO_ROOT = Path(__file__).resolve().parent.parent


def render(output_dir: Path, **extra_context: str) -> Path:
    """Render the template and return the generated project directory."""
    context = {"project_name": "Demo Project", **extra_context}
    cookiecutter(
        str(REPO_ROOT),
        no_input=True,
        output_dir=str(output_dir),
        extra_context=context,
    )
    # Derive the package name the same way cookiecutter.json does, so tests can
    # locate the project regardless of the name they passed in.
    package = context["project_name"].lower().replace(" ", "_").replace("-", "_")
    project = output_dir / package
    assert project.is_dir(), f"expected generated project at {project}"
    return project


@pytest.fixture(scope="module")
def generated_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Render the template once with defaults and return the project directory."""
    return render(tmp_path_factory.mktemp("rendered"))


def _all_text_files(root: Path) -> list[Path]:
    suffixes = {".py", ".toml", ".md", ".txt", ".yaml", ".yml", ".json", ".sh"}
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes]


def test_no_leftover_placeholders(generated_project: Path) -> None:
    """No unrendered Jinja or template placeholders leak into the output."""
    for path in _all_text_files(generated_project):
        text = path.read_text(encoding="utf-8")
        for marker in ("{{ cookiecutter", "{%", "%TESSERACT_VERSION%", "%LICENSE%"):
            # GitHub Actions expressions ${{ ... }} are intentionally emitted
            # from a {% raw %} block and are not cookiecutter placeholders.
            if marker == "{{ cookiecutter":
                assert "{{ cookiecutter" not in text, f"{path}: {marker}"
            else:
                assert marker not in text, f"{path}: {marker}"


def test_readme_title(generated_project: Path) -> None:
    """The README title renders the project name."""
    first_line = (
        (generated_project / "README.md").read_text(encoding="utf-8").splitlines()[0]
    )
    assert first_line == "# Demo Project"


def test_template_ships_an_example_test_case(generated_project: Path) -> None:
    """`make new` seeds a runnable regression test case."""
    example = (
        generated_project / "components/tesseracts/.template/test_cases/example.json"
    )
    assert example.is_file()


def test_makefile_exposes_all_documented_targets(generated_project: Path) -> None:
    """Every workflow advertised in the README is a real Makefile target."""
    makefile = (generated_project / "Makefile").read_text(encoding="utf-8")
    for target in ("new", "build", "test", "run"):
        assert f"\n{target}:" in makefile, f"Makefile is missing the '{target}' target"


def test_ci_installs_from_app_paths(generated_project: Path) -> None:
    """Component CI installs from the app/ paths that actually exist."""
    ci = (generated_project / ".github/workflows/test.yaml").read_text(encoding="utf-8")
    assert "app/requirements.txt" in ci
    assert 'pip install -e "app[dev]"' in ci


# ---------------------------------------------------------------------------
# Name propagation
#
# ``package_name`` is the single most load-bearing template variable: it names
# the app package, the shared-code package, the installed CLI script, and the
# ``tesseract init --name`` prefix. A slugification regression would break the
# generated project silently, so exercise a name that stresses every rule.
# ---------------------------------------------------------------------------


def test_package_name_propagates_everywhere(tmp_path: Path) -> None:
    """A hostile project name is slugified consistently across the project."""
    project = render(tmp_path, project_name="My-Cool Tess 2")
    package = "my_cool_tess_2"

    # App package and shared-code package directories are named after the package.
    assert (project / "app" / package / "main.py").is_file()
    assert (project / "app" / package / "__init__.py").is_file()
    assert (project / "components" / "shared_code" / f"{package}_shared").is_dir()

    # The installed CLI script and package metadata use the package name.
    pyproject = (project / "app" / "pyproject.toml").read_text(encoding="utf-8")
    assert f'name = "{package}"' in pyproject
    assert f'"{package}" = "{package}.main:entrypoint"' in pyproject

    # `make new` names each component `<package>_<component>` so images are namespaced.
    makefile = (project / "Makefile").read_text(encoding="utf-8")
    assert f"{package}_$$TESS_SLUG" in makefile

    # No stale references to the default/example package name leaked in.
    for path in _all_text_files(project):
        assert "demo_project" not in path.read_text(encoding="utf-8"), (
            f"{path}: stale package name"
        )


# ---------------------------------------------------------------------------
# License selection
# ---------------------------------------------------------------------------

LICENSE_MARKERS = {
    "Apache-2.0": "Apache License",
    "MIT": "MIT License",
    "BSD-3-Clause": "BSD 3-Clause License",
    "Proprietary": "proprietary and confidential",
}


@pytest.mark.parametrize("license_id", sorted(LICENSE_MARKERS))
def test_license_is_rendered(tmp_path: Path, license_id: str) -> None:
    """Each license choice renders concrete text and records the identifier."""
    project = render(tmp_path, license=license_id)

    license_text = (project / "LICENSE").read_text(encoding="utf-8")
    assert "%LICENSE%" not in license_text
    assert LICENSE_MARKERS[license_id] in license_text

    pyproject = (project / "app" / "pyproject.toml").read_text(encoding="utf-8")
    assert f'license = "{license_id}"' in pyproject


# ---------------------------------------------------------------------------
# Tesseract version pinning
# ---------------------------------------------------------------------------


def test_requirements_pin_installed_tesseract_version(generated_project: Path) -> None:
    """The post-gen hook pins the installed tesseract-core version."""
    tesseract_core = pytest.importorskip("tesseract_core")
    requirements = (generated_project / "app" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    assert f"tesseract-core=={tesseract_core.__version__}" in requirements


# ---------------------------------------------------------------------------
# The generated app is a valid, installable package
#
# This is the strongest signal available without Docker: install the app into
# an isolated virtualenv and run its own pytest suite. It exercises the
# pyproject metadata, the package layout, imports, and the typer CLI end to end.
# ---------------------------------------------------------------------------


def test_generated_app_installs_and_its_tests_pass(
    generated_project: Path, tmp_path: Path
) -> None:
    """`pip install -e app[dev]` succeeds and `pytest app` passes."""
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    py = venv / ("Scripts" if os.name == "nt" else "bin") / "python"

    app_dir = generated_project / "app"
    subprocess.run(
        [str(py), "-m", "pip", "install", "-q", "-e", f"{app_dir}[dev]"],
        check=True,
    )
    subprocess.run([str(py), "-m", "pytest", str(app_dir), "-q"], check=True)
