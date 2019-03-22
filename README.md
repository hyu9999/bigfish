# Big Fish

This repository contains backend for Big Fish project.


## Quickstart

0. Clone this repository.

1. Create virtual environment (with for example
   [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):

        mkvirtualenv -p /usr/bin/python3.5 bigfish-venv

2. Install package in *develop* mode:

        pip install -e .

3. Initialize database:

        manage.py migrate

4. Load some initial data:

        manage.py loaddata quickstart

5. Run development server:

        manage.py runserver 
        manage.py runserver 192.168.1.179:8000

6. Visit webpage at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).


Hint: Place `local_settings.py` in your `PYTHONPATH` to alter default settings
during development process.


## Using Docker

0. Login to the Docker Hub:

        docker login

1. Build project and docker images with:

        make

2. Execute server using Docker Compose:

        docker-compose --file deploy/docker-compose.yml up -d

## Production

1. Copy `deploy/docker-compose.yml` on the host machine.

2. Configure `docker-compose.yml` as necessary.

3. Execute service:

        docker-compose --file <path>/docker-compose.yml up -d

    For example:

        docker-compose --file /opt/bigfish/docker-compose.yml up -d
