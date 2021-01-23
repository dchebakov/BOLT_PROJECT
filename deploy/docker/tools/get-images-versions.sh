#!/bin/bash

export VERSION=$(git describe --abbrev=0)

# eu.gcr.io - ссылка docker-репозитория от gcloud (в Европе, так как указан поддомен eu)
# bmstu-fun - название проекта в gcloud
REPOSITORY=eu.gcr.io/bmstu-fun

export MAIN_IMAGE_TAG=$REPOSITORY/solver-main:$VERSION
export NGINX_IMAGE_TAG=$REPOSITORY/solver-nginx:$VERSION
