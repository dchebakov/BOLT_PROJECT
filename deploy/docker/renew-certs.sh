#!/bin/bash

docker run --rm \
     -v /srv/bmstu-fun/keys/conf:/var/www/certbot \
     -v /srv/bmstu-fun/keys/letsencrypt:/etc/letsencrypt \
     certbot/certbot \
     	renew

docker service update --force solver_nginx
