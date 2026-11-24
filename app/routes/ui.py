from flask import Blueprint, current_app

bp = Blueprint("ui", __name__)


@bp.get("/")
def index():
    """Serves the demo page. All data still goes through the JSON API."""
    return current_app.send_static_file("index.html")
