#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VIRTUALENV_DIR := ".venv"
PYTHON_INTERPRETER = python3

VALID_PROFILES := dev qa staging prod

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
	isort src stack construct --profile black
	black src stack construct

## Lint using flake8
lint:
	flake8 src stack construct

## Run tests using pytest
test:
	pytest tests/

.PHONY: clean clean_py clean_cdk_out format lint test

#################################################################################
# AWS DEPLOYMENT COMMANDS                                                       #
#################################################################################

# validate if profile is set and has a valid value
validate_profile:
ifndef profile
	$(error profile is not set. Please provide the profile argument, e.g., make deploy profile=dev)
endif
ifeq (,$(filter $(profile),$(VALID_PROFILES)))
	$(error Invalid profile. Allowed values are: $(VALID_PROFILES))
endif
	$(eval ACCOUNT := $(shell aws sts get-caller-identity --query "Account" --output text --profile $(profile)))
	$(eval REGION := $(shell aws configure get region --profile $(profile)))
	@echo "Deploying to $(profile) environment in region $(REGION) and account $(ACCOUNT)"

deploy: validate_env_type
# set environment variable JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1 to suppress warning
	@echo "   ... AWS CDK deploy started"
	@JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=1 cdk deploy \
	--profile $(profile) '**'
	@echo "   ... AWS CDK deploy completed"

destroy: validate_env_type
	@echo "   ... AWS CDK destroy started"
	cdk destroy --profile $(env_type) '**'
	rm -Rf ./cdk.out/asset*
	@echo "   ... AWS CDK destroy completed"

.PHONY: validate_env_type deploy destroy sync_assets