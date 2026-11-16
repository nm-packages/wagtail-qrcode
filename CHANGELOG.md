# Wagtail QRcode Changelog

## Unreleased

### Breaking changes

- Require Python 3.11+, Django 5.2+ and Wagtail 7.4+. See the
  [supported combinations](README.md#installation).
- Replace the mixin's stored QR fields with on-demand output and a separate
  counter table. Run package and host migrations; preserve existing scan counts
  before removing the old fields. Legacy documents, counts and revisions are
  not converted automatically. Follow the [upgrade guide](docs/upgrading.md).
- Remove the `collection_name` and `svg_has_doc_type_declaration` settings.

### Features and fixes

- Generate QR previews, SVG/EPS downloads and email attachments on demand.
  Downloads require page edit permission. Copies, translations and aliases have
  their own codes and counts.
- Keep scan counts independent of revisions and add an editor control to reset
  them. Only live QR pages redirect; invalid IDs return 404.
- Send email after an explicit save commits; autosave sends nothing. Add
  configurable [subject and body defaults](README.md#configuration).

### Contributor changes

- Document the
  [test driven development workflow](docs/contrubute.md#test-driven-development).
- Adopt uv, Just and Ruff for dependencies, commands and formatting. Follow the
  updated [contributor guide](docs/contrubute.md).
- Add a persistent [sandbox](docs/sandbox.md) with example pages and local email
  capture, replacing MailHog.
- Expand compatibility testing and fix PostgreSQL test configuration. See the
  [test matrix](docs/platform-upgrade.md#databases-and-validation).
- Use `main` for contributions and releases; retire the `release` branch.
  Add contributor skills and a PR template, and simplify the documentation.

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
