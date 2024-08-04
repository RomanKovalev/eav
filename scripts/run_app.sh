#!/bin/sh

cd apexive
python3 manage.py migrate
python manage.py collectstatic --no-input
python manage.py runserver 0:8000