#!/bin/bash

echo "Применяем миграции"
python src/manage.py migrate

echo "Запускаем сервер"
uwsgi --ini deploy/uwsgi.ini
