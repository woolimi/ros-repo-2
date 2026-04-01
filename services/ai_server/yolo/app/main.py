"""YOLO inference server stub — TCP:5005."""

import socket
import logging

HOST = '0.0.0.0'
PORT = 5005

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_frame(data: bytes) -> bytes:
    """Stub: receive frame bytes, return inference result bytes."""
    return b'[]'


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        logger.info(f'YOLO server listening on {HOST}:{PORT}')
        while True:
            conn, addr = srv.accept()
            logger.info(f'Connection from {addr}')
            with conn:
                data = b''
                while True:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                result = handle_frame(data)
                conn.sendall(result)


if __name__ == '__main__':
    main()
