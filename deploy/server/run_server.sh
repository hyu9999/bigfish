#!/bin/sh

set -e

export PYTHONPATH=$PYTHONPATH:.
export DJANGO_SETTINGS_MODULE=server_settings

case "$1" in
    server)
        mkdir -p /opt/server/media
        mkdir -p /opt/server/static

        wait_for_psql.py -u "${POSTGRES_USER}" -w "${POSTGRES_PASSWORD}" -h postgres

        manage.py collectstatic --no-input --no-color
        manage.py migrate --no-input --no-color

        gunicorn -c server-conf.py bigfish.apps.bigfish.wsgi
        ;;

    *)
        $@
esac
