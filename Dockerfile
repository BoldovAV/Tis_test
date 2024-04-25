FROM python:3

WORKDIR /core

COPY ./requirements.txt /core/

RUN pip install -r /core/requirements.txt

COPY . .
