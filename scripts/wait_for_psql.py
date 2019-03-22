#!/usr/bin/env python
import time

import click
import psycopg2


@click.command()
@click.option('-u', '--user', required=True)
@click.option('-w', '--password', required=True)
@click.option('-d', '--dbname', default='postgres', help='default: postgres')
@click.option('-h', '--host', required=True)
@click.option('-p', '--port', default=5432, help='default: 5432')
@click.option('-c', '--try-count', default=15, help='default: 15')
def wait_for_psql(user, password, dbname, host, port, try_count):
    """
    Wait for PostgreSQL instance by trying to connect to it.

    It will exit immediately if host was not found (exit code will be set to 2)
    or if connection was made but provided credentials were wrong (exit code
    will be set to 3).

    Check exit code for failure.
    """
    print('Waiting for PostgreSQL to start...')
    for _ in range(try_count):
        try:
            conn = psycopg2.connect(
                user=user,
                password=password,
                dbname=dbname,
                host=host,
                port=port
            )

            cur = conn.cursor()
            cur.execute('SELECT 1;')

            cur.close()
            conn.close()
            exit(0)

        except psycopg2.Error as e:
            # Psycopg2 doesn't fill exception with any usefull error codes, so
            # we have to extract it from text message.
            message = str(e)
            if 'could not translate host name' in message:
                exit(2)
            elif 'password authentication failed' in message:
                exit(3)
            time.sleep(1)

    print("Couldn't connect do PostgreSQL on {}:{}".format(host, port))
    exit(1)


if __name__ == '__main__':
    wait_for_psql()
