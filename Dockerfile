# syntax=docker/dockerfile:1
FROM python:3.10-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

FROM base AS python-deps
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN pipenv install gunicorn

FROM base AS runtime
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /code
COPY ./server /code/
RUN chmod +x run.sh

RUN python manage.py collectstatic --noinput --clear

EXPOSE 80

CMD [ "./run.sh" ]
