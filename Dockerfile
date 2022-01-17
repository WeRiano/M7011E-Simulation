FROM python:3.9.9-alpine3.15 as simulation
LABEL maintainer="m7011e"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt
COPY ./Simulation /app/Simulation

WORKDIR /app/Simulation

EXPOSE 8000

RUN apk add build-base python3-dev py-pip jpeg-dev zlib-dev libressl-dev musl-dev libffi-dev

RUN python -m venv /app/py && \
    /app/py/bin/pip install --upgrade pip && \
    /app/py/bin/pip install -r /app/requirements.txt && \
    chmod -R a+x /app

ENV PATH="/app/py/bin:$PATH"

ADD ./scripts/simulation_run.sh /app/Simulation
RUN chmod 755 simulation_run.sh

CMD ["./simulation_run.sh"]
