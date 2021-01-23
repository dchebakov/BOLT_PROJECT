#!/bin/bash
# Данный скрипт собирает docker конейнеры.
# Запускать из папки с проектом: ./deploy/tools/build.sh

source deploy/tools/get-images-versions.sh

echo "Собираем основной контейнер с версией ${VERSION}"
docker build \
     --tag=$MAIN_IMAGE_TAG \
     -f Dockerfile-main .

echo "Собираем nginx контейнер с версией ${VERSION}"
docker build \
     --tag=$NGINX_IMAGE_TAG \
     -f Dockerfile-nginx .

if [ "$SAVE_ARCHIVE" = "true" ]; then
     docker save -o main.tar $MAIN_IMAGE_TAG
     docker save -o nginx.tar $NGINX_IMAGE_TAG
fi;
