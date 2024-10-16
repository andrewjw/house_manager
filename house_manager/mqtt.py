import functools
import time
import traceback
import sys

import paho.mqtt.client as mqtt
from sentry_sdk import capture_exception

#from .foxess_msg import foxess_msg
from .glow_msg import glow_msg


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("glow/+/+/+")
    #client.subscribe("foxess/+")


def safe_on_message(args, client, userdata, msg):
    try:
        if msg.topic.startswith("glow/"):
            return glow_msg(client, userdata, msg)
        #elif msg.topic.startswith("foxess/"):
        #    return foxess_msg(args.foxess, msg)
        else:
            raise ValueError(f"Unknown topic {msg.topic}")
    except Exception as e:
        capture_exception(e)
        sys.stderr.write(f"Exception processing message: {msg}\n")

        traceback.print_exc()


def connect(args, retry=True):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = functools.partial(safe_on_message, args)

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
