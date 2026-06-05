from flask import Blueprint, flash, render_template, redirect, url_for, session

from app.database import get_db
from app.forms import EditWatch, SellerForm
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


@seller_bp.route("/delete_review/<int:review_id>")
@login_required_seller
def delete_review(review_id):
    db = get_db()
    db.execute(
        """DELETE FROM reviews
           WHERE review_id = ?""",
        (review_id,)
    )
    db.commit()
    return redirect(url_for("seller.seller"))


@seller_bp.route("/edit_watch/<int:watch_id>", methods=["GET", "POST"])
@login_required_seller
def edit_watch(watch_id):
    form = EditWatch()
    db = get_db()
    watch = db.execute(
        """SELECT * FROM watches
           WHERE watch_id = ?""",
        (watch_id,)
    ).fetchone()
    
    if watch is None:
        flash("Watch not found")
        return redirect(url_for("watches.main"))
    
    if watch["user_id"] != session["seller"]:
        flash("You are not allowed to edit this watch")
        return redirect(url_for("seller.seller"))

    title = watch["title"]
    price = watch["price"]
    size = watch["size"]
    material = watch["material"]
    weight = watch["weight"]
    description = watch["description"]
    quantity = watch["quantity"]
    watch_picture = watch["watch_picture"]

    if form.validate_on_submit():
        if form.title.data:
            title = form.title.data.capitalize()
        if form.price.data is not None:
            price = form.price.data
        if form.size.data is not None:
            size = form.size.data
        if form.material.data:
            material = form.material.data
        if form.weight.data is not None:
            weight = form.weight.data
        if form.description.data:
            description = form.description.data
        if form.quantity.data is not None:
            quantity = form.quantity.data
        if form.file.data:
            file = form.file.data
            watch_picture = file.read()

        db.execute(
            """UPDATE watches
               SET title = ?, price = ?, size = ?, material = ?, weight = ?, description = ?, quantity = ?, watch_picture = ?
               WHERE watch_id = ?""",
            (title, price, size, material, weight, description, quantity, watch_picture, watch_id)
        )
        db.commit()
        return redirect(url_for("seller.seller"))

    return render_template(
        "edit_watch.html",
        form=form,
        title="edit watches",
        name=watch["title"],
        price=watch["price"],
        size=watch["size"],
        material=watch["material"],
        weight=watch["weight"],
        description=watch["description"],
        quantity=watch["quantity"]
    )


@seller_bp.route("/delete/<int:watch_id>")
@login_required_seller
def delete(watch_id):
    db = get_db()
    db.execute(
        """DELETE FROM watches
           WHERE watch_id = ?""",
        (watch_id,)
    )
    db.commit()
    return redirect(url_for("seller.seller"))
