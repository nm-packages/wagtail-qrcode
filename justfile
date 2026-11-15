# List available contributor commands (also the default recipe).
list:
    @"{{ just_executable() }}" --list

# Apply migrations to the legacy test fixture site.
migrate:
    @uv run --locked python manage.py migrate

# Create the local admin/admin user in the legacy test fixture site.
admin:
    @echo "Creating superuser"
    @echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')" | uv run --locked python manage.py shell

# Serve the legacy test fixture site on port 8000.
run:
    @uv run --locked python manage.py runserver 0.0.0.0:8000

# Run package tests with branch coverage and report missing lines.
test:
    @echo "Running tests..."
    @uv run --locked coverage run manage.py test tests --deprecation all
    @uv run --locked coverage report -m

# Fix lint and format Python, Markdown code blocks and this justfile.
format:
    @uv run --locked ruff check --fix .
    @uv run --locked ruff format .
    @"{{ just_executable() }}" --fmt

# Check lint and formatting without changing files.
lint:
    @uv run --locked ruff check .
    @uv run --locked ruff format --check .
    @"{{ just_executable() }}" --fmt --check

# Install the locked contributor dependencies.
sync:
    @uv sync --locked

# Initialize or update the persistent sandbox, preserving existing content.
sandbox-setup:
    @uv run --locked python sandbox/manage.py setup_sandbox

# Serve the persistent sandbox on port 8000.
sandbox-run:
    @uv run --locked python sandbox/manage.py runserver 0.0.0.0:8000

# Run sandbox integration tests with isolated database and media.
sandbox-test:
    @uv run --locked python sandbox/manage.py test home

# Delete ALL sandbox data and restore examples; stop the server first.
sandbox-reset:
    @uv run --locked python sandbox/reset.py --yes
    @"{{ just_executable() }}" sandbox-setup

# Print the latest captured email and extract its EPS attachment.
sandbox-email:
    @uv run --locked python sandbox/read_email.py
