"""Small browser frontend for OmniBot.

Run with:
    python3 web_app.py
"""

import cgi
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from main import EXTENSION_MAP, process_file
from retrieval.tfidf_retriever import TFIDFRetriever


ROOT = Path(__file__).parent
FRONTEND = ROOT / "frontend"
UPLOADS = Path(tempfile.gettempdir()) / "omnibot-uploads"
UPLOADS.mkdir(exist_ok=True)

retriever = TFIDFRetriever(similarity_threshold=0.05, top_k=3)
processed_files = []
index_ready = False


def json_response(handler, payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


class OmniBotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/avatar":
            body = (ROOT / "cloudee.avatar.json").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/status":
            json_response(
                self,
                {
                    "files": processed_files,
                    "ready": index_ready,
                    "chunks": retriever.chunk_count,
                },
            )
            return

        file_path = FRONTEND / ("index.html" if path == "/" else path.lstrip("/"))
        if not file_path.is_file() or FRONTEND not in file_path.parents:
            self.send_error(404)
            return
        content_type = "text/html; charset=utf-8" if file_path.suffix == ".html" else "text/css; charset=utf-8" if file_path.suffix == ".css" else "application/javascript; charset=utf-8"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global index_ready
        path = urlparse(self.path).path

        if path == "/api/upload":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            uploaded = form["files"] if "files" in form else []
            if not isinstance(uploaded, list):
                uploaded = [uploaded]

            added = []
            errors = []
            for item in uploaded:
                if not item.filename:
                    continue
                suffix = Path(item.filename).suffix.lower()
                if suffix not in EXTENSION_MAP:
                    errors.append(f"Unsupported file type: {item.filename}")
                    continue
                destination = UPLOADS / Path(item.filename).name
                destination.write_bytes(item.file.read())
                if process_file(str(destination), retriever):
                    if item.filename not in processed_files:
                        processed_files.append(item.filename)
                    added.append(item.filename)
                else:
                    errors.append(f"Could not extract text from {item.filename}")

            if retriever.chunk_count:
                index_ready = retriever.build_index()
            json_response(self, {"added": added, "errors": errors, "ready": index_ready})
            return

        if path == "/api/ask":
            length = int(self.headers.get("Content-Length", "0"))
            try:
                question = json.loads(self.rfile.read(length)).get("question", "").strip()
            except (json.JSONDecodeError, UnicodeDecodeError):
                json_response(self, {"error": "Invalid request."}, 400)
                return
            if not question:
                json_response(self, {"error": "Ask a question first."}, 400)
                return
            if not index_ready:
                json_response(self, {"error": "Upload at least one readable file first."}, 400)
                return
            answer, source = retriever.answer(question)
            json_response(self, {"answer": answer, "source": source})
            return

        self.send_error(404)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    print("OmniBot is running at http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), OmniBotHandler).serve_forever()
