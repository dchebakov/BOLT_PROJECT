#!/bin/bash

echo "Удаляем имеющиеся сертификаты"
rm -rf keys/letsencrypt/*

echo "Выпускаем новые"
docker run --rm \
     -v /srv/bmstu-fun/keys/conf:/var/www/certbot \
     -v /srv/bmstu-fun/keys/letsencrypt:/etc/letsencrypt \
     certbot/certbot \
          certonly --agree-tos --non-interactive --webroot \
          --webroot-path /var/www/certbot \
          --email "chad-d@mail.ru" -d bmstu.fun

docker service update --force solver_nginx

