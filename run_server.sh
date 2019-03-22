#!/bin/sh
#杀掉所有 gunicorn进程
#killall gunicorn
#杀掉所有包含有关键字 “106.15.136.219:8001” 的进程
ps -ef|grep 192.168.3.5:8002|grep -v grep|cut -c 9-15|xargs kill -9
# ps -ef|grep 192.168.3.5:8003|grep -v grep|cut -c 9-15|xargs kill -9
ps -ef|grep "8008 -b 192.168.3.5"|grep -v grep|cut -c 9-15|xargs kill -9
ps -ef|grep "bigfish/bin/manage.py runworker"|grep -v grep|cut -c 9-15|xargs kill -9


set -e

export PYTHONPATH=$PYTHONPATH:.
export DJANGO_SETTINGS_MODULE=server_settings



mkdir -p /home/www/bigfish_server/media
mkdir -p /home/www/bigfish_server/static

#wait_for_psql.py -u "${POSTGRES_USER}" -w "${POSTGRES_PASSWORD}" -h postgres
# manage.py collectstatic --no-input --no-color
echo ====================================================collectstatic 
# manage.py collectstatic --no-input --no-color
echo ====================================================makemigrations
# manage.py makemigrations
echo ====================================================migrate
# manage.py migrate
echo ====================================================start server
gunicorn --timeout 100 --keep-alive 100 -w 4 -b 192.168.3.5:8002 bigfish.apps.bigfish.wsgi
# gunicorn --timeout 100 --keep-alive 100 -w 4 -b 192.168.3.5:8003 bigfish.apps.bigfish.wsgi

nohup daphne bigfish.apps.bigfish.asgi:channel_layer -p 8008 -b 192.168.3.5 >/dev/null 2>&1 &
nohup manage.py runworker >/dev/null 2>&1 &
