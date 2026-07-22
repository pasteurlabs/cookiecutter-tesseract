# Contributing to cookiecutter-tesseract

cookiecutter-tesseract is an open-source project and, as such, we welcome
contributions from developers, engineers, scientists, and end-users in general.
Contributions are what make the open source community such an amazing place to
learn, inspire, and create. Any contributions you make are greatly appreciated.

## Code of Conduct

Ensure your contributions adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Feedback

Constructive feedback is very welcome. We are interested in hearing from you!

In the case things aren't working as expected, or the documentation is lacking,
please [file a bug
report](https://github.com/pasteurlabs/cookiecutter-tesseract/issues/new?template=BUG-REPORT.yml).

In the case you want to suggest a new feature, please file a new [feature
request](https://github.com/pasteurlabs/cookiecutter-tesseract/issues/new?template=FEATURE-REQUEST.yml).
In particular, we recommend you open an issue before contributing code in a
pull request. This allows all parties to talk things over before jumping into
action, and increases the likelihood of pull requests getting merged.

In case you have general questions or feedback, need support from the
community, or have a cool demo to share, start a thread in our [Discourse
Forum](https://si-tesseract.discourse.group/). We use GitHub Issues for bug
reports and feature requests only.

## Code

cookiecutter-tesseract is developed under the [Apache 2.0](LICENSE) license. By
contributing to the project you agree that your code contributions are governed
by this license. We require you to sign our [Contributor License
Agreement](https://github.com/pasteurlabs/pasteur-oss-cla/blob/main/README.md)
to state so.

### What lives where

This repository is a [cookiecutter](https://cookiecutter.readthedocs.io)
template. A couple of things are worth knowing before you dive in:

- `{{ cookiecutter.package_name }}/` holds the files that get rendered into a
  generated project. Anything inside is Jinja-templated, so `{{ ... }}`
  placeholders are expanded at generation time.
- `hooks/` contains the pre- and post-generation hooks.
- `cookiecutter.json` defines the template variables and their defaults.
- `tests/` contains the test suite (see below).

### Local development setup

Make sure you have [Docker installed](https://docs.docker.com/engine/install/)
on your machine and you can run `docker` commands via your user; the end-to-end
tests render the template and drive a real `make build`/`run` against it. Then
clone the repository, install the test dependencies, and set up
[pre-commit](https://pre-commit.com/) hooks:

```console
$ git clone git@github.com:pasteurlabs/cookiecutter-tesseract.git
$ cd cookiecutter-tesseract
$ python -m venv venv
$ . venv/bin/activate
$ pip install cookiecutter tesseract-core pytest
$ pre-commit install
```

### Tests

This project uses the pytest framework for all tests. New code should be
covered by new or existing tests.

Tests are split into two groups:

- **Structural tests** render the template and inspect the result. They are fast
  and need no Docker.
- **End-to-end tests** (marked `e2e`) render the template and drive the real
  `make new`/`build`/`test`/`run` workflow, including the `base|jax|pytorch`
  recipe matrix. These require Docker and the Tesseract CLI, and are skipped
  automatically when Docker is unavailable.

```console
$ pytest -m "not e2e"   # structural tests only
$ pytest -m e2e         # end-to-end tests (needs Docker)
$ pytest                # everything
```

#### Testing philosophy

We follow these principles when writing tests:

- **Prefer end-to-end tests over unit tests** — Tests that render the template
  and exercise the generated project catch more bugs than isolated unit tests.
  When in doubt, write an end-to-end test.

- **Avoid mocks where feasible** — Mocks can hide real integration issues.
  If a test requires complex mocking to work, consider whether an end-to-end
  test would be more valuable.

- **Don't test implementation details** — Tests should verify behavior, not
  internal structure. If refactoring breaks your test but not the actual
  functionality, the test was too tightly coupled.

- **Be mindful of slow tests** — End-to-end tests that build Tesseracts are
  slow. Before adding a new one, check if an existing test can be extended,
  or if a faster structural test would suffice for your specific case.

### Linting and code quality

We use [pre-commit](https://pre-commit.com/) to run linters and formatters
automatically before each commit. The hooks are configured in
`.pre-commit-config.yaml` and include:

- **Ruff** — Fast Python linter and formatter (replaces flake8, isort, black)
- **Various file checks** — Trailing whitespace, YAML validation, etc.

To run all pre-commit hooks manually on all files:

```console
$ pre-commit run --all-files
```

To run a specific hook:

```console
$ pre-commit run ruff --all-files
```

### GitHub workflow

This project uses Git for version control and follows a GitHub workflow. To
contribute follow these steps:

1. Fork the project via the GitHub UI.
1. Clone your fork to your machine.
1. Add an upstream remote: `git remote add upstream git@github.com:pasteurlabs/cookiecutter-tesseract.git`.
1. Create a new branch for your code contribution: `git switch --create my_branch`.
1. Implement your changes.
1. Commit and push to your fork: `git push --set-upstream origin my_branch`.
1. [Open a Pull Request](https://github.com/pasteurlabs/cookiecutter-tesseract/pulls) with
   your changes.

It is a good practice to rebase often on top of `main` to keep your code up to
date with latest development and minimize merge conflicts:

```console
$ git fetch upstream
$ git switch main
$ git merge upstream/main
$ git switch my_branch
$ git rebase main
$ git push --force
```

### Commit and pull request messages guidelines

We follow the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all
commits that reach the `main` branch. Each commit is crafted from a pull
request that is squash-merged. The commit title and message come from the pull
request title and message, respectively. As such, they should be structured
following the specification.

The title consists of a _type_, an optional _scope_, and a short
_description_: `type[(scope)]: description`. The types we use are:

- `chore`: for changes that affect the build system, external dependencies, or
  general housekeeping.
- `ci`: for changes in the CI.
- `doc`: for documentation only changes.
- `feat`: for a new feature.
- `fix`: for fixing a bug.
- `perf`: for a code change that improves performance.
- `refactor`: for a code change that neither adds a feature nor fixes a bug.
- `security`: for a change that fixes a security issue.
- `test`: for adding new tests or fixing existing ones.

The scopes we use are:

- `template`: for changes to the rendered project (`{{ cookiecutter.package_name }}/`).
- `hooks`: for changes to the generation hooks.
- `deps`: for changes in the dependencies.

In case there are breaking changes in your code, this should be indicated in
the message either by appending an exclamation mark (`!`) after the type/scope
or by adding a `BREAKING CHANGE:` trailer to the message.

## Versioning

The project follows [semantic versioning](https://semver.org).
