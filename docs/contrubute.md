# Contributing

## Development setup

### Clone this repo to your computer

```bash
git clone https://github.com/nickmoreton/wagtail-qrcode
```

## Setup a virtual environment

```bash
uv venv
```

Activate the virtual environment (optional):

```bash
source .venv/bin/activate
```

## Install the package into your virtual environment

```bash
uv pip install -e ".[development]"
```

## Setup the testing app

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

The app can be viewed at <http://localhost:8000>

You can log into the admin at <http://localhost:8000/admin> and use `admin` for the username & `admin` for the password.

## Setup a local mail server with docker

You can use [MailHog](docs/mailhog.md) to test email sending.

```bash
cp tests/local.py.example tests/local.py
docker run -it -p 8025:8025 -p 1025:1025 mailhog/mailhog
```

The mail-hog web interface will be available at `http://localhost:8025` **Before testing this feature** you may need to stop and start the django development server

With the test app set up: create a QRCode page and on the QRcode tab complete the field to send an email you can access the QR code sample page in the admin and add an email address before saving the page.

The email will show up in mail hog.

## Testing

The app uses django tests and has `tox` setup for running them against the compatible Wagtail and Django versions.

To run the tests:

```bash
uv run python manage.py test
```
