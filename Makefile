project_name:=todo-list
cfn_dir:=stack/cfn
dist_dir:=dist

# parameters
api_debug:=true

# Docker
.PHONY: up
up: create-dev-env
	@docker compose up --build -d

.PHONY: down
down:
	@docker compose down -v

.PHONY: create-dev-env
create-dev-env:
	@test -e .env || cp .env.example .env

# CI/CD
.PHONY: ci-%
ci-%: create-dev-env
	@docker compose run --rm dev sh -c 'make $*'

.PHONY: deploy
deploy:
	@rain deploy -y $(cfn_dir)/api.yaml $(project_name) --params Debug=$(api_debug)

# Dev
.PHONY: test
test: lint-actions test-cfn test-py

.PHONY: build
build: cleanup-build build-py

.PHONY: cleanup-build
cleanup-build:
	@rm -rf ${dist_dir}
	@mkdir -p ${dist_dir}

## CFN
.PHONY: test-cfn
test-cfn: format-cfn lint-cfn

.PHONY: format-cfn
format-cfn:
	@rain fmt $(cfn_dir)/*.yaml -w

.PHONY: lint-cfn
lint-cfn:
	@cfn-lint $(cfn_dir)/**/*.yaml

## Lambda
.PHONY: build-py
build-py:
	@# https://github.com/python-poetry/poetry/issues/1937
	@poetry build -f wheel -o ${dist_dir}/wheel
	@pip install ${dist_dir}/wheel/*.whl -t ${dist_dir}/app

.PHONY: test-py
test-py: full-install type-py lint-py unit-py

.PHONY: lint-py
lint-py:
	@# run both ruff format and lint. https://github.com/astral-sh/ruff/issues/8232
	@poetry run ruff format .
	@poetry run ruff check .

.PHONY: type-py
type-py:
	@poetry run mypy .

.PHONY: unit-py
unit-py:
	@poetry run pytest

.PHONY: full-install
full-install:
	@poetry install

## Action
lint-actions:
	@actionlint

## Local
.PHONY: server
server: create-table
	@cd src && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

.PHONY: create-table
create-table:
	@mkdir -p ${dist_dir}/dynamodb
	@aws dynamodb create-table --table-name ${DB_TASKS_TABLE} \
		--attribute-definitions AttributeName=id,AttributeType=S \
		--key-schema AttributeName=id,KeyType=HASH \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
		--endpoint-url ${DB_HOST} > /dev/null  2>&1 || echo "Table already exists. Skipping creation."
