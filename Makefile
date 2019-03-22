# Quick and dirty way to build containers.

all: clean build

build:
	python setup.py bdist_wheel
	cp dist/bigfish*.whl deploy/server
	docker-compose -f deploy/docker-compose.yml build

clean:
	rm -rf build dist deploy/server/*.whl
