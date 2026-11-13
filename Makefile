.PHONY: list sync migrate admin run test format lint
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

migrate:
	@uv run --locked python manage.py migrate

admin:
	@echo "Creating superuser"
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')" | uv run --locked python manage.py shell

run:
	@uv run --locked python manage.py runserver 0.0.0.0:8000

test:
	@echo "Running tests..."
	@uv run --locked coverage run manage.py test tests --deprecation all
	@uv run --locked coverage report -m

format:
	@uv run --locked ruff check --fix .
	@uv run --locked ruff format .

lint:
	@uv run --locked ruff check .
	@uv run --locked ruff format --check .

sync:
	@uv sync --locked

.PHONY: sandbox-setup sandbox-run sandbox-test sandbox-reset sandbox-email
sandbox-setup:
	@uv run --locked python sandbox/manage.py setup_sandbox

sandbox-run:
	@uv run --locked python sandbox/manage.py runserver 0.0.0.0:8000

sandbox-test:
	@uv run --locked python sandbox/manage.py test home

# Explicitly destructive: stop the sandbox server before invoking this target.
sandbox-reset:
	@uv run --locked python sandbox/reset.py --yes
	@$(MAKE) sandbox-setup

sandbox-email:
	@uv run --locked python sandbox/read_email.py
