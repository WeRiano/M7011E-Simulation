FROM nginx:stable-alpine
LABEL maintainer="m7011e"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params

ENV BACKEND_HOST=simulation

RUN touch /etc/nginx/conf.d/default.conf

CMD["/run.sh"]