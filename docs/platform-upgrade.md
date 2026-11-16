# Platform compatibility

## Support policy

We support stable Python releases until upstream end of life, including
security-only releases. For Django and Wagtail, we support the latest stable
release back through the preceding LTS. If the latest release is an LTS,
we retain the previous LTS too.

Use mutually compatible combinations. Support refreshes remove versions outside
this window and align requirements, classifiers, tox, CI, tooling and docs.
See [repository policy](../AGENTS.md#platform-support-policy).

## Compatible combinations

The November 2026 matrix supports Python 3.11–3.15, Django 5.2–6.1 and
Wagtail 7.4–8.1:

| Wagtail | Django | Python |
| --- | --- | --- |
| 7.4 LTS | 5.2 LTS | 3.11–3.14 |
| 7.4 LTS | 6.0 | 3.12–3.14 |
| 8.0 | 5.2 LTS | 3.11–3.14 |
| 8.0 | 6.0, 6.1 | 3.12–3.14 |
| 8.1 | 5.2 LTS | 3.11–3.14 |
| 8.1 | 6.0 | 3.12–3.14 |
| 8.1 | 6.1 | 3.12–3.15 |

Use the latest patches. Python 3.14 needs Django 5.2.8+ on the 5.2 series;
Python 3.15 needs Django 6.1.3+. Tox applies these minimums to each series.

Recheck upstream sources when upgrading:

- [Python lifecycles](https://devguide.python.org/versions/)
- [Django support](https://www.djangoproject.com/download/#supported-versions)
  and [Python compatibility](https://docs.djangoproject.com/en/6.1/faq/install/#what-python-version-can-i-use-with-django)
- [Wagtail support](https://github.com/wagtail/wagtail/wiki/Release-schedule)
  and [Django/Python compatibility](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions)

## Upgrading

Upgrade installations below Python 3.11, Django 5.2 or Wagtail 7.4 before using
this revision. Django is supplied through the Wagtail dependency.
Follow intermediate framework upgrade notes for host models and content;
tests on fresh databases do not verify an existing site's migration.

The package uses standard `wagtail.models.Page`. Wagtail 8 custom base page
models require separate adaptation of the redirect view and counter relation.

Django 6.1 uses `MAILERS` in the test site and sandbox; older versions use
`EMAIL_BACKEND`. See [Django's email migration guide](https://docs.djangoproject.com/en/6.1/topics/email/#migrating-email-to-mailers).
For the QR storage changes, see [host migration notes](../README.md#upgrading-from-stored-qr-assets).

## Databases and validation

Each of the 28 framework/interpreter combinations supports SQLite, PostgreSQL
and MySQL: 84 combinations in total.

CI runs eight jobs: lint/sandbox checks, five SQLite Python jobs, PostgreSQL and
MySQL. Tox's default selection contains 34 environments: all 28 SQLite
combinations and these three pairs on Python 3.14 for each server database:

| Django | Wagtail |
| --- | --- |
| 5.2 LTS | 7.4 LTS |
| 6.0 | 8.0 |
| 6.1 | 8.1 |

CI uses PostgreSQL 16 and MySQL 8.4. Django 6.1 requires PostgreSQL 15+,
MySQL 8.4+ or SQLite 3.37+, with psycopg2 2.9.9+ or mysqlclient 2.2.1+
for those drivers. See [database requirements](https://docs.djangoproject.com/en/6.1/ref/databases/).

Start server databases before running their environments. Tox sets `DATABASE`
from the factor and forwards `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`
and `DB_PORT`. Coverage files are separate per environment.

```bash
uv run --locked tox list
uv run --locked tox -f sqlite
uv run --locked tox -f postgres
uv run --locked tox -f mysql
uv run --locked tox -e py311-dj52-wt74-sqlite
uv run --locked tox -e py315-dj61-wt81-sqlite
```

To select all 84 combinations:

```bash
uv run --locked tox -e 'py{311,312,313,314}-dj52-wt{74,80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py{312,313,314}-dj60-wt{74,80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py{312,313,314}-dj61-wt{80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py315-dj61-wt81-{sqlite,postgres,mysql}'
```

Missing interpreters are skipped. Check installed versions and environment
summaries before claiming matrix coverage. The original 11 November 2026 local
validation covered SQLite only; see [PR #65's checks](https://github.com/nm-packages/wagtail-qrcode/pull/65/checks)
for subsequent results by revision.
