################################################################################
#  Setup
include env

#-------------------------------------------------------------------------------

lint: ## Run ruff to lint the code
	uv run ruff format
	uv run mypy src/

#-------------------------------------------------------------------------------

format: ## Run ruff to format the code
	uv run ruff check --fix

#-------------------------------------------------------------------------------

unit-test: ## Run the unit test
	@echo "🚀 Testing code..."
	uv run pytest --cov=my_package \
	--cov-report=term-missing tests/unit

#-------------------------------------------------------------------------------

integration-test: ## Run the integration test
	uv run pytest \
	tests/unit tests/integration

#-------------------------------------------------------------------------------

.PHONY: clean
clean: ## Clean up from the last app run before the next
	- rm /mnt/nfs_storage/${ENVIRONMENT}/tro_investing/logs/*.log
#
	- rm /mnt/nfs_storage/${ENVIRONMENT}/tro_investing/reports/*.rpt
#  @rm src/${app_name}/logs/*.log
#  @rm src/${app_name}/reports/*.rpt
#  @mv src/${app_name)/stage/*.xlsx.bkp src/${app_name)/stage/*.xlsx
--------------------: ## ----------------------------------

setup: ## Set up the pre-commit environment
	uv sync
	uv run pre-commit install

--------------------: ## ----------------------------------


.PHONY: build-image
build-image: ## Build the Docker image
	@echo "🚀  Building our docker image..."
	@export DOCKER_BUILDKIT=1
	#  docker image build --no-cache -t jasmit/$(app_name):$(app_version) .
	docker image build -t jasmit/$(app_name):$(app_version) .
	#  @echo "🚀  Running docker scout quickview..."
	#  @docker scout quickview
	#  @echo "🚀  Running docker scout cves..."
	#  @docker scout cves local://jasmit/${app_name}:$(app_version)

#-------------------------------------------------------------------------------

.PHONY: start-service
start-service: ## Start a service on the swarm cluster using the image
	@echo "🚀  Starting the service ..."
	ansible-playbook -i ansible/inventory/test_swarm.yaml ansible/playbooks/start_$(ENVIRONMENT)_service.yaml

################################################################################

.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv sync --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: build-wheel
build-wheel: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean up any crap from previous builds
	@echo "🚀 Removing any crap from previous builds..."
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing: Dry run."
	@uvx --from build pyproject-build --installer uv
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@echo "🚀 Generating local PDF documentation"
	@pandoc --toc=true -o '/Volumes/SharedSpace/Users/jeff/Project Documentation/Active/TROLoad System Guide.pdf' 'docs/TROLoad System Guide.md'
	@pandoc --toc=true -o "/Volumes/SharedSpace/Users/jeff/Project Documentation/Active/TROLoad User's Guide.pdf" "docs/TROLoad User's Guide.md"
	@uv run mkdocs serve

.PHONY: dr-get-ip
dr-get-ip:
	@echo "🚀  Cionnecting to running docker container..."
	@docker inspect --format '{{ .NetworkSettings.IPAddress }}' jasmit/troloadtrans:latest

.PHONY: dr-status
dr-status:
	@echo "🚀  Checking the status of all docker containers..."
	@docker ps --all

.PHONY: dr-push-image
dr-push-image:
	docker push jasmit/troloadtrans:${app_version}

################################################################################

.PHONY: help
help:
	@uv run --no-sync python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
