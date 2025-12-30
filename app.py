from flask import Flask, jsonify
import os


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home():
        return jsonify(status="ok")

    @app.get("/health")
    def health():
        return jsonify(status="healthy")

    return app


if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    create_app().run(host="0.0.0.0", port=port)

