import argparse
from avro import schema
from avro import io as avro_io
import io

import pika

from test_event_bodies import event_bodies


def send_event(exchange):
    """Send an event to publish at an input "exchange"."""

    # Get Avro schema, create serialized raw_bytes version of event body
    event_schema = schema.Parse(open(f"{exchange}.avsc", "rb").read())
    writer = avro_io.DatumWriter(event_schema)

    bytes_writer = io.BytesIO()
    encoder = avro_io.BinaryEncoder(bytes_writer)

    writer.write(event_bodies[exchange], encoder)
    raw_bytes = bytes_writer.getvalue()

    # create connection, declare exchange
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='fanout')

    # publish message, close connection
    channel.basic_publish(exchange=exchange, routing_key='', body=raw_bytes)
    connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-count', type=int, required=True)
    parser.add_argument('--exchange', type=str, choices=['profile_created_or_updated', 'large_event'], required=True)
    args = parser.parse_args()
    event_count, exchange = args.event_count, args.exchange

    sent = 0

    for i in range(event_count):
        send_event(exchange)
        print(f"send_count: {sent}")
        sent += 1
