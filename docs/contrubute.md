# Contributing

## Branches and pull requests

`main` is the default branch and the integration branch for ongoing work.
Create working branches from an up-to-date `main` and target pull requests
at `main`. This applies to features, bug fixes, documentation, maintenance,
and release preparation.

The former `release` branch is retired from active development.
Prepare releases through pull requests into `main`, then create release tags
from the reviewed commits on `main`. Use the existing tag format, such as
`2.1.1`.

For an existing checkout, start new work with:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c improve-qr-code-preview
```

Choose a branch name that describes the change. Confirm the pull request's base
branch is `main` before submitting it.

Use the [pull request template](../.github/pull_request_template.md) to explain
the problem, resulting behavior, and validation commands with their results.
Remove sections that do not apply. Include compatibility or upgrade notes when
support changes, and before/after screenshots for admin interface changes.

Keep the PR title and description aligned with the complete final diff. When
adding work to an existing PR, update its description and validation results as
part of the same push. Identify the commit or revision for linked CI results so
earlier passing checks are not mistaken for validation of the latest changes.

Add an entry under `Unreleased` in [CHANGELOG.md](../CHANGELOG.md) for notable
features, fixes, compatibility changes, and contributor workflow changes.
Describe the outcome and any required action, using the existing style. Keep
entries current as the PR grows. Trivial edits need no entry; explain in the PR
when a changelog update is unnecessary. Release versions and dates are added
during release preparation.

## Development setup

### First clone this repo to your computer

```bash
git clone --branch main https://github.com/nm-packages/wagtail-qrcode
```

## Install uv and sync dependencies

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.12.10 or
newer, then run:

```bash
uv sync --locked
```

This creates `.venv` and installs the package in editable mode, together with
Ruff, coverage, pre-commit, tox and its plugins from `uv.lock`. No activation is
needed: Make targets use `uv run --locked`. To choose an interpreter explicitly,
use `uv sync --locked --python 3.11` (or another supported Python version).

The former `development` and `testing` extras are replaced by the `dev`
dependency group. Existing contributors should switch to the commands above.
Normal installation of the published package with pip remains supported.

### Updating dependencies

Use `uv add <package>` for runtime dependencies and `uv add --dev <tool>` for
contributor tools; use `uv remove` (with `--dev` for tools) to remove them.
Commit `pyproject.toml` and `uv.lock` together. For a targeted version refresh:

```bash
uv lock --upgrade-package coverage
uv sync --locked
uv lock --check
```

Use `uv lock --upgrade` only for an intentional refresh of all locked versions.
Ruff's dependency pin, `required-version`, and pre-commit revision must still
agree. Run the checks below after dependency changes.

The lock captures the contributor environment across supported Python versions.
Tox uses the locked tooling but resolves each environment's framework constraints
independently through tox-uv, so the development lock cannot collapse the matrix
to one Django/Wagtail pair. Database drivers remain specific to tox environments.

Build distributions with `uv build`; setuptools includes the package's admin
templates via `MANIFEST.in`.

## Run the persistent sandbox

```bash
make sandbox-setup
make sandbox-run
```

Open <http://localhost:8000/> or <http://localhost:8000/admin/> and log in with
`admin` / `admin`. Setup is repeatable and preserves edits and existing passwords.
The [sandbox guide](sandbox.md) explains local configuration, captured email,
optional device testing and the explicit `make sandbox-reset` operation.
Use the [developer smoke tests](smoke-tests.md) to verify the manual workflows.

The root `manage.py`, `make migrate`, `make admin` and `make run` remain available
for the older automated test fixture site. Use the `sandbox-` targets for manual
testing so content and generated files persist separately from the test suite.

## Other commands

- `make test`: run package tests in `tests/` with coverage.
- `make sandbox-test`: run sandbox integration tests with isolated database/media.
- `make sandbox-email`: print the latest captured email and extract its EPS.
- `make format`: apply Ruff fixes and format Python and Markdown code blocks.
- `make lint`: check lint and formatting without changing files.
- `make mail`: start optional [MailHog](mailhog.md), preserving local settings.
- `make mail-stop`: stop and remove the MailHog container.

When invoking the root test runner directly, use
`uv run --locked python manage.py test tests` to keep discovery within the package
suite. Sandbox tests use `uv run --locked python sandbox/manage.py test home`.
Tox defaults to package tests; pass a specific label with
`uv run --locked tox -e <environment> -- tests.test_cls`.

## Formatting and linting

Run `uv sync --locked` to install the locked contributor tools.
Run `make format` before committing and `make lint` to run the same checks as CI.
Run `uv run --locked pre-commit install` to enable hooks and
`uv run --locked pre-commit run --all-files` to check all tracked files, including Markdown prose.
Ruff lint fixes run before formatting; PyMarkdown remains the Markdown checker.

Ruff replaces Black, isort, Flake8 and blacken-docs. The development dependency,
`required-version` and pre-commit hook revision must be updated together. CI
uses `uv sync --locked` to install the same tools and reject a stale lockfile.

The formatter targets Python 3.11 and 88 columns. Linting enables Ruff's stable
`E`/`W` (pycodestyle), `F` (Pyflakes), `C90` (McCabe), and `I` (import sorting)
rules, with a 120-column lint limit and maximum complexity of 10. `tests` and
`wagtail_qrcode` are explicitly first-party imports. Existing build, environment,
and legacy directory exclusions are retained; `docs/` is excluded from linting
but its Python code blocks are formatted.

Rule coverage is close rather than identical to Flake8: Ruff leaves some
whitespace checks to the formatter, and preview-only rules are not enabled.
The formatter-conflicting `E111`, `E114`, `E117`, and `W191` are disabled.
The former `D203` ignore was inactive without a docstring plugin, and Ruff does
not implement `W503`. Ruff's `E501` also exempts some long URLs and single words.
Import ordering and formatting can differ slightly from isort and Black.
See the [Ruff formatter documentation](https://docs.astral.sh/ruff/formatter/)
and [compatibility notes](https://docs.astral.sh/ruff/faq/).

Ruff 0.17.5 formats Python fenced code blocks in Markdown without preview mode;
the formatter hook explicitly includes Markdown. Invalid Python blocks are
skipped, so examples still need review. Markdown prose and shell blocks remain
under PyMarkdown's existing checks.

## Testing

Follow the [platform support policy](../AGENTS.md#platform-support-policy):
support all stable Python releases that have not reached end of life, and
Django and Wagtail releases from the preceding LTS through the latest stable
release. Test only mutually compatible combinations. See the
[current matrix and upgrade notes](platform-upgrade.md).

The app uses django tests and has `tox` setup for running them against the compatible Wagtail and Django versions.

Run:

```bash
uv run --locked tox
```

The default selection matches CI: all 28 SQLite combinations and three
representative combinations each for PostgreSQL and MySQL, for 34 environments
in total. Server database tests require running services and their connection
settings. Use `uv run --locked tox -f sqlite` for SQLite only, or `uv run --locked tox -f postgres` / `uv run --locked tox -f mysql`
for the three representative server database environments. See the
[matrix guide](platform-upgrade.md#databases-and-validation) for explicit
selections covering all 84 supported combinations.
