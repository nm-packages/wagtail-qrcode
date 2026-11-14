---
name: python-upgrade
description: Plan or implement Python version upgrades for wagtail-qrcode, including adding interpreter support, raising the minimum Python version, and resolving Python compatibility failures. Use when changing the package's Python support policy or validating it against a new Python release.
---

# Python Upgrade

Use the [repository guidelines](../../../AGENTS.md) for contributor commands and
Git conventions and the [platform support policy](../../../AGENTS.md#platform-support-policy).
Support all stable Python releases that have not reached upstream end of life,
including those receiving security fixes only. A Python support refresh adds new
stable releases and removes EOL releases; do not preserve historical minimums by
default. Keep framework combinations within their own support policy.

## Establish the intended support range

Distinguish adding a Python version from raising the minimum version or fixing a
failure on an already supported interpreter. Read the current declarations rather
than assuming that the developer's active interpreter defines package support.
For an unspecified support refresh, verify the latest stable release and all
non-EOL branches against the current date, then apply the repository policy.
Explicit user targets take precedence; treat prerelease support separately.

For planning or audit requests, inspect and report without changing files,
installing dependencies, or creating environments. For an authorized upgrade,
continue the necessary local changes and checks. Ask only when a decision would
drop support inside the agreed policy or materially expand the requested upgrade.

Inspect these sources together:

- `pyproject.toml`: `requires-python`, Python classifiers, runtime dependencies,
  development tools, and Black's `target-version`.
- `tox.ini`: interpreter factors, Django/Wagtail dependency factors,
  `envlist`, `gh-actions` mappings, and database combinations.
- `.github/workflows/test.yml`: Python matrices in every database job and their
  mapping to tox environments.
- `.pre-commit-config.yaml`: hook versions, tool pins, and any interpreter
  requirements. Check environment, container, or lock files if present.
- `README.md`, `CHANGELOG.md`, `docs/`, and `AGENTS.md`: advertised support,
  contributor setup, and minimum-version instructions.

## Check upstream compatibility

Use official sources for the specific versions under consideration:

- [Python version status](https://devguide.python.org/versions/) for release
  status and lifecycle dates.
- [Python What's New](https://docs.python.org/3/whatsnew/index.html) for the
  target release and intervening releases, particularly porting guidance,
  removals, deprecations, and packaging or build changes.
- [Django's Python compatibility table](https://docs.djangoproject.com/en/stable/faq/install/#what-python-version-can-i-use-with-django)
  and the documentation for each retained Django release.
- [Wagtail compatibility guidance](https://docs.wagtail.org/en/stable/releases/upgrading.html)
  and the release notes for each affected Wagtail version.

Check minimum patch releases where upstream added interpreter support. Inspect
runtime and transitive dependencies, database drivers, and test/build tools for
target-interpreter support using their official release notes and package
metadata. Successful dependency resolution alone does not establish upstream
support. If sources are unavailable, report the unresolved compatibility.

Build the matrix from supported Python/Django/Wagtail combinations rather than
blindly multiplying all factors. Preserve valid existing combinations. If the new
Python version requires newer frameworks, add suitable combinations for that
interpreter without forcing all existing users onto newer dependencies. Use
[Django upgrade](../django-upgrade/SKILL.md) or
[Wagtail upgrade](../wagtail-upgrade/SKILL.md) when a framework upgrade is needed
within the agreed scope.

## Implement the upgrade

Keep the changes focused on interpreter compatibility:

- Adding a newer interpreter alone does not require raising `requires-python`
  or Black's syntax target. Add its classifier and matching tox and CI coverage.
- When the rolling policy removes EOL releases, or the user explicitly changes
  the minimum, align `requires-python`,
  classifiers, tox, CI, formatter targets, and documentation, including the
  compatibility instruction in `AGENTS.md`. Remove compatibility shims only when
  their supported consumers have been removed.
- Change code only where Python changes affect it. Keep syntax and APIs usable
  on the lowest retained interpreter, including tests and test-app migrations.
  Add regression tests for actual behavior fixes rather than metadata edits.
- Update dependency or tool pins only as needed, keeping corresponding
  pre-commit and development pins consistent. Update existing lockfiles with
  their owning tool if present; do not introduce a new dependency manager.
- Document the resulting support range and any required dependency minimums
  using the repository's existing README and changelog conventions.

## Verify the declared support

Capture a baseline in the existing environment when practical, then use isolated
environments for affected interpreter/dependency combinations. Record the actual
Python, Django, and Wagtail versions used so resolver choices are visible.

- Enumerate the tox environments with the installed tox version's listing
  command and check that CI selects the intended factors for each Python and
  database job.
- Run `make test` and relevant explicit tox environments on the new interpreter
  and the lowest retained interpreter, covering affected framework boundaries.
  Exercise PostgreSQL and MySQL combinations when drivers or database behavior
  are affected and services are available.
- Check the tox results for skipped environments: this repository enables
  `skip_missing_interpreters`, so a successful exit can leave Python versions
  untested. Report unavailable interpreters or databases as validation gaps.
- Run `python manage.py check` in the affected environment and the applicable
  pre-commit hooks. Review deprecation warnings, identify their source, and fix
  upgrade-related failures without suppressing warnings broadly or weakening
  tests. Use meaningful regression tests for changes to package behavior.
- If packaging configuration or build dependencies change, build with the
  project's tooling and verify installation of the built package on the target
  interpreter; editable installation alone does not verify the distribution.

Report the before/after support range, compatibility decisions with links to
the official evidence, changed files, and checks that ran. Separate passing,
failing, and skipped checks, and state what remains unverified. Do not describe
the full matrix as passing when only a subset ran.
