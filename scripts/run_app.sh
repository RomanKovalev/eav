#!/bin/sh

python3 manage.py migrate
python manage.py collectstatic --no-input
gunicorn --threads 4 --bind 0.0.0.0:8000 apexive.wsgi