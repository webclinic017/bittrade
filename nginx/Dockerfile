FROM huakunshen/nginx-certbot

RUN rm /etc/nginx/sites-available/default

WORKDIR /app

COPY default.conf .

RUN cp default.conf /etc/nginx/sites-available/default
