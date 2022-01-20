FROM python:3.9-alpine3.13 as simulation
LABEL maintainer="m7011e"

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE simulation.settings

COPY ./requirements.txt /app/requirements.txt
COPY simulation /app/simulation

WORKDIR /app/simulation

EXPOSE 8000

#RUN apk add build-base python3-dev py-pip jpeg-dev zlib-dev libressl-dev musl-dev libffi-dev

RUN apk add build-base python3-dev py-pip

RUN python -m venv /app/py && \
    /app/py/bin/pip install --upgrade pip && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base musl-dev linux-headers && \
    /app/py/bin/pip install -r /app/requirements.txt && \
    apk del .tmp-deps && \
    chmod -R a+x /app

ENV PATH="/app/py/bin:$PATH"

ADD ./scripts/simulation_run.sh /app/simulation
RUN chmod 755 simulation_run.sh

CMD ["./simulation_run.sh"]
