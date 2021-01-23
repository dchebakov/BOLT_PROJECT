#!/bin/bash

domains=(bmstu.fun www.bmstu.fun)
rsa_key_size=4096
data_path="keys/letsencrypt"
email="chad-d@mail.ru"

conf_path="keys/conf"
if [ ! -e "$conf_path/options-ssl-nginx.conf" ] || [ ! -e "$conf_path/ssl-dhparams.pem" ]; then
  echo "### Скачиваем рекомендуемые TLS параметры ..."
  mkdir -p "$conf_path"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf > "$conf_path/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem > "$conf_path/ssl-dhparams.pem"
  echo
fi

if [ -d "$data_path/live" ]; then
  echo "Сертификаты уже существуют."
  exit
fi

echo "### Создаём фальшивые сертификаты для $domains ..."
path="$data_path/live/$domains"
mkdir -p "$path"

openssl req -x509 -nodes -newkey rsa:1024 -days 1\
  -keyout "$path/privkey.pem" \
  -out "$path/fullchain.pem" \
  -subj "/CN=localhost"
