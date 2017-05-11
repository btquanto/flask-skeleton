# Flask-Skeleton

A skeleton for developing flask applications

# Running

First, make sure that you have created a logs

## Using docker

1. Using `docker run`

    ```
    docker run -dv `pwd`:/src \
        -p 8000:8000 \
        -e GUNICORN_CONFIG_FILE=scripts/gunicorn_config.py \
        btquanto/docker-flask
    ```

2. Using `docker-compose`

    ```
    docker-compose up -d
    ```

    Edit `docker-compose.yml` as fit

## Using virtualenv

* Create a new virtual environment

    ```
    virtualenv .env
    ```

* Create a bootstrap script

    ```
    cp scripts/flask.sh.template scripts/flask.sh
    ```

    Edit `scripts/flask.sh` and change the virtual environment path

    ``` bash
    #!/bin/bash

    set -e

    bin_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
    cd "$bin_dir"

    source .env/bin/activate
    pip install -U pip
    pip install -r requirements.txt

    exec gunicorn --config ./scripts/gunicorn_config.py -w 1 app:app

    ```

    Add execution permission to `flask.sh`

    ```
    chmod +x scripts/flask.sh
    ```

* Run the flask app

    ```
    ./scripts/flask.sh
    ```

# Configuration

1. Configuring GUnicorn

    ```
    cp scripts/gunicorn_config.py.template scripts/gunicorn_config.py
    ```

    Edit `scripts/gunicorn_config.py` as fit

2. Configuring flask:

    ```
    cp flaskconfig.py.template flaskconfig.py
    ```

    Edit `flaskconfig.py` as fit
