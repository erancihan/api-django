#!make
include .env
export $(shell sed 's/=.*//' .env)

SHELL := /bin/bash

clean:
	rm -rf .venv

venv-init:
	python3.10 -m venv .venv

install:
	. .venv/bin/activate; pip install --upgrade pip; pip install pipenv
	. .venv/bin/activate; PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	@echo "Setting up pre-commit hooks..."
	. .venv/bin/activate; pre-commit install

fresh: clean venv-init install

test:
	source ./.venv/bin/activate; \
	ENV_TARGET=TEST python server/manage.py test tests

gen-migrations:
	source ./.venv/bin/activate; \
	python server/manage.py makemigrations api

migrate:
	source ./.venv/bin/activate; \
	python server/manage.py migrate api

run:
	source ./.venv/bin/activate; \
	python server/manage.py runserver 8000

.PHONY: install
