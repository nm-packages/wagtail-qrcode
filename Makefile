.PHONY: list
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

migrate:
	@uv run manage.py migrate

admin:
	@echo "Creating superuser"
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')" | uv run manage.py shell

run:
	@uv run manage.py runserver 0.0.0.0:8000

test:
	@echo "Running tests..."
	@uv run coverage run manage.py test --deprecation all
	@uv run coverage report -m

mail:
	@echo "Starting mail server"
	@cp tests/local.py.example tests/local.py
	@docker run -d -p 8025:8025 -p 1025:1025 --name mailhog mailhog/mailhog

mail-stop:
	@echo "Stopping mail server"
	@docker stop mailhog
	@docker rm mailhog
