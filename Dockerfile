FROM python:3.7-slim

RUN apt-get update && apt-get install -y vim git gcc g++ npm

COPY ./backend/requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /code

ENTRYPOINT /code/docker/docker-entrypoint.sh
