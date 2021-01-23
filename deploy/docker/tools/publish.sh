#!/bin/bash
# Данна команда публикует докер контейнеры в gcloud репозиторий.
# Запускать из папки с проектом: ./tools/publish.sh

source ./deploy/tools/get-images-versions.sh

if [ "$LOAD_IMAGE_ARCHIVE" = "true" ]; then
     docker load -i images/main.tar
     docker load -i images/nginx.tar
fi;

docker push $REPOSITORY/solver-main:$VERSION
docker push $REPOSITORY/solver-nginx:$VERSION
