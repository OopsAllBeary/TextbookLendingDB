
import json

from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer
)

from threading import (
    Thread,
    Lock
)

from PySide6.QtCore import (
    QObject,
    Signal
)


class BookstoreServer(QObject):

    results_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(
        self,
        host="127.0.0.1",
        port=8765
    ):
        super().__init__()

        self.host = host
        self.port = port

        self.server = None
        self.thread = None

        self.pending_lookup = None

        self.lookup_lock = Lock()


    def start(self):

        if self.server is not None:
            return

        try:

            handler = self._create_handler()

            self.server = ThreadingHTTPServer(
                (
                    self.host,
                    self.port
                ),
                handler
            )

            self.thread = Thread(
                target=self.server.serve_forever,
                daemon=True
            )

            self.thread.start()

        except Exception as e:

            self.server = None

            self.error_occurred.emit(
                str(e)
            )


    def stop(self):

        if self.server is None:
            return

        try:

            self.server.shutdown()
            self.server.server_close()

        except Exception:
            pass

        finally:

            self.server = None
            self.thread = None


    def request_lookup(
        self,
        student_id,
        term_id,
        program_id
    ):

        from bookstore.config import (
            BOOKSTORE_PROGRAMS
        )

        program_id = str(
            program_id
        )

        print(
            "BOOKSTORE request_lookup:",
            student_id,
            term_id,
            program_id
        )

        program = BOOKSTORE_PROGRAMS.get(
            program_id
        )

        if not program:

            self.error_occurred.emit(
                f"Unknown bookstore program: "
                f"{program_id}"
            )

            return False


        lookup = {
            "type": "bookstore_lookup",

            "studentId": str(
                student_id
            ),

            "termId": str(
                term_id
            ),

            "programId": program_id,

            "campus": program[
                "campus"
            ]
        }


        with self.lookup_lock:

            self.pending_lookup = lookup


        return True


    def get_pending_lookup(self):

        with self.lookup_lock:

            lookup = self.pending_lookup

            self.pending_lookup = None

            return lookup


    def clear_lookup(self):

        with self.lookup_lock:

            self.pending_lookup = None


    def _create_handler(self):

        parent = self

        class Handler(
            BaseHTTPRequestHandler
        ):

            def log_message(
                self,
                format,
                *args
            ):
                pass


            def _cors_headers(self):

                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )

                self.send_header(
                    "Access-Control-Allow-Methods",
                    "GET, POST, OPTIONS"
                )

                self.send_header(
                    "Access-Control-Allow-Headers",
                    "Content-Type"
                )


            def do_OPTIONS(self):

                self.send_response(204)

                self._cors_headers()

                self.end_headers()


            def do_GET(self):

                if (
                    self.path
                    != "/bookstore-lookup"
                ):

                    self.send_response(404)

                    self.end_headers()

                    return


                data = (
                    parent.get_pending_lookup()
                )


                self.send_response(200)

                self._cors_headers()

                self.send_header(
                    "Content-Type",
                    "application/json"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()


                if data is None:

                    self.wfile.write(
                        b"null"
                    )

                    return


                self.wfile.write(
                    json.dumps(
                        data
                    ).encode("utf-8")
                )


            def do_POST(self):

                if (
                    self.path
                    != "/bookstore-results"
                ):

                    self.send_response(404)

                    self.end_headers()

                    return


                try:

                    length = int(
                        self.headers.get(
                            "Content-Length",
                            0
                        )
                    )

                    raw_data = (
                        self.rfile.read(
                            length
                        )
                    )

                    data = json.loads(
                        raw_data.decode(
                            "utf-8"
                        )
                    )

                except Exception as e:

                    self.send_response(400)

                    self._cors_headers()

                    self.end_headers()

                    parent.error_occurred.emit(
                        f"Invalid bookstore data: {e}"
                    )

                    return


                print(
                    "BOOKSTORE RESULTS RECEIVED BY PYTHON"
                )


                parent.results_received.emit(
                    data
                )


                self.send_response(200)

                self._cors_headers()

                self.send_header(
                    "Content-Type",
                    "text/plain"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()

                self.wfile.write(
                    b"OK"
                )


        return Handler
