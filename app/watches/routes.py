import io

from flask import Blueprint, abort, send_file

from app.database import get_db


watches_bp = Blueprint("watches", __name__)


@watches_bp.route("/serve_image/<int:id>")
def serve_image(id):
    db = get_db()
    image = db.execute(
        "SELECT watch_picture FROM watches WHERE watch_id = ?",
        (id,)
    ).fetchone()

    if image and image["watch_picture"]:
        return send_file(io.BytesIO(image["watch_picture"]), mimetype="image/jpeg")

    abort(404)


@watches_bp.route("/serve_image_to_check/<int:id>")
def serve_image_to_check(id):
    db = get_db()
    image = db.execute(
        "SELECT watch_picture FROM watches_to_check WHERE watch_id = ?",
        (id,)
    ).fetchone()

    if image and image["watch_picture"]:
        return send_file(io.BytesIO(image["watch_picture"]), mimetype="image/jpeg")

    abort(404)


@watches_bp.route("/serve_image_from_selling/<int:id>")
def serve_image_from_selling(id):
    db = get_db()
    image = db.execute(
        "SELECT watch_picture FROM selling_history WHERE watch_id = ?",
        (id,)
    ).fetchone()

    if image and image["watch_picture"]:
        return send_file(io.BytesIO(image["watch_picture"]), mimetype="image/jpeg")

    abort(404)