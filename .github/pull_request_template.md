# Short, specific PR title

<!--
Replace the heading above with the specific PR title describing the change.
Target main. Keep the title and description aligned with the complete final diff,
including work added after opening the PR. Remove sections that do not apply.
-->

## Summary

<!-- Explain the problem and resulting behavior. Link related issues if relevant. -->

## Changes

<!-- Highlight the changes a reviewer needs to understand and any key tradeoffs. -->

## Validation

<!--
List actual commands and results. For code changes, include make test; for
compatibility changes, include relevant tox environments and the actual Python,
Django, Wagtail, and database versions tested. For documentation-only changes,
report applicable pre-commit checks.

Explain failures, skipped checks, or tests not run. Link CI results with their
commit or revision; distinguish earlier passing runs from checks for the current
head. Update this section when later commits affect the results.
-->

## Compatibility and documentation

<!--
If relevant, describe support-range changes, public settings or behavior changes,
migrations, upgrade steps, and updated documentation. Note any remaining limits.
For notable features, fixes, compatibility changes, or contributor workflow
changes, add an Unreleased entry in CHANGELOG.md. Trivial edits need no entry;
explain here when a changelog update is unnecessary.
Remove this section when it does not apply.
-->

## Screenshots

<!-- Include before/after screenshots for admin interface changes; otherwise remove. -->

## Review checklist

- [ ] The PR targets `main`, and its title and description cover the final scope.
- [ ] Validation results reflect the latest changes and identify any gaps.
- [ ] Documentation and screenshots are included where relevant.
- [ ] Notable changes have an `Unreleased` changelog entry, or I have explained why none is needed.
