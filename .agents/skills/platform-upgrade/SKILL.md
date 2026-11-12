---
name: platform-upgrade
description: Coordinate a combined Python, Django, and Wagtail upgrade for wagtail-qrcode using the individual upgrade skills. Use for whole-platform upgrade plans, compatibility audits, or implementation spanning multiple platform components; use an individual skill for an isolated component upgrade.
---

# Platform Upgrade

Coordinate the existing upgrade skills through one compatibility plan. Keep their
component-specific instructions in those skills rather than duplicating them
here. Each remains usable independently:

| Component | Skill | Responsibility |
| --- | --- | --- |
| Python | [Python upgrade](../python-upgrade/SKILL.md) | Interpreter support, syntax baseline, packaging tools |
| Django | [Django upgrade](../django-upgrade/SKILL.md) | Framework APIs, deprecations, settings, migrations, database requirements |
| Wagtail | [Wagtail upgrade](../wagtail-upgrade/SKILL.md) | CMS upgrade path, Wagtail APIs, admin integration |

Read the relevant component skills before planning their changes. For a full
platform upgrade, read all three. For a partial upgrade, inspect compatibility
with unchanged components and load their detailed workflows only if affected.
Follow the [repository guidelines](../../../AGENTS.md) for project conventions.

## Set one scope and support policy

Establish whether the request is a plan, audit, or implementation, and whether it
adds versions or replaces the minimum supported versions. Planning and audits
remain read-only: no file changes, dependency installs, new environments,
branches, or migrations. An authorized implementation permits necessary local
work; do not introduce repeated approval steps for that work.

Build one inventory from package metadata, tox, CI, documentation, and available
environment information. Separate declared support, tested combinations, and
locally installed versions. Record explicit targets and constraints for each
component. Carry these decisions into the component workflows so a default such
as "latest Wagtail" cannot override a target already chosen for this request.

When the user requests the latest platform, verify stable releases and support
dates from official sources linked by the component skills. Identify a mutually
supported combination; independently selecting each component's newest release
may not yield one. Explain any difference between the newest individual releases
and the newest compatible combination. If targets are missing and cannot be
inferred, inspect first and clarify the decision before changing support policy.

Apply the repository's [platform support policy](../../../AGENTS.md#platform-support-policy):
all stable, non-EOL Python releases, and each framework's latest stable release
back through the preceding LTS, using mutually compatible combinations. A
platform upgrade includes removing versions outside this rolling policy; do not
default to preserving historical minimums or ask again to apply the policy.
Explicit user targets take precedence. If they conflict, explain the constraints
and present viable choices rather than silently changing the user's targets.

## Work out the compatibility path

Use the component skills' official release notes and compatibility sources to
create one table of retained, intermediate where needed, and target combinations.
Include Python, Django, Wagtail, required patch versions, database server/driver
requirements, and the evidence supporting each combination. Mark unknowns.

Derive the order from compatibility overlaps rather than always upgrading Python,
then Django, then Wagtail. For example, an intermediate Wagtail release may be
needed to bridge old and new Django versions, or a newer interpreter may first
require updated frameworks. Keep each execution stage installable and testable.
If there is no supported bridge, describe the transition in an isolated target
environment and its validation limits; do not claim an unsupported intermediate
combination is a supported upgrade path.

Distinguish temporary environments used to diagnose an upgrade from the final
support matrix for this reusable package. Preserve valid combinations inside the
agreed support policy and avoid an unrestricted cross product of framework and
interpreter versions.

## Execute the component work as one change

In implementation mode, capture a useful baseline once and apply the relevant
component instructions in the chosen order. Pass the agreed mode, target range,
retained support, and validation results into each stage. Keep a single record
of completed changes and unresolved issues; component workflows should not reset
the plan or repeat unchanged baseline checks.

Reconcile shared files after each stage: `pyproject.toml`, `tox.ini`,
`.github/workflows/test.yml`, tool pins, existing lockfiles, and documentation.
Resolve dependency bounds and environment markers against the whole support
matrix. Do not let a later component update undo earlier compatibility work.
Keep syntax compatible with the lowest retained Python version and framework
shims needed by retained Django or Wagtail versions.

Use each component skill's checks to verify a stage before relying on it for the
next. When a failure appears, identify the responsible component or dependency
and fix it within scope; re-evaluate the path if a compatibility assumption fails.
Ask only when the resolution changes the user's support policy or scope.

## Verify and hand off the combined result

Run the final package checks against the resulting matrix, reusing still-valid
results where no later change affects them. Cover the target combination, the
lowest retained boundaries, and affected framework/database combinations. Include
`make test`, relevant explicit tox environments, Django system and migration
checks, applicable pre-commit hooks, and packaging checks when required by the
component changes. Inspect admin behavior when Wagtail UI integration changes.

Check actual installed versions and tox skips; this repository can skip missing
interpreters. A pass in one component or environment does not establish that the
combined platform or all retained combinations work.

Produce one report with the before/after support matrix, upgrade stages,
compatibility evidence, code and dependency changes, and checks with actual
versions. Distinguish passes, failures, skips, and unverified combinations.
Include unresolved deprecations and required follow-up without treating optional
modernization as part of the completed upgrade.
