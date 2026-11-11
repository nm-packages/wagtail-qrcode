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
- `make mail` to run a [docker container](docs/mailhog.md) for `MailHog`

## Testing

The app uses django tests and has `tox` setup for running them against the compatible Wagtail and Django versions.

Run:

```bash
tox
```
