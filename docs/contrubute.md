# Contributing

## Branches and pull requests

`main` is the default branch and the integration branch for ongoing work.
Create working branches from an up-to-date `main` and target pull requests
at `main`. This applies to features, bug fixes, documentation, maintenance,
and release preparation.

The former `release` branch is retired from active development.
Prepare releases through pull requests into `main`, then create release tags
from the reviewed commits on `main`. Use the existing tag format, such as
`2.1.1`.

For an existing checkout, start new work with:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c improve-qr-code-preview
```

Choose a branch name that describes the change. Confirm the pull request's base
branch is `main` before submitting it.

Use the [pull request template](../.github/pull_request_template.md) to explain
the problem, resulting behavior, and validation commands with their results.
Remove sections that do not apply. Include compatibility or upgrade notes when
support changes, and before/after screenshots for admin interface changes.

Keep the PR title and description aligned with the complete final diff. When
adding work to an existing PR, update its description and validation results as
part of the same push. Identify the commit or revision for linked CI results so
earlier passing checks are not mistaken for validation of the latest changes.

Add an entry under `Unreleased` in [CHANGELOG.md](../CHANGELOG.md) for notable
features, fixes, compatibility changes, and contributor workflow changes.
Describe the outcome and any required action, using the existing style. Keep
entries current as the PR grows. Trivial edits need no entry; explain in the PR
when a changelog update is unnecessary. Release versions and dates are added
during release preparation.

## Development setup

### First clone this repo to your computer

```bash
git clone --branch main https://github.com/nm-packages/wagtail-qrcode
```

## Setup a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install the package into your virtual environment

```bash
pip install -e ".[development,testing]"
```

## Setup the testing app

```bash
make migrate && make admin && make run
```

The app can be viewed at <http://localhost:8000>

You can log into the admin at <http://localhost:8000/admin> and use `admin` for the username & `admin` for the password.

## Other commands

You can use the commands in the Make file to conveniently run various commands.

- `make migrate` run migrations
- `make run` run the development server
- `make test` run the tests
- `make admin` to quickly setup a superuser account with the above login details.
- `make lint` to run pre-commit --all-files
- `make mail` to run a [docker container](mailhog.md) for `MailHog`

## Testing

The app uses django tests and has `tox` setup for running them against the compatible Wagtail and Django versions.

Run:

```bash
tox
```
