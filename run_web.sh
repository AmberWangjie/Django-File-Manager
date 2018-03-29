#!/usr/bin/env bash

cd django_file_manager/
python3 manage.py migrate
python3 manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000

#access container: docker-compose exec web bash
#run without accessing container: docker-compose exec web python3 manage.py migrate/test/shell
