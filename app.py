import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import psycopg


def connect():
    return psycopg.connect(host="db", dbname="study", user="study",
                           password=os.environ["DB_PASSWORD"])


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/visits"):
            self.send_error(404)
            return
        with connect() as conn:
            if self.path == "/":
                visit = conn.execute(
                    "INSERT INTO visits DEFAULT VALUES RETURNING id"
                ).fetchone()[0]
                body = Path("site/index.html").read_bytes()
                body += f"<p>Visit #{visit}</p>".encode()
                kind = "text/html"
            else:
                rows = conn.execute("SELECT id FROM visits ORDER BY id")
                body = "".join(f"{row[0]}\n" for row in rows).encode()
                kind = "text/plain"
        self.send_response(200)
        self.send_header("Content-Type", kind + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


with connect() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS visits (id serial PRIMARY KEY)")
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
