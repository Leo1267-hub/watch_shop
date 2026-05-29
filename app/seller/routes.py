from flask import Blueprint, render_template, redirect, url_for, session

from app.database import get_db
from app.forms import SellerForm
from app.utils.auth import login_required_seller
from app.utils.time import send_current_time


seller_bp = Blueprint("seller", __name__)


@seller_bp.route("/seller", methods=["GET", "POST"])
@login_required_seller
def seller():
    print(send_current_time())

    form = SellerForm()
    message = ""
    user_id = session["seller"]
    db = get_db()

    watches = db.execute(
        """SELECT * FROM watches
           WHERE user_id = ?""",
        (user_id,)
    ).fetchall()

    income = db.execute(
        """SELECT income FROM seller
           WHERE user_id = ?""",
        (user_id,)
    ).fetchone()

    selling_history = db.execute(
        """SELECT * FROM selling_history
           WHERE user_id = ?""",
        (user_id,)
    ).fetchall()

    reviews = db.execute(
        """SELECT * FROM reviews
           WHERE seller_id = ?
           ORDER BY date DESC;""",
        (user_id,)
    ).fetchall()

    if form.validate_on_submit():
        title = form.title.data.capitalize()
        price = round(form.price.data, 3)
        size = round(form.size.data, 3)
        material = form.material.data
        weight = round(form.weight.data, 3)
        description = form.description.data
        quantity = form.quantity.data

        file = form.file.data
        watch_picture = file.read()

        db.execute(
            """INSERT INTO watches_to_check
               (user_id, title, price, size, material, weight, description, quantity, watch_picture)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (user_id, title, price, size, material, weight, description, quantity, watch_picture)
        )
        db.commit()

        return redirect(url_for("seller.seller"))

    return render_template(
        "seller.html",
        form=form,
        message=message,
        watches=watches,
        income=round(income["income"], 2),
        selling_history=selling_history,
        reviews=reviews,
        title="Seller"
    )