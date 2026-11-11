# Repository Guidelines

## Project Structure & Module Organization

`wagtail_qrcode/` is the reusable Django/Wagtail package. QR generation lives in `cls.py`; page integration, admin forms, panels, hooks, and redirects live in the corresponding modules. Admin templates are under `wagtail_qrcode/templates/wagtail_qrcode/admin/`.

`tests/` contains Django tests and project settings. `tests/testapp/` supplies example page models, migrations, templates, and static assets. `docs/` contains contributor instructions and MailHog setup. Packaging metadata lives in `pyproject.toml` and `MANIFEST.in`.

## Build, Test, and Development Commands

Create and activate a virtual environment, then run:

```bash
pip install -e ".[development,testing]"
make migrate
make admin
make run
```

These commands install the package in editable mode with its development and testing dependencies, initialize the example database, create an `admin` user, and serve the test site at `http://localhost:8000`. The generated `admin`/`admin` credentials are for local development only.

- `make test`: run Django tests with coverage and print missing lines.
- `python manage.py test tests.test_cls`: run one test module.
- `tox`: run the configured Python/Django/Wagtail/database matrix; install `tox` separately. PostgreSQL and MySQL environments require database services and drivers.
- `pre-commit run --all-files`: run configured code and Markdown checks; install `pre-commit` separately. There is currently no `make lint` target.

## Coding Style & Naming Conventions

Use four-space Python indentation, `snake_case` functions/modules, and `PascalCase` classes. Preserve Python 3.9 compatibility. Format with Black (88 columns), sort imports with isort's Black profile, and lint with Flake8 (120-column limit, complexity limit 10). `.pre-commit-config.yaml` also checks Markdown and formats Python examples in documentation.

## Testing Guidelines

Use Django's `TestCase`, naming files `test_*.py` and methods `test_*`. Add regression tests in the corresponding module under `tests/`. Use `tests/testapp/` for page integration fixtures and `override_settings` for configuration variations. Coverage measures package branch coverage; no minimum percentage is configured. Run `make test` before submitting and relevant tox environments for compatibility changes.

## Development & Review Skills

- [Development](.agents/skills/development/SKILL.md) for
  planning, implementing, and verifying package changes.
- [Code Review](.agents/skills/code-review/SKILL.md) for
  requested reviews and reporting findings with evidence.

## Wagtail Skills

Read the local skill relevant to the task. Follow this guide for the
package’s development commands, compatibility matrix, and testing conventions.

- [Wagtail upgrade](.agents/skills/wagtail-upgrade/SKILL.md) for adding
  support for a Wagtail release or resolving deprecations.
- [Wagtail backend](.agents/skills/wagtail-backend/SKILL.md) for QR code
  generation hooks, publishing behavior, redirects, and permissions.
- [Wagtail content modeling](.agents/skills/wagtail-content-modeling/SKILL.md)
  for changes to `QRCodeMixin`, editor panels, or the example page model.

When updating imported skills, follow the
[provenance notes](.agents/skills/PROVENANCE.md) and preserve the licence material.

## Commit & Pull Request Guidelines

Create working branches from the latest `main` and target pull requests at
`main`, the default integration branch. Prepare releases through `main` and
create release tags from reviewed commits there. The former `release` branch
is retired from active development. See the
[contribution workflow](docs/contrubute.md#branches-and-pull-requests).

History uses short, descriptive subjects such as `Update pre-commit hooks and dependencies`; no mandatory prefix scheme is evident. Keep commits focused. In pull requests, explain the behavior change, link relevant issues, and report validation commands/results. Include screenshots for admin interface changes and update documentation when configuration or public behavior changes.
