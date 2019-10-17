FROM python:3.6.8-stretch

WORKDIR /rabbitmq-avro-demo
RUN python -m pip install avro-python3 pika
ENTRYPOINT ["python", "consumer.py"]
