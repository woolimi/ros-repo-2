"""SocketIO event handlers for browser ↔ customer_web (channel A)."""

import logging
from app import socketio

logger = logging.getLogger(__name__)


@socketio.on('connect')
def on_connect():
    logger.info('[WS] client connected')


@socketio.on('disconnect')
def on_disconnect():
    logger.info('[WS] client disconnected')


@socketio.on('cmd')
def on_cmd(data):
    logger.info(f'[WS] cmd: {data}')
