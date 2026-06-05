import io

from flask import Blueprint, abort, flash, get_flashed_messages, redirect, render_template, send_file, session, url_for

from app.database import get_db
from app.forms import CompareForm, FilterForm


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

        if "buyer" in session:
            query += " AND user_id NOT IN (SELECT seller_id FROM blocked_sellers WHERE buyer_id = ?)"
            user_inputs.append(session["buyer"])

        if form.watch.data and form.watch.data != "all":
            query += " AND title LIKE ?"
            user_inputs.append(form.watch.data)

        if form.min_price.data is not None:
            query += " AND price >= ?"
            user_inputs.append(form.min_price.data)

        if form.max_price.data is not None:
            query += " AND price <= ?"
            user_inputs.append(form.max_price.data)

        if (
            form.min_price.data is not None
            and form.max_price.data is not None
            and form.min_price.data > form.max_price.data
        ):
            flash("Minimum price cannot be greater than maximum price")
            return redirect(url_for("watches.main"))

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


@watches_bp.route("/watch/<int:watch_id>")
def watch(watch_id):
    db = get_db()
    watch = db.execute(
        "SELECT * FROM watches WHERE watch_id = ?;",
        (watch_id,)
    ).fetchone()

    if watch is None:
        flash("Watch not found")
        return redirect(url_for("watches.main"))

    title = watch["title"]
    return render_template("watch.html", watch=watch, title=title)


@watches_bp.route("/compare", methods=["POST", "GET"])
def compare():
    form = CompareForm()
    db = get_db()
    watch1_inf = ""
    watch2_inf = ""

    watch1 = session.get("watch1")
    watch2 = session.get("watch2")

    if watch1:
        watch1_inf = db.execute(
            "SELECT * FROM watches WHERE watch_id = ?",
            (watch1,)
        ).fetchone()
        if watch1_inf is None:
            session.pop("watch1", None)
            watch1 = None
            flash("One compared watch no longer exists")

    if watch2:
        watch2_inf = db.execute(
            "SELECT * FROM watches WHERE watch_id = ?",
            (watch2,)
        ).fetchone()
        if watch2_inf is None:
            session.pop("watch2", None)
            watch2 = None
            flash("One compared watch no longer exists")

    if form.validate_on_submit():
        session.pop("watch1", None)
        session.pop("watch2", None)
        session.modified = True
        return redirect(url_for("watches.compare"))

    session.modified = True
    return render_template(
        "compare.html",
        watch1=watch1,
        watch2=watch2,
        form=form,
        watch2_inf=watch2_inf,
        watch1_inf=watch1_inf,
        title="Compare"
    )


@watches_bp.route("/compare_watch/<int:watch_id>")
def compare_watch(watch_id):
    db = get_db()
    watch = db.execute(
        "SELECT watch_id FROM watches WHERE watch_id = ?",
        (watch_id,)
    ).fetchone()

    if watch is None:
        flash("Watch not found")
        return redirect(url_for("watches.main"))

    watch1 = session.get("watch1")
    watch2 = session.get("watch2")

    if (watch1 == watch_id) or (watch2 == watch_id):
        flash("You cannot compare the same watch")
        return redirect(url_for("watches.main"))

    if watch1 and watch2:
        flash("You can compare only 2 watches at a time")
        return redirect(url_for("watches.main"))

    if not watch1:
        session["watch1"] = watch_id
    elif not watch2:
        session["watch2"] = watch_id

    session.modified = True
    return redirect(url_for("watches.compare"))
