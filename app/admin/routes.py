from flask import Blueprint, flash, render_template, redirect, url_for

from app.database import get_db
from app.forms import MessageForm
from app.utils.auth import login_required_admin
from app.utils.time import send_current_time


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

    if watch is None:
        flash("Pending watch not found")
        return redirect(url_for("admin.admin"))

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
    db.execute(
        "DELETE FROM watches_to_check WHERE watch_id = ?",
        (watch_id,)
    )
    db.commit()
    flash("Watch approved")

    return redirect(url_for("admin.admin"))


@admin_bp.route("/reject/<int:watch_id>")
@login_required_admin
def reject(watch_id):
    db = get_db()
    watch = db.execute(
        "SELECT * FROM watches_to_check WHERE watch_id = ?",
        (watch_id,)
    ).fetchone()

    if watch is None:
        flash("Pending watch not found")
        return redirect(url_for("admin.admin"))

    db.execute(
        "DELETE FROM watches_to_check WHERE watch_id = ?",
        (watch_id,)
    )
    db.commit()
    flash("Watch rejected")
    return redirect(url_for("admin.admin"))


@admin_bp.route("/help_admin")
@login_required_admin
def help_admin():
    db = get_db()
    respond_needed = db.execute("SELECT * FROM messages_to_response_buyer").fetchall()
    return render_template("admin_help.html", respond_needed=respond_needed, title="Response")


@admin_bp.route("/response/<int:message_id>", methods=["POST", "GET"])
@login_required_admin
def response(message_id):
    form = MessageForm()
    db = get_db()
    previous_message = db.execute(
        """SELECT * FROM messages_to_response_buyer
           WHERE message_id = ?""",
        (message_id,)
    ).fetchone()

    if previous_message is None:
        flash("Message not found")
        return redirect(url_for("admin.help_admin"))

    last_message = previous_message["message"]
    last_date = previous_message["date"]
    buyer_id = previous_message["buyer_id"]

    if form.validate_on_submit():
        message = form.message.data.strip()
        if not message:
            flash("Response cannot be empty")
            return redirect(url_for("admin.response", message_id=message_id))

        date = send_current_time()
        db.execute(
            """INSERT INTO responded_messages_buyer
               VALUES (?, ?, ?, ?, ?, ?)""",
            (message_id, buyer_id, last_message, last_date, message, date)
        )
        db.execute(
            """DELETE FROM messages_to_response_buyer
               WHERE message_id = ?""",
            (message_id,)
        )
        db.commit()
        flash("Response sent")
        return redirect(url_for("admin.help_admin"))

    return render_template(
        "response.html",
        title="response",
        buyer_id=buyer_id,
        last_message=last_message,
        form=form,
    )
