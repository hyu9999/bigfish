FROM python:3.5-slim

WORKDIR /usr/src
ADD . /usr/src

ARG PY_PKG_SRC

RUN pip install --no-cache ${PY_PKG_SRC:--r requirements.txt}

ENTRYPOINT ["./run_server.sh"]
