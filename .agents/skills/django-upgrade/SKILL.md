---
name: django-upgrade
description: Plan or implement Django upgrades for wagtail-qrcode, including adding Django release support, raising the minimum version, and resolving Django deprecations or compatibility failures. Use for Django-specific upgrades; use platform-upgrade when coordinating Python, Django, and Wagtail changes together.
---

# Django Upgrade

Use the [repository guidelines](../../../AGENTS.md) for contributor commands and
Git conventions. This skill works independently for Django changes; a platform
upgrade is not a prerequisite.

## Establish the Django support policy

Distinguish adding support for a release from raising the minimum or fixing a
failure on an already supported release. This is a reusable package: preserve
existing supported versions unless the request changes that policy. Read the
declared and tested ranges rather than treating the active environment as the
package's only supported combination.

Identify the target from the request and repository context. If it remains
unspecified, inspect the current range and clarify before changing it. For
"latest" or "latest LTS", verify the applicable stable release and support dates
at the current date; do not silently substitute a prerelease.

For planning or audit requests, inspect and report without modifying files,
installing dependencies, creating environments, or applying migrations. For an
authorized upgrade, continue necessary local work. Ask when resolving a conflict
would drop promised compatibility or materially expand scope.

Read these sources together:

- `pyproject.toml`: Django classifiers, Python requirements, Wagtail constraints,
  and any direct Django requirement. Django currently arrives through Wagtail;
  distinguish that dependency from the explicit Django factors in tox.
- `tox.ini`: Django dependency factors and their Python, Wagtail, and database
  combinations, plus `gh-actions` mappings.
- `.github/workflows/test.yml`: all database jobs and the tox combinations
  selected by their Python and database values.
- `tests/settings.py`, `tests/testapp/`, and package code: framework APIs,
  migrations, settings, forms, queries, URL handling, and templates affected by
  the upgrade. Treat the test app as a host integration fixture.
- `README.md`, `CHANGELOG.md`, `docs/`, and contributor guidance: advertised
  compatibility and local setup. Inspect existing lockfiles if present.

## Determine a supported upgrade path

Use official sources for the versions involved:

- [Supported Django releases](https://www.djangoproject.com/download/#supported-versions)
  for stable releases, support status, and LTS choices.
- [Django upgrade guide](https://docs.djangoproject.com/en/stable/howto/upgrade-version/)
  for the upgrade method and warning checks.
- [Django release notes](https://docs.djangoproject.com/en/stable/releases/)
  and [deprecation timeline](https://docs.djangoproject.com/en/stable/internals/deprecation/)
  for every intervening feature release, including removals and incompatible
  behavior changes. Use version-specific pages for the affected releases.
- [Django's Python compatibility table](https://docs.djangoproject.com/en/stable/faq/install/#what-python-version-can-i-use-with-django)
  and the affected release's database documentation for interpreter, database
  server, and driver minimums.
- [Wagtail compatibility guidance](https://docs.wagtail.org/en/stable/releases/upgrading.html)
  and the affected Wagtail release notes for supported Django combinations.

Check required patch releases and third-party dependency support. Resolution
success alone does not prove upstream compatibility. Where practical, use
incremental feature-release checks with the latest patch in each series to
isolate failures. These checks do not automatically add intermediate releases to
the package's advertised support policy.

Choose valid Python/Django/Wagtail combinations instead of expanding every tox
factor into an unsupported cross product. If a new Django release needs newer
Python or Wagtail, retain valid old combinations and add suitable new ones.
Use [Python upgrade](../python-upgrade/SKILL.md) or
[Wagtail upgrade](../wagtail-upgrade/SKILL.md) when those changes are needed within
scope. Do not require the platform skill for a Django-only change.

## Apply compatibility changes

Capture a baseline when practical, then isolate the target dependency
combinations. Record installed versions so dependency resolution is visible.

- Align Django classifiers, dependency constraints where needed, tox factors,
  CI selection, and support documentation. Do not add a direct Django dependency
  merely to select a test version; use tox for test combinations. Add a runtime
  constraint when needed to express an actual package compatibility requirement.
- Fix affected Django APIs, settings, forms, queries, storage, URLs, and templates
  while retaining behavior on the oldest supported framework and interpreter.
  Use [Wagtail backend](../wagtail-backend/SKILL.md) for affected publishing,
  permissions, redirects, or ORM behavior.
- Add focused regression tests for behavior fixes using Django `TestCase` and
  `override_settings`. Do not rewrite unrelated code or create tests solely for
  metadata edits.
- Check migration requirements before generating files. Keep existing migrations
  loadable on the retained range and avoid generating migrations only to absorb
  incidental framework default changes. Validate necessary migrations against a
  disposable test database.
- Update existing lockfiles with their owning tool if present, and document the
  final supported combinations and any new dependency minimums.

## Validate and report

Run `make test`, relevant explicit tox environments, and
`python manage.py check` in affected environments. Include the target Django
release and the oldest retained framework boundary. Exercise the affected
database backends when services are available, especially when database or
driver requirements change. Run applicable pre-commit hooks for changed files.

Review deprecation warnings on the old and target versions, tracing whether they
come from this package or dependencies. Do not broadly silence warnings to get a
pass. Check for missing model migrations with
`python manage.py makemigrations --check --dry-run`; the test runner should also
exercise migration application on a fresh test database.

Inspect tox summaries for skipped interpreters and verify the installed versions
match the intended factors. Report commands and actual combinations tested,
failures, skips, unavailable databases, and unresolved warnings. Summarize the
before/after support policy and link official evidence for compatibility
decisions without claiming unexecuted matrix checks passed.
