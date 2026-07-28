"""End-to-end tests for the generated project.

These render the template and drive the real user-facing workflow through the
Makefile: ``make new`` / ``build`` / ``test`` / ``run``. They require Docker and
the Tesseract CLI, so they are marked ``e2e`` and skipped automatically when
Docker is unavailable (e.g. local runs without a daemon).

Run just these with::

    pytest tests/test_e2e.py            # or: pytest -m e2e

Skip them (structural tests only) with::

    pytest -m "not e2e"

The scaler test below covers the documented happy path plus the negative case,
with per-step assertions and readable failures, and the recipe matrix
additionally guards the advertised ``--recipe base|jax|pytorch`` scaffolds. The
worked scaler example lives in ``example_workflow_files/``.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_FILES = REPO_ROOT / "example_workflow_files"


def _docker_available() -> bool:
    docker = shutil.which("docker")
    if docker is None or shutil.which("tesseract") is None:
        return False
    return (
        subprocess.run([docker, "info"], capture_output=True, check=False).returncode
        == 0
    )


pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not _docker_available(),
        reason="Docker and the Tesseract CLI are required for end-to-end tests",
    ),
]


def run(
    cmd: list[str] | str, cwd: Path, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a command in ``cwd``, echoing output so failures are legible."""
    shell = isinstance(cmd, str)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check:
        assert result.returncode == 0, f"command failed ({result.returncode}): {cmd}"
    return result


@pytest.fixture(scope="module")
def rendered_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Render the template into a temp dir via the CLI (exercises the real path)."""
    out = tmp_path_factory.mktemp("e2e")
    run(
        [
            "cookiecutter",
            str(REPO_ROOT),
            "-o",
            str(out),
            "--no-input",
            "project_name=Test Project",
        ],
        cwd=out,
    )
    project = out / "test_project"
    assert project.is_dir()
    return project


def test_scaler_pipeline_end_to_end(rendered_project: Path) -> None:
    """The full documented workflow builds, tests, and runs the scaler example.

    Mirrors the worked example: `make new` scaffolds a component, we drop in the
    schema-specific scaler implementation shipped in `example_workflow_files`,
    then build/test/run the whole pipeline including the app.
    """
    project = rendered_project
    run(["make", "new", "scaler"], cwd=project)

    # The base example.json does not match the scaler's schema; replace the
    # generated component + app with the worked example.
    (project / "components/tesseracts/scaler/test_cases/example.json").unlink(
        missing_ok=True
    )
    run(f"cp -r {EXAMPLE_FILES}/* .", cwd=project)

    run(["make", "build"], cwd=project)
    run(["make", "test", "scaler"], cwd=project)

    # Negative test: a failing regression case must make `make test` exit
    # non-zero. Guards against the `test` endpoint reporting failures inside an
    # HTTP-200 body (a real bug this repo has hit before).
    bad_case = project / "components/tesseracts/scaler/test_cases/_should_fail.json"
    bad_case.write_text(
        '{"endpoint": "apply", '
        '"payload": {"inputs": {"vector": [1.0], "scale_factor": 2.0}}, '
        '"expected_exception": "ValueError"}'
    )
    failed = run(["make", "test", "scaler"], cwd=project, check=False)
    assert failed.returncode != 0, "`make test` passed despite a failing test case"
    bad_case.unlink()

    # The app installs and its own tests pass against the built image.
    run("pip install ./app[dev]", cwd=project)
    run(["make", "test", "app"], cwd=project)
    result = run(["make", "run"], cwd=project)
    assert "Running Test Project pipeline" in result.stdout


# ---------------------------------------------------------------------------
# Recipe matrix
#
# The README advertises `make new <name> RECIPE=jax|pytorch`. The template's
# job is to scaffold and wire each recipe (copy `.template/*`, append the
# shared_code dependency) and produce a buildable component. We therefore assert
# scaffold + build for every recipe.
#
# `base` ships a runnable empty-schema `apply`, so it is additionally exercised
# through `make test`. The jax/pytorch recipe defaults are placeholders that are
# not runnable as-is (e.g. the pytorch recipe references an input outside its
# schema), so those stop at a successful build — running them is the user's job
# once they fill in real logic, not the template's.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("recipe", ["base", "jax", "pytorch"])
def test_recipe_scaffolds_and_builds(rendered_project: Path, recipe: str) -> None:
    """`make new NAME RECIPE=X` scaffolds a wired, buildable component."""
    project = rendered_project
    name = f"comp_{recipe}"
    # The recipe is passed as a make variable (`RECIPE=`) rather than a CLI flag:
    # `make` would otherwise parse a leading `--recipe` as one of its own options
    # before the target ever sees it.
    run(["make", "new", name, f"RECIPE={recipe}"], cwd=project)

    comp = project / "components" / "tesseracts" / name
    assert (comp / "tesseract_api.py").is_file()
    assert (comp / "tesseract_config.yaml").is_file()
    # `make new` seeds the shared regression-test scaffolding and wires the
    # shared_code dependency into the component's requirements.
    assert (comp / "test_cases").is_dir()
    assert "../../shared_code" in (comp / "tesseract_requirements.txt").read_text(
        encoding="utf-8"
    )

    run(["make", "build", name], cwd=project)

    if recipe == "base":
        # The empty-schema default apply passes the shipped example.json.
        run(["make", "test", name], cwd=project)
