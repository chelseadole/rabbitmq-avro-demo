import argparse
from avro import schema
from avro import io as avro_io
import io

import pika

EXCHANGE_NAME = "profile_created_or_updated"
SCHEMA_FILE = "schema.avro"


def send_event(**kwargs):
    """Send a ProfileCreatedOrUpdated event."""

    event_body = {
        "full_name": "Chelsea Dole",
        "profile_id": 123456,
        "gender": "f",
        "zipcode": 98122,
        "ethnicity": "white",
        "height_feet": 5,
        "height_inches": 6,
        "religion": "atheist",
        "latitude": 1.0,
        "longitude": 2.0,
        "approved": True
    }

    # Get Avro schema, create serialized raw_bytes version of event body
    profile_updated_schema = schema.Parse(open(f"{EXCHANGE_NAME}.avsc", "rb").read())
    writer = avro_io.DatumWriter(profile_updated_schema)

    bytes_writer = io.BytesIO()
    encoder = avro_io.BinaryEncoder(bytes_writer)
    writer.write(event_body, encoder)

    raw_bytes = bytes_writer.getvalue()

    # create connection, declare exchange
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

    # publish message, close connection
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key='', body=raw_bytes)
    connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-count', type=int, required=True)
    args = parser.parse_args()
    event_count = args.event_count

    sent = 0

    for i in range(event_count):
        send_event()
        print(f"send_count: {sent}")
        sent += 1
