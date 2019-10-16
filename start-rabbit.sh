#!/usr/bin/env bash

# Assumes that RabbitMQ is installed
python3 -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
/usr/local/opt/rabbitmq/sbin/rabbitmq-server start