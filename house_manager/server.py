from datetime import datetime
import http.server
import json
import traceback

from sentry_sdk import capture_exception  # type:ignore

from .metrics import get_metrics, start_metrics

BOOTSTRAP_VERSION = json.load(open("package.json"))["dependencies"]["bootstrap"][1:]
REACT_VERSION = json.load(open("package.json"))["dependencies"]["react"][1:]

def handle_error(func):
    def r(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            traceback.print_exception(e)
            capture_exception(e)

            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write(f"Exception Occurred.\n".encode("utf8"))
    return r

class Handler(http.server.BaseHTTPRequestHandler):
    @handle_error
    def do_GET(self):
        if self.path == "/":
            self.send_index()
        elif self.path == "/metrics":
            self.send_metrics()
        else:
            self.send_error(404)

    def send_index(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(open("static/index.html").read().format(
            bootstrap_version=BOOTSTRAP_VERSION,
            react_version=REACT_VERSION
        ).encode("utf8"))

    def send_metrics(self):
        metrics = get_metrics()
        if metrics is None:
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(metrics.encode("utf8"))


def serve(args):  # pragma: no cover
    start_metrics(args)

    server = http.server.HTTPServer(args.bind, Handler)
    server.serve_forever()
