from avro import io as avro_io
from avro import schema
from io import BytesIO
import sys

import pika

EXCHANGE_NAME = "profile_created_or_updated"
SCHEMA_FILE = "schema.avro"


def receive_event():
    """Receive a ProfileCreatedOrUpdated event."""

    # create connection, declare exchange to consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')

    # get dynamically-created queue_name from exchange, and bind to it
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

    def callback(ch, method, properties, body):
        bytes_reader = BytesIO(body)
        decoder = avro_io.BinaryDecoder(bytes_reader)
        reader = avro_io.DatumReader(schema.Parse(open(f"{EXCHANGE_NAME}.avsc", "rb").read()))
        event_body = reader.read(decoder)
        print(event_body, f"   Size: {sys.getsizeof(event_body)} bytes")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


if __name__ == "__main__":
    receive_event()
