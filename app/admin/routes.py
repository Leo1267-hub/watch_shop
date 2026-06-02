from flask import Blueprint, render_template, redirect, url_for

from app.database import get_db
from app.utils.auth import login_required_admin


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["POST", "GET"])
@login_required_admin
def admin():
    db = get_db()
    watches = db.execute("SELECT * FROM watches_to_check").fetchall()
    return render_template("admin.html", watches=watches, title="Admin")


@admin_bp.route("/accept/<int:watch_id>")
@login_required_admin
def accept(watch_id):
    db = get_db()
    watch = db.execute(
        "SELECT * FROM watches_to_check WHERE watch_id = ?",
        (watch_id,)
    ).fetchone()

    db.execute(
        """INSERT INTO watches
           (user_id, title, price, size, material, weight, description, quantity, watch_picture)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        (
            watch["user_id"],
            watch["title"],
            watch["price"],
            watch["size"],
            watch["material"],
            watch["weight"],
            watch["description"],
            watch["quantity"],
            watch["watch_picture"],
        )
    )
    db.commit()

    return redirect(url_for("admin.reject", watch_id=watch_id))


@admin_bp.route("/reject/<int:watch_id>")
@login_required_admin
def reject(watch_id):
    db = get_db()
    db.execute(
        "DELETE FROM watches_to_check WHERE watch_id = ?",
        (watch_id,)
    )
    db.commit()
    return redirect(url_for("admin.admin"))