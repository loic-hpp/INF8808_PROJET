# -*- coding: utf-8 -*-
"""
Entry point for production/Gunicorn deployment.
Local dev: just run `python app.py` directly.
"""
import os
from flask_failsafe import failsafe


@failsafe
def create_app():
    # intentional inside-function import for flask_failsafe
    from app import app  # pylint: disable=import-outside-toplevel
    return app.server


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    create_app().run(host="0.0.0.0", port=port, debug=False)
