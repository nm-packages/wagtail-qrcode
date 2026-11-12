---
name: development
description: Plan and implement focused changes to wagtail-qrcode. Use for package features, bug fixes, and refactors that need compatibility checks, behavior tests, or contributor documentation.
---

# Development

Use the [repository guidelines](../../../AGENTS.md) for package conventions,
commands, and Git practices. Read the relevant Wagtail technical skill listed
there. Use [Code Review](../code-review/SKILL.md) for a
requested review or an agreed review step.

## Scope the change

Identify the package behavior the caller or editor should observe and trace the
existing entry point and tests before editing. For larger changes, plan a series
of usable increments. Keep the implementation, tests, migrations when needed,
and documentation for one behavior together. A focused fix can be one increment.
Resolve product or compatibility decisions that materially affect the outcome.

## Preserve package contracts

- Check `pyproject.toml`, `tox.ini`, and the CI matrix for the applicable Python,
  Django, Wagtail, and database combinations. Verify framework behavior against
  the version affected. Routine development preserves the declared range;
  support refreshes apply the repository's rolling platform support policy,
  including removing versions outside it. Explicit user targets take precedence.
- Check how host sites configure and integrate the package before changing
  `QRCodeMixin`, public settings, admin hooks, or the scan redirect. Treat the
  example page in `tests/testapp/` as an integration fixture. Keep site-specific
  choices in the host project or in test fixtures.
- When changing QR generation, follow the affected path through document or SVG
  creation, the editor workflow, and the redirect destination where relevant.
  For admin changes, check the templates and panel APIs used by affected
  Wagtail versions.

## Verify the behavior

Choose checks that demonstrate the user-visible result. A passing HTTP status
alone does not verify a redirect destination or the content of an admin panel.
For a meaningful regression test, show that it fails for the expected behavior
before fixing the code when practical. Prefer Django `TestCase` and
`override_settings` for package settings. Cover the package's integration with
Wagtail where a test would catch a regression and rely on Wagtail's existing
coverage for framework behavior the package leaves unchanged.

- Use `python manage.py test <test-label>` for focused development checks.
- Run `make test` for package changes. Run relevant tox environments for
  compatibility changes, especially affected versions and database backends.
- Run the applicable hooks in `.pre-commit-config.yaml` for changed files or use
  `pre-commit run --all-files` for tracked files. Check links and formatting for
  documentation or skill changes.
- Inspect the admin or rendered output when the change affects what editors see.
  For model changes, check for required migrations in the affected test app.

If a check is unavailable, report the command, reason, and resulting gap. Review
the diff for unrelated changes and avoid weakening checks to obtain a pass.

## Document and hand off

Update `README.md` or the relevant guide in `docs/` when public behavior or host
configuration changes. Use the [feature guide template](assets/developer-feature-guide.md)
when a feature needs a standalone developer guide. Include any setup, editor
workflow, and concrete steps to verify it.

Add notable features, fixes, compatibility changes, and contributor workflow
changes to `CHANGELOG.md` under `Unreleased`, following the changelog rule in
`AGENTS.md`. Keep entries aligned with the final PR scope. Trivial edits need no
entry; explain in the PR when a changelog update is unnecessary.

Report the change, checks and results, and any limitations that affect use or
review. Follow `AGENTS.md` for commit and PR conventions and keep each commit
focused on the behavior it delivers.
