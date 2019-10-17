FROM python:3.6.8-stretch
RUN apt-get update
RUN apt-get upgrade -y

WORKDIR /rabbitmq-avro-demo
RUN python -m pip install avro-python3 pika
