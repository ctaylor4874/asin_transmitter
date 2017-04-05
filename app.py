import webbrowser
import os
from contextlib import closing
from boto import sqs

BOTO_REGION = 'us-east-1'
BOTO_QUEUE_NAME = 'asin-viewing-queue'
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

BROADCAST_CHANNEL = ''

URL = 'https://www.amazon.com/product/dp/{}'


def get_asin_from_queue():
    with closing(sqs.connect_to_region(BOTO_REGION,
                                       aws_access_key_id=AWS_ACCESS_KEY,
                                       aws_secret_access_key=AWS_SECRET_KEY)) as connection:
        queue = connection.get_queue(BOTO_QUEUE_NAME)
        messages = queue.get_messages(message_attributes=['broadcast_channel'])
        if messages:
            for message in messages:
                if message.message_attributes['broadcast_channel']['string_value'] == BROADCAST_CHANNEL:
                    body = message.get_body()
                    message.delete()
                    return body
        return


def show(asin):
    webbrowser.open_new_tab(URL.format(asin))


def run():
    while True:
        asin = get_asin_from_queue()
        if asin:
            show(asin)


if __name__ == '__main__':
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument('--broadcast-channel', help='The channel which to listen on', dest='broadcast_channel')
    args = psr.parse_args()
    BROADCAST_CHANNEL = args.broadcast_channel
    run()
