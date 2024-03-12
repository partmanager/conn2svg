FROM python:3.12-slim-bookworm

RUN apt update
RUN apt install make pylint -y

WORKDIR /mnt/conn2svg_backend/

ENV PYTHONPATH="/mnt/conn2svg_backend/src/"
COPY requirements-dev.txt /var/conn2svg_backend/
RUN pip install -r /var/conn2svg_backend/requirements-dev.txt
