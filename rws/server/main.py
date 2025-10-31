"""Basic custom http handler."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from rws.server.graph import Graph


class Server(BaseHTTPRequestHandler):
    """Rest API format."""
    def do_GET(self):
        url = urlparse(self.path)
        print(url.query)
        query = parse_qs(url.query)
        print(query)
        if url.path == "/graph":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # TODO: validate the input of the query

            self.wfile.write(Graph(query).as_html())
        elif url.path == "/index.js":
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()

            res = open("index.js", "rb")
            self.wfile.write(res.read())
        elif url.path == "/index.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()

            res = open("index.css", "rb")
            self.wfile.write(res.read())
        elif url.path == "/favicon.ico":
            self.send_response(404)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            res = open('index.html', 'rb')

            self.wfile.write(res.read())


def start_server():
    """Type localhost:8080 in order to look at the site
    MIGHT have some difficulties with some network securities but probs not
    """
    host = 'localhost'
    port = 8080

    webServer = HTTPServer((host, port), Server)

    webServer.serve_forever()
    Server.server_close()


if __name__ == '__main__':
    start_server()
