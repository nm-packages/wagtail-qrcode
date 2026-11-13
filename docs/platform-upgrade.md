# Platform compatibility and upgrade notes

## Rolling support policy

Follow the [repository support policy](../AGENTS.md#platform-support-policy)
when refreshing the platform:

- Support every stable Python release that has not reached upstream end of life,
  including releases receiving security fixes only. Exclude prereleases.
- For Django and Wagtail independently, support the latest stable release and
  every intervening feature release back through the preceding LTS, inclusive.
  When the latest stable release is itself an LTS, retain the previous LTS too.
- Select only combinations supported by Python and both frameworks. A Python
  release need not work with every framework release to remain supported.
- Apply this policy during upgrades, including removing versions outside the
  window. Explicit user targets override the default policy. Align metadata,
  dependency minimums, tox, CI, formatter targets and contributor guidance.

As of November 2026, this means:

| Component | Before this upgrade | After this upgrade |
| --- | --- | --- |
| Python | 3.9–3.13 | 3.11–3.15 |
| Django | 4.2, 5.0, 5.1 | 5.2 LTS, 6.0, 6.1 |
| Wagtail | 5.2, 6.0–6.3 | 7.4 LTS, 8.0, 8.1 |

Python 3.9 and 3.10 are EOL. Django 5.2 and Wagtail 7.4 are the LTS
boundaries preceding the current stable releases. These are rolling boundaries,
not permanent minimum versions: verify upstream releases and lifecycle dates
again on the next upgrade.

## Compatible combinations

The supported combinations below can be used with SQLite, PostgreSQL and MySQL:
28 combinations per backend, 84 in total. By default, tox and CI run all 28
SQLite combinations and three representative combinations for each server
database, as described under [databases and validation](#databases-and-validation).

| Wagtail | Django | Python |
| --- | --- | --- |
| 7.4 LTS | 5.2 LTS | 3.11–3.14 |
| 7.4 LTS | 6.0 | 3.12–3.14 |
| 8.0 | 5.2 LTS | 3.11–3.14 |
| 8.0 | 6.0, 6.1 | 3.12–3.14 |
| 8.1 | 5.2 LTS | 3.11–3.14 |
| 8.1 | 6.0 | 3.12–3.14 |
| 8.1 | 6.1 | 3.12–3.15 |

Use the latest patch release of each series. Python 3.14 requires Django 5.2.8+
when using Django 5.2, and Python 3.15 requires Django 6.1.3+. The tox factors
use those patch minimums for the whole corresponding Django series.

Evidence for the current selection:

- [Python release lifecycles](https://devguide.python.org/versions/).
- [Django releases and LTS support](https://www.djangoproject.com/download/#supported-versions)
  and [Python compatibility](https://docs.djangoproject.com/en/6.1/faq/install/#what-python-version-can-i-use-with-django).
- [Wagtail release schedule and LTS support](https://github.com/wagtail/wagtail/wiki/Release-schedule)
  and [Django/Python compatibility](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions).

## Upgrade considerations

Installations below Python 3.11, Django 5.2 or Wagtail 7.4 must upgrade before
using this package revision. Wagtail supplies the Django dependency; the package
requires Wagtail 7.4+ and Python 3.11+. The compatibility table still determines
which framework combinations to use.

The local exercise started with Python 3.13 / Django 5.1 / Wagtail 6.3.
It checked Wagtail 6.4 and 7.0 on Django 5.1, switched to Django 5.2 on Wagtail
7.0, then checked each Wagtail release through 7.4. From there it checked Django
6.0, Wagtail 8.0, Django 6.1, Python 3.14, Wagtail 8.1 and Python 3.15 in that
order, keeping each transition compatible. Intermediate versions are diagnostic
steps; they are not part of the final support matrix.

Each check uses a separate environment and a fresh test database. This is not an
in-place migration of an existing site. Host sites must also follow each
intermediate framework release's upgrade notes for their models, content and
customizations.

No required changes were found to the package's existing publishing hooks or
field panel APIs. A rendering test now covers the QR preview, usage count,
document field and recipient field. The example site and sandbox email configuration
use Django 6.1's `MAILERS` setting on that release and retain `EMAIL_BACKEND` for
Django 5.2 and 6.0. Host sites should follow
[Django's email migration guidance](https://docs.djangoproject.com/en/6.1/topics/email/#migrating-email-to-mailers).

Wagtail 8's optional custom base page models require separate adaptation of the
redirect view, which currently queries `wagtail.models.Page`. This exercise
covers sites using the standard base page model. New optional CMS features are
outside this upgrade's scope. The example site's API v2 remains supported in
Wagtail 8.1; its announced deprecation begins in Wagtail 8.2.

## Databases and validation

CI uses PostgreSQL 16 and MySQL 8.4. Django 6.1 requires PostgreSQL 15+ or
MySQL 8.4+, SQLite 3.37+, and psycopg2 2.9.9+ or mysqlclient 2.2.1+ for the
selected drivers. See the [Django database requirements](https://docs.djangoproject.com/en/6.1/ref/databases/).
These CI servers also support the retained Django releases.

CI runs seven jobs: five Python jobs covering all 28 SQLite environments, one
PostgreSQL job and one MySQL job. Each server database job uses Python 3.14 and
runs the full test suite on these three Django/Wagtail pairs:

| Django | Wagtail |
| --- | --- |
| 5.2 LTS | 7.4 LTS |
| 6.0 | 8.0 |
| 6.1 | 8.1 |

This selects 34 environments per workflow run, covering every supported Django
and Wagtail release on both server databases. Python/driver combinations outside
this selection are not covered by CI. Plain `uv run --locked tox` uses the same 34 environments;
CI selects from this list by Python version and database. All 84 supported
combinations remain available through explicit `tox -e` selections for release
checks and database-specific investigations.

Tox sets `DATABASE` from its database factor and forwards `DB_*` connection
settings. Coverage files are isolated per environment. Start database services
before invoking the PostgreSQL or MySQL environments.

The test site enables `django.contrib.postgres` when PostgreSQL is selected,
so Django can validate Wagtail's PostgreSQL search fields and indexes. Hook
tests check the generated document's identity and deletion without assuming
that database sequences reset between tests.

```bash
uv run --locked tox list
uv run --locked tox -f sqlite
uv run --locked tox -f postgres
uv run --locked tox -f mysql
uv run --locked tox -e py311-dj52-wt74-sqlite
uv run --locked tox -e py315-dj61-wt81-sqlite
uv run --locked tox -e py315-dj61-wt81-postgres,py315-dj61-wt81-mysql
```

To run all 84 supported combinations explicitly:

```bash
uv run --locked tox -e 'py{311,312,313,314}-dj52-wt{74,80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py{312,313,314}-dj60-wt{74,80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py{312,313,314}-dj61-wt{80,81}-{sqlite,postgres,mysql}'
uv run --locked tox -e 'py315-dj61-wt81-{sqlite,postgres,mysql}'
```

Tox skips missing interpreters by default. Inspect summaries and installed
versions before treating a run as evidence for a combination. Black's syntax
target is Python 3.11; formatter and linter pins are unchanged.

Local validation on 11 November 2026:

- `tox -f sqlite`: all 28 environments passed, 27 tests each, with no skipped
  interpreters. The installed Python versions were 3.11.14, 3.12.12, 3.13.18,
  3.14.10 and 3.15.2; Django versions were 5.2.19, 6.0.10 and 6.1.3; Wagtail
  versions were 7.4.4, 8.0.1 and 8.1, in the combinations above.
- `make test` on Python 3.15.2 / Django 6.1.3 / Wagtail 8.1 passed all
  27 tests, with 81% package branch coverage.
- `python manage.py check` and `python manage.py makemigrations --check --dry-run`
  passed on the lowest and highest combinations. No model changes were detected.
  The existing `staticfiles.W004` warning remains because `tests/static` is absent.
- Pre-commit hooks passed for changed files. All five changed skills passed
  `quick_validate.py`; local documentation links and CI/tox selection were checked.
- Source and wheel distributions built and passed `twine check`. The wheel
  installed into a separate Python 3.15.2 environment with Django 6.1.3 and
  Wagtail 8.1; `pip check`, metadata and bundled template checks passed.
  Setuptools reports existing license metadata deprecations during the build.
- PostgreSQL and MySQL integration runs were not performed: neither database
  service nor the Docker daemon was running locally. Their 56 matrix entries
  were unverified in this initial local run; SQLite results do not establish
  database backend coverage. See [PR #65's checks](https://github.com/nm-packages/wagtail-qrcode/pull/65/checks)
  for subsequent database validation of each revision.
