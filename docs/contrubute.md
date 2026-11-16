# Contributing

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.12.10+
and [Just](https://just.systems/man/en/packages.html) 1.59.0+.
On macOS, install Just with `brew install just`. Recipes need a POSIX `sh`;
on Windows, use Git for Windows with `sh` on `PATH`.

```bash
git clone --branch main https://github.com/nm-packages/wagtail-qrcode
cd wagtail-qrcode
just sync
```

This installs the editable package and locked contributor tools in `.venv`.
No activation is needed. To choose Python, use
`uv sync --locked --python 3.11` or another supported version.

The `dev` dependency group replaces the old `development` and `testing` extras.
The justfile replaces the Makefile. Recipes run from the repository root,
including when called from subdirectories.

## Commands

Run `just` to list recipes.

| Command | Purpose |
| --- | --- |
| `just sync` | Install locked dependencies |
| `just sandbox-setup` | Apply migrations and create missing examples |
| `just sandbox-run` | Serve the persistent sandbox on port 8000 |
| `just sandbox-email` | Read captured email and extract its EPS |
| `just sandbox-test` | Run isolated sandbox tests |
| `just test` | Run package tests with branch coverage |
| `just format` | Apply Ruff fixes and format Python, Markdown code blocks and the justfile |
| `just lint` | Check lint and formatting without edits |

See the [sandbox guide](sandbox.md) for login, settings and reset, and
[smoke tests](smoke-tests.md) for manual checks. The root `manage.py` and
`just migrate`, `just admin`, `just run` serve the older test fixture site.

## Checks

Run `just test` for package changes and `just lint` before submitting.
Use explicit test labels to keep package and sandbox discovery separate:

```bash
uv run --locked python manage.py test tests.test_cls
uv run --locked python manage.py test tests
uv run --locked python sandbox/manage.py test home
uv run --locked pre-commit run --all-files
```

Install hooks with `uv run --locked pre-commit install`.
Pre-commit checks Markdown prose as well as Python. Ruff formats Python and
Markdown Python blocks; PyMarkdown checks Markdown. Invalid Python blocks may
be skipped by Ruff, so review examples too.

Formatting targets Python 3.11 and 88 columns. Ruff enables E, W, F, C90 and I,
with a 120-column lint limit and complexity limit of 10. Formatter-conflicting
E111, E114, E117 and W191 are disabled. `docs/` is excluded from linting,
but its Python blocks are formatted.

Run compatibility tests with `uv run --locked tox`, or
`uv run --locked tox -f sqlite` without database services. The default selection
is 28 SQLite environments plus three each for PostgreSQL and MySQL.
See the [matrix guide](platform-upgrade.md#databases-and-validation) for database
settings and all 84 combinations. Missing interpreters are skipped; check results.
To select a test, use `uv run --locked tox -e <environment> -- tests.test_cls`.

## Dependencies and packaging

Use `uv add <package>` for runtime dependencies, `uv add --dev <tool>` for tools,
and `uv remove` with the same group choice to remove them.
Commit `pyproject.toml` and `uv.lock` together.

```bash
uv lock --upgrade-package coverage
uv sync --locked
uv lock --check
```

Use `uv lock --upgrade` only to refresh all locked versions deliberately.
Keep Ruff's dependency pin, `required-version` and pre-commit revision aligned.
Tox resolves framework versions independently of the contributor lock.

Build with `uv build`. `MANIFEST.in` includes package templates and static assets.

## Branches and pull requests

Branch from an up-to-date `main` and target PRs at `main`:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c improve-qr-code-preview
```

Use a short, descriptive commit subject. Follow the
[PR template](../.github/pull_request_template.md); remove sections that do not
apply. Include screenshots for admin changes and upgrade notes for support changes.

Keep the title, description and validation results aligned with the full diff
after each push. Link CI results to their commit so earlier passes cannot be
mistaken for current checks.

Add notable changes under `Unreleased` in [CHANGELOG.md](../CHANGELOG.md),
including any action users need to take. Trivial edits need no entry; explain
that in the PR. Add release versions and dates only during release preparation.

Prepare releases through PRs into `main`, then tag reviewed commits there using
the existing format, such as `2.1.1`. The former `release` branch is retired.
