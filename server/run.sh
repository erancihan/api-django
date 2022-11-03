#!/bin/bash

if [ -f ".venv/bin/activate" ]; then source .venv/bin/activate; fi

IS_CELERY_RUN=0
IS_DEV=0

if [[ -z "${RUN_FLAG_CELERY}" ]]; then
  IS_CELERY_RUN=0
else
  IS_CELERY_RUN=1
fi

for key in "$@"; do
  case $key in
    --celery)
      IS_CELERY_RUN=1
      shift # pass argument
    ;;
    --dev)
      IS_CELERY_RUN=0
      IS_DEV=1
      shift # pass argument
    ;;
    *)  # default
        # skip
    ;;
  esac
done

if [[ "$IS_CELERY_RUN" == 1 ]]; then
    celery -A server worker --loglevel=INFO -E --beat --scheduler=django_celery_beat.schedulers:DatabaseScheduler
else
    python manage.py migrate
    if [[ "$IS_DEV" == 1 ]]; then
        python manage.py runserver 0.0.0.0:8080
    else
        gunicorn -R --workers=1 --timeout=120 --bind=0.0.0.0:80 server.wsgi
    fi
fi
