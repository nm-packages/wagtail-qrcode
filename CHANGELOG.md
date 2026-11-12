# Wagtail QRcode Changelog

## Unreleased

- Prevent editor autosave from publishing QR page edits or sending EPS emails. Explicit draft saves and publication update the QR files and send the requested email once after saving, without creating an extra revision; retain existing EPS documents for published content and older revisions.
- Adopt a rolling support policy: Python releases that have not reached end of life, and Django and Wagtail releases from the preceding LTS through the latest stable release, using compatible combinations. The supported ranges are now Python 3.11–3.15, Django 5.2–6.1 and Wagtail 7.4–8.1; upgrade older installations to the new minimums.
- Ensure tox selects the requested database backend and forwards its connection settings; use PostgreSQL 16 and MySQL 8.4 in CI for the expanded platform matrix.
- Reduce CI to seven jobs and align plain `tox` with its 34 test environments: keep the full SQLite matrix and test three representative Django/Wagtail pairs on Python 3.14 for each of PostgreSQL and MySQL. Use explicit `tox -e` selections for all 84 supported combinations when needed.
- Fix database test compatibility by enabling Django's PostgreSQL application for that backend and checking generated documents without assuming primary keys restart at one.
- Use Django 6.1's `MAILERS` configuration in the example site and MailHog setup while preserving email settings for older Django versions.
- Add repository skills for development, code review, Wagtail integration, and Python, Django, Wagtail, and combined platform upgrades.
- Standardize contribution and release preparation on `main`; retire `release` from active development.
- Add a PR template and contributor guidance for keeping descriptions and validation results current and recording notable changes in the changelog.
- Fix the Django 5.1 tox dependency selector and pin CI runners to Ubuntu 24.04 for the existing Python test matrix.

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
