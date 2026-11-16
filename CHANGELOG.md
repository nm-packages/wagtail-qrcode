# Wagtail QRcode Changelog

## Unreleased

- Generate QR previews, SVG/EPS downloads and email attachments on demand, without Documents or page asset fields. Codes follow each page's ID, including copies, translations and chained aliases. Downloads require edit permission; aliases have QR actions in the header menu.
- Store scan counts outside revisions and increment them atomically. Only live QR pages redirect; malformed IDs return 404. Restoring revisions leaves counts alone; deleting a page removes its counter. Editors can reset counts immediately without losing unsaved input.
- Send EPS emails after an explicit save commits, using validated form values. Autosave sends nothing. Prefill editable subject and body fields with `WAGTAIL_QRCODE_EMAIL_SUBJECT` and `WAGTAIL_QRCODE_EMAIL_BODY`; recipients start blank and messages are not stored. Custom field initials, disabled fields and cleaning are respected; constructor `initial=` takes precedence.
- Run package migrations for the new counter table and host migrations to remove old mixin fields. Legacy documents, counters and revisions are not converted. Remove `collection_name` and `svg_has_doc_type_declaration` settings; SVG always includes its namespace.
- Apply a rolling support policy: non-EOL Python releases and framework releases from the preceding LTS through latest stable, in compatible combinations. Current ranges are Python 3.11–3.15, Django 5.2–6.1 and Wagtail 7.4–8.1. Upgrade older installations to the new minimums.
- Run 34 tox environments by default: all 28 SQLite combinations and three Django/Wagtail pairs on Python 3.14 for each of PostgreSQL and MySQL. All 84 combinations remain selectable. Tox forwards database settings; CI uses PostgreSQL 16 and MySQL 8.4 on Ubuntu 24.04.
- Fix PostgreSQL test configuration and remove assumptions that database IDs restart at one. Use `MAILERS` on Django 6.1 and retain older email settings on Django 5.2 and 6.0.
- Use uv with a committed contributor lock and a `dev` dependency group instead of development/testing extras. Tox resolves its framework matrix separately.
- Replace Make with Just 1.59.0+ and Black/isort/Flake8/blacken-docs with pinned Ruff. Use `just sync`, `just format` and `just lint`; CI uses the same locked tools and checks justfile formatting.
- Add a persistent sandbox with published/draft examples and local email capture, replacing MailHog. Use `just sandbox-setup` and `just sandbox-run`; package and sandbox tests have separate discovery and data.
- Simplify the sandbox to the QR examples and Wagtail admin, without Documents, Django admin, a WSGI entrypoint or `local.py` overrides. Configure it through environment variables. Recreate outdated sandbox schemas with `just sandbox-reset`, which deletes manual sandbox data.
- Add development, review and platform upgrade skills. Use `main` for contribution and release preparation; retire `release`. Add a PR template and require current descriptions, validation results and notable-change entries.
- Shorten the README and contributor guides, remove repeated instructions, and align repository links and tooling notes.

## [2.1.1] - 2025-05-16

- Test against Wagtail 5.2 - 6.3 and Django 4.2 - 5.1
- Fix template attribute from `class_name` to `classname` for Wagtail 6.0 compatibility
- Fix hooks to only delete documents with existing QR codes
- Drop support for Python 3.8
- Update contribution guidelines

## [2.1.0] - 2024-07-14

- Add testing for Wagtail 5.2 & 6.0
- Add testing for Django 5.0
- Add testing for Python 3.12

## [2.0.0] - 2023-08-01

- [General tidy up around tests and docs](https://github.com/nickmoreton/wagtail-qrcode/pull/28)
- Drop older versions
- Move tests and tes with postgres and mysql as well as sqlite
- Test against wagtail 5.0 <https://github.com/thepubclub/wagtail-qrcode/pull/42>

## [1.0.0] - 2022-09-09

- [Support Wagtail 4](https://github.com/nickmoreton/wagtail-qrcode/pull/24)

## [0.1.4] - 2022-08-17

- [Change admin form and misc. improvements](https://github.com/nickmoreton/wagtail-qrcode/pull/23)

## [0.1.3] - 2022-08-14

- [Add more options around emailing EPS](https://github.com/nickmoreton/wagtail-qrcode/pull/19)
- [Improve documentation](https://github.com/nickmoreton/wagtail-qrcode/pull/18)

## [0.1.2] - 2022-08-12

Correct version

## [0.1.1] - 2022-08-12

Allow python >=3.7

## [0.1.0] - 2022-08-11

Initial release
