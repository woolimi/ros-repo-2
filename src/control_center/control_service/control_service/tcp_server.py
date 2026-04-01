"""TCP server stub — localhost:8080, JSON newline-delimited protocol."""

import json
import logging
import socket
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)

TCP_HOST = 'localhost'
TCP_PORT = 8080


class TCPServer:
    """Listens for JSON messages from customer_web on TCP port 8080."""

    def __init__(self, on_message: Optional[Callable[[dict, socket.socket], None]] = None):
        self._on_message = on_message
        self._server_sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        self._running = True
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((TCP_HOST, TCP_PORT))
        self._server_sock.listen(5)
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        logger.info(f'[TCPServer] listening on {TCP_HOST}:{TCP_PORT}')

    def stop(self) -> None:
        self._running = False
        if self._server_sock:
            self._server_sock.close()

    def _accept_loop(self) -> None:
        while self._running:
            try:
                conn, addr = self._server_sock.accept()
                logger.info(f'[TCPServer] connection from {addr}')
                t = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
                t.start()
            except OSError:
                break

    def _handle_client(self, conn: socket.socket) -> None:
        buf = b''
        with conn:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    try:
                        msg = json.loads(line.decode('utf-8'))
                        self._dispatch(msg, conn)
                    except json.JSONDecodeError:
                        logger.warning(f'[TCPServer] invalid JSON: {line}')

    def _dispatch(self, msg: dict, conn: socket.socket) -> None:
        msg_type = msg.get('type')
        handler = getattr(self, f'handle_{msg_type}', None)
        if handler:
            handler(msg, conn)
        elif self._on_message:
            self._on_message(msg, conn)
        else:
            logger.warning(f'[TCPServer] unhandled message type: {msg_type}')

    def handle_login(self, msg: dict, conn: socket.socket) -> None:
        pass

    def handle_session_check(self, msg: dict, conn: socket.socket) -> None:
        pass

    def handle_cmd(self, msg: dict, conn: socket.socket) -> None:
        pass

    @staticmethod
    def send_response(conn: socket.socket, data: dict) -> None:
        try:
            conn.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except OSError as e:
            logger.error(f'[TCPServer] send error: {e}')
