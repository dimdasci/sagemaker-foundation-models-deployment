#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VIRTUALENV_DIR := ".venv"
PYTHON_INTERPRETER = python3

VALID_ENV_TYPES := dev qa staging prod

#################################################################################
# SETUP                                                                         #
#################################################################################

## Set up python interpreter environment 
create_environment:
	$(PYTHON_INTERPRETER) -m venv $(VIRTUALENV_DIR)
	@echo ">>> New virtualenv created. Activate with:\nsource $(VIRTUALENV_DIR)/bin/activate"

pip_upgrade:
	$(PYTHON_INTERPRETER) -m pip install --upgrade pip	

## Install Python Dependencies for development tools
requirements_dev: 
	$(PYTHON_INTERPRETER) -m pip install -r requirements-dev.txt

## Install Python Dependencies for application
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Install all Python Dependencies
install: pip_upgrade requirements_dev requirements


.PHONY: create_environment install pip_upgrade requirements_dev requirements

#################################################################################
# DEVELOPMENT COMMANDS                                                          #
#################################################################################

## Delete all compiled Python files

clean: clean_py clean_cdk

clean_py:
	find . -type f -name '._*' -delete
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

clean_cdk:
	rm -Rf ./cdk.out/asset*

## Format using Black
format: 
	isort src iac glue tests --profile black
	black src iac glue tests

## Lint using flake8
lint:
	flake8 src iac

## Run tests using pytest
test:
	pytest tests/

.PHONY: clean clean_py clean_cdk_out format lint test
