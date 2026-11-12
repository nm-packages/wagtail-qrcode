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

Use four-space Python indentation, `snake_case` functions/modules, and `PascalCase` classes. Preserve Python 3.11 compatibility, the current minimum under the support policy below. Format with Black (88 columns), sort imports with isort's Black profile, and lint with Flake8 (120-column limit, complexity limit 10). `.pre-commit-config.yaml` also checks Markdown and formats Python examples in documentation.

## Platform Support Policy

- Support every stable Python release that has not reached upstream end of life,
  including releases receiving security fixes only. Exclude prereleases.
- For Django and Wagtail independently, support the latest stable release and
  all intervening feature releases back to and including the preceding LTS
  release. If the latest stable release is itself an LTS, retain the previous
  LTS as the lower boundary.
- Test only combinations supported by both frameworks and the interpreter.
  Verify upstream compatibility tables, required patch versions and lifecycle
  dates when upgrading; do not build an unrestricted version cross product.
- A platform upgrade applies this rolling policy, including removing versions
  outside it. Do not retain historical minimums by default or ask again for
  approval to apply this policy. Explicit user targets take precedence.
- Keep package requirements, classifiers, tox, CI, formatter targets and
  documentation aligned. At November 2026 the ranges are Python 3.11–3.15,
  Django 5.2 LTS–6.1 and Wagtail 7.4 LTS–8.1. See
  [compatible combinations](docs/platform-upgrade.md) for the current matrix.

## Testing Guidelines

Use Django's `TestCase`, naming files `test_*.py` and methods `test_*`. Add regression tests in the corresponding module under `tests/`. Use `tests/testapp/` for page integration fixtures and `override_settings` for configuration variations. Coverage measures package branch coverage; no minimum percentage is configured. Run `make test` before submitting and relevant tox environments for compatibility changes.

## Development & Review Skills

- [Development](.agents/skills/development/SKILL.md) for
  planning, implementing, and verifying package changes.
- [Code Review](.agents/skills/code-review/SKILL.md) for
  requested reviews and reporting findings with evidence.
- [Python upgrade](.agents/skills/python-upgrade/SKILL.md) for adding Python
  version support, raising the minimum version, or resolving interpreter
  compatibility failures.
- [Django upgrade](.agents/skills/django-upgrade/SKILL.md) for adding Django
  release support, raising its minimum version, or resolving Django deprecations.
- [Platform upgrade](.agents/skills/platform-upgrade/SKILL.md) for coordinating
  Python, Django, and Wagtail upgrades through one compatibility plan. Each
  component upgrade skill can also be used independently.

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

Use the [PR template](.github/pull_request_template.md), removing sections that do
not apply. Keep the title and description aligned with the complete final diff.
When pushing additional work to an existing PR, update its description and
validation results in the same workflow. Identify the commit or revision for CI
results and distinguish earlier passing runs from checks for the current head.

Add an entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md) for notable
changes, including features, bug fixes, compatibility changes, and contributor
workflow changes. Describe the outcome and any action users or contributors
need to take, following the existing style. Trivial edits need no entry; explain
in the PR when no changelog update is needed. Keep entries aligned with the final
scope when more work is added to an existing PR. Do not assign a release version
or date outside release preparation.
