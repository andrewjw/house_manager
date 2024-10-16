import argparse

from .exceptions import InvalidArguments

parser = argparse.ArgumentParser()
parser.add_argument('--mqtt', type=str, nargs='?', default="mqtt",
                    help='the mqtt server to connect to.')
parser.add_argument('--port', type=int, nargs='?', default=1883,
                    help='the mqtt port to connect to.')
parser.add_argument('--bind', type=str, nargs='?', default="0.0.0.0:6060",
                    help='the ip address and port to bind to')
parser.add_argument('--foxess', type=str, nargs='?', default="foxess",
                    help='the foxessprom server to connect to.')
parser.add_argument('--prometheus', type=str, nargs='?', default="prometheus",
                    help='the prometheus server to connect to.')


def get_arguments(args) -> argparse.Namespace:
    args = parser.parse_args(args)

    if ":" not in args.bind:
        args.bind = (args.bind, 6060)
    else:
        args.bind = (args.bind.split(":")[0], int(args.bind.split(":")[1]))

    return args
