#!/usr/bin/env python3
"""Pre-prompt hook for cookiecutter template.

This script runs before prompting the user for template variables.
It validates that required tools are installed.
"""


def check_tesseract_cli() -> bool:
    """Check if the Tesseract (tesseract-core) package is installed.

    We deliberately import ``tesseract_core`` rather than probing for a
    ``tesseract`` binary on the PATH: the unrelated Tesseract OCR project also
    ships a ``tesseract`` executable, so a ``shutil.which`` check produces a
    false positive on machines that have OCR installed but not tesseract-core.

    Returns:
        True if tesseract-core is importable, False otherwise.
    """
    try:
        import tesseract_core  # noqa: F401
    except ImportError:
        return False
    return True


def main() -> None:
    """Validate prerequisites before template generation."""
    print("Checking prerequisites...")

    if not check_tesseract_cli():
        print("WARNING: tesseract-core is not installed in this environment.")
        print(
            "The generated project needs it to build and run components "
            "(`make new`, `make build`, `make run`)."
        )
        print(
            "Note: a `tesseract` binary on your PATH may be the unrelated "
            "Tesseract OCR tool."
        )
        print(
            "Install tesseract-core before working with the project: "
            "https://github.com/pasteurlabs/tesseract-core"
        )

    print("Prerequisites check complete!")


if __name__ == "__main__":
    main()
