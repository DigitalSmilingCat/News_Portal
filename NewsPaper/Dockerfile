FROM python:3.11-slim

RUN mkdir /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/

CMD gunicorn NewsPaper.wsgi:application -b 0.0.0.0:8000
EXPOSE 8000
