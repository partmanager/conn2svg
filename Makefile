up:
	sudo docker compose up conn2svg_backend
.PHONY: up

build:
	sudo docker compose up --build conn2svg_backend
.PHONY: build

clean:
	sudo docker compose down -v
.PHONY: clean

terminal:
	sudo docker exec -it conn2svg_backend bash
.PHONY: terminal

docs:
	make tests
	sphinx-build -M html docs/ docs/_build/
.PHONY: docs

doctests:
	python -m doctest -v docs/index.rst
.PHONY: doctests

unittests:
	python tests/test_conn2svg.py
.PHONY: unittests

tests:
	make unittests
	make doctests
.PHONY: tests

versions:
	python --version
	pip freeze
.PHONY: versions

freeze:
	pip freeze > requirements.txt
.PHONY: freeze
