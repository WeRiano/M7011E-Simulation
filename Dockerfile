FROM python:3.9.9-alpine3.15 as simulation
LABEL maintainer="m7011e"

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE Simulation.settings

COPY requirements.txt /requirements.txt
COPY Simulation /Simulation

WORKDIR /Simulation
EXPOSE 8000

RUN apk add build-base python3-dev py-pip jpeg-dev zlib-dev libressl-dev musl-dev libffi-dev
ENV LIBRARY_PATH=/lib:/usr/lib

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    chmod -R +x /scripts


ENV PATH="/py/bin:$PATH"