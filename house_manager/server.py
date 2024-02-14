from datetime import datetime
import http.server

from .metrics import get_metrics


class Handler(http.server.BaseHTTPRequestHandler):
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
        self.wfile.write("""
<html>
<head><title>House Manager</title></head>
<body>
<h1>House Manager</h1>
<p><a href="/metrics">Metrics</a></p>
</body>
</html>""".encode("utf8"))

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
    server = http.server.HTTPServer(args.bind, Handler)
    server.serve_forever()
