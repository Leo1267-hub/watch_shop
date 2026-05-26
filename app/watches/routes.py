import io

from flask import Blueprint, abort, render_template, send_file, session, get_flashed_messages

from app.database import get_db
from app.forms import FilterForm


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
    
@watches_bp.route("/", methods=["GET", "POST"])
@watches_bp.route("/main", methods=["GET", "POST"])
def main():
    form = FilterForm()
    db = get_db()
    message = get_flashed_messages()

    if "buyer" in session:
        watches = db.execute(
            """SELECT * FROM watches
               WHERE user_id NOT IN (
                   SELECT seller_id
                   FROM blocked_sellers
                   WHERE buyer_id = ?
               );""",
            (session["buyer"],)
        ).fetchall()
    else:
        watches = db.execute("SELECT * FROM watches").fetchall()

    all_watches = [watch["title"] for watch in watches]
    all_possible_watches = []

    for title in all_watches:
        if title not in all_possible_watches:
            all_possible_watches.append(title)

    form.watch.choices = all_possible_watches + ["all"]

    if form.validate_on_submit():
        query = "SELECT * FROM watches WHERE 1=1"
        user_inputs = []

        if form.watch.data and form.watch.data != "all":
            query += " AND title LIKE ?"
            user_inputs.append(form.watch.data)

        if form.min_price.data:
            query += " AND price >= ?"
            user_inputs.append(form.min_price.data)

        if form.max_price.data:
            query += " AND price <= ?"
            user_inputs.append(form.max_price.data)

        if form.sort.data and form.sort.data != "all":
            if form.sort.data == "Price low to high":
                query += " ORDER BY price ASC"
            else:
                query += " ORDER BY price DESC"

        watches = db.execute(query, tuple(user_inputs)).fetchall()

        all_watches = [watch["title"] for watch in watches]
        all_possible_watches = []

        for title in all_watches:
            if title not in all_possible_watches:
                all_possible_watches.append(title)

        form.watch.choices = all_possible_watches + ["all"]

    return render_template(
        "index.html",
        title="Main page",
        watches=watches,
        message=message,
        form=form
    )