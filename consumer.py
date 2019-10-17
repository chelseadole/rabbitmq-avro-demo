import argparse
from avro import io as avro_io
from avro import schema
from io import BytesIO
import sys
import time
import pika


def receive_event(exchange):
    """Receive events from a declared exchange."""
    # create connection, declare exchange to consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='fanout')

    # get dynamically-created queue_name from exchange, and bind to it
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)

    def callback(ch, method, properties, body):
        start_time = time.clock()
        bytes_reader = BytesIO(body)
        decoder = avro_io.BinaryDecoder(bytes_reader)
        reader = avro_io.DatumReader(schema.Parse(open(f"schemas/{exchange}.avsc", "rb").read()))
        event_body = reader.read(decoder)
        time.sleep(0.1)  # Mock feature computing time
        print(f"Event received:"
              f"size: {sys.getsizeof(event_body)} bytes,"
              f"time: {time.clock() - start_time} secs")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--exchange', type=str, choices=['profile_created_or_updated', 'large_event'], required=True)
    args = parser.parse_args()
    exchange = args.exchange

    receive_event(exchange)
