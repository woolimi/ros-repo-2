"""Flask + SocketIO app factory."""

from flask import Flask
from flask_socketio import SocketIO

from config import SECRET_KEY
from routes.auth import auth_bp
from routes.main import main_bp
from routes.cart import cart_bp
import ws_handler  # noqa: F401 — registers SocketIO events

socketio = SocketIO()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)

    socketio.init_app(app, cors_allowed_origins='*')
    return app


if __name__ == '__main__':
    from config import DEBUG, PORT
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=PORT, debug=DEBUG)
