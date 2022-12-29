#!make
include .env
export $(shell sed 's/=.*//' .env)

SHELL := /bin/bash


install:
	source ./.venv/bin/activate; \
	pipenv install --dev; \
	pre-commit install

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
