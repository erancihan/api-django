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

.PHONY: install
