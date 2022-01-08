server {
    listen 8000;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass ${BACKEND_HOST}:9000
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}