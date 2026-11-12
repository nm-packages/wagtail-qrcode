.PHONY: list format lint
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

migrate:
	@python manage.py migrate

admin:
	@echo "Creating superuser"
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')" | python manage.py shell

run:
	@python manage.py runserver 0.0.0.0:8000

test:
	@echo "Running tests..."
	@coverage run manage.py test --deprecation all
	@coverage report -m

mail:
	@echo "Starting mail server"
	@cp tests/local.py.example tests/local.py
	@docker run -d -p 8025:8025 -p 1025:1025 --name mailhog mailhog/mailhog
	@make run

mail-stop:
	@echo "Stopping mail server"
	@docker stop mailhog
	@docker rm mailhog

format:
	@ruff check --fix .
	@ruff format .

lint:
	@ruff check .
	@ruff format --check .
