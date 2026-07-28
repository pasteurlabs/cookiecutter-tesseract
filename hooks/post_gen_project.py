#!/usr/bin/env python3
"""Post-generation hook for cookiecutter template.

This script runs after the project is generated from the template.
"""

from datetime import datetime, timezone
from pathlib import Path

PROJECT_NAME = "{{ cookiecutter.project_name }}"
AUTHOR_NAME = "{{ cookiecutter.author_name }}"
LICENSE_ID = "{{ cookiecutter.license }}"


def get_tesseract_version() -> str | None:
    """Return the installed tesseract-core version, or None if unavailable."""
    try:
        import tesseract_core
    except ImportError:
        return None
    return tesseract_core.__version__


def pin_tesseract_version(project_dir: Path) -> None:
    """Pin the installed Tesseract version in requirements.txt, if available."""
    requirements_file = project_dir / "app" / "requirements.txt"
    current_reqs = requirements_file.read_text(encoding="utf-8")

    version = get_tesseract_version()
    if version is not None:
        requirements_file.write_text(
            current_reqs.replace("%TESSERACT_VERSION%", version), encoding="utf-8"
        )
    else:
        # tesseract-core not installed at generation time: fall back to an
        # unpinned dependency so the project is still valid.
        requirements_file.write_text(
            current_reqs.replace(
                "tesseract-core==%TESSERACT_VERSION%", "tesseract-core"
            ),
            encoding="utf-8",
        )
        print(
            "WARNING: tesseract-core not installed; leaving it unpinned in "
            "app/requirements.txt. Pin a version once installed."
        )


def render_license(project_dir: Path) -> None:
    """Write the chosen license text and record it in the app metadata."""
    license_file = project_dir / "LICENSE"
    year = datetime.now(tz=timezone.utc).year
    holder = AUTHOR_NAME or PROJECT_NAME

    text = LICENSE_TEXTS[LICENSE_ID].format(year=year, holder=holder)
    license_file.write_text(text, encoding="utf-8")

    # Record the license identifier in the app package metadata.
    pyproject = project_dir / "app" / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    content = content.replace(
        'requires-python = ">=3.10"',
        f'license = "{LICENSE_ID}"\nrequires-python = ">=3.10"',
    )
    pyproject.write_text(content, encoding="utf-8")


MIT_TEXT = """MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

BSD_3_TEXT = """BSD 3-Clause License

Copyright (c) {year}, {holder}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

APACHE_NOTICE = """Copyright {year} {holder}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The full license text is available at http://www.apache.org/licenses/LICENSE-2.0
"""

PROPRIETARY_TEXT = """Copyright (c) {year} {holder}. All rights reserved.

This software and its source code are proprietary and confidential.
Unauthorized copying, distribution, or use of this software, via any medium,
is strictly prohibited without the express written permission of the copyright
holder.
"""

LICENSE_TEXTS = {
    "Apache-2.0": APACHE_NOTICE,
    "MIT": MIT_TEXT,
    "BSD-3-Clause": BSD_3_TEXT,
    "Proprietary": PROPRIETARY_TEXT,
}


def main() -> None:
    """Perform post-generation cleanup tasks."""
    project_dir = Path.cwd()

    pin_tesseract_version(project_dir)
    render_license(project_dir)

    print("Post-generation cleanup complete!")


if __name__ == "__main__":
    main()
