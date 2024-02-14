import functools
import time
import traceback
import sys

import paho.mqtt.client as mqtt


def on_connect(topic, client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe(topic)


def safe_on_message(on_message):
    def safe_on_message(client, userdata, msg):
        try:
            return on_message(client, userdata, msg)
        except Exception as e:
            sys.stderr.write(f"Exception processing message: {msg}\n")

            traceback.print_exc()

    return safe_on_message


def connect(args, on_message, retry=True):
    client = mqtt.Client()
    client.on_connect = \
        functools.partial(on_connect, "glow/+/+/+")
    client.on_message = safe_on_message(on_message)

    while True:
        try:
            client.connect(args.mqtt, args.port, 60)
        except Exception as e:
            if not retry:
                raise
            print(e)
            time.sleep(10)
        else:
            break

    client.loop_forever()
