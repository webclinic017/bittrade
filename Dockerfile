FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV REDIS_CHANNEL=redis_channel
ENV DEBUG 1

EXPOSE 8000
EXPOSE 80

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate