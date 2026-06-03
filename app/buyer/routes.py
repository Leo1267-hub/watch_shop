from flask import Blueprint, flash, get_flashed_messages, redirect, render_template, session, url_for

from app.database import get_db
from app.forms import BasketForm, EditBudget, EditPassword
from app.utils.auth import login_required_buyer
from app.utils.time import send_current_time


buyer_bp = Blueprint("buyer", __name__)


@buyer_bp.route("/profile", methods=["GET", "POST"])
@login_required_buyer
def profile():
    message = ""
    form_budget = EditBudget()
    form_password = EditPassword()
    user_id = session["buyer"]
    db = get_db()

    user = db.execute(
        """SELECT * FROM buyer
           WHERE user_id = ?""",
        (user_id,)
    ).fetchone()
    budget = round(user["budget"], 2)

    if form_budget.validate_on_submit():
        budget = form_budget.new_budget.data
        db.execute(
            """UPDATE buyer SET budget = ?
               WHERE user_id = ?""",
            (budget, user_id)
        )
        db.commit()

    return render_template(
        "profile.html",
        title="Profile",
        budget=budget,
        form_budget=form_budget,
        form_password=form_password,
        message=message,
    )


@buyer_bp.route("/basket", methods=["GET", "POST"])
@login_required_buyer
def basket():
    form = BasketForm()
    message = get_flashed_messages()
    message_to_pay = ""

    if "basket" not in session:
        session["basket"] = {}

    names = {}
    db = get_db()

    for watch_id in session["basket"]:
        watch = db.execute(
            """SELECT * FROM watches
               WHERE watch_id = ?;""",
            (watch_id,)
        ).fetchone()
        names[watch_id] = watch["title"]

    total_cost = sum(item["price"] for item in session["basket"].values())
    total_cost = round(total_cost, 2)

    if form.validate_on_submit():
        budget_sql = db.execute(
            """SELECT budget FROM buyer
               WHERE user_id = ?""",
            (session["buyer"],)
        ).fetchone()
        budget = budget_sql["budget"]

        if total_cost > budget:
            money_needed = total_cost - budget
            message_to_pay = f"you need {money_needed}€ more to complete purchase"
        else:
            budget -= total_cost
            db.execute(
                """UPDATE buyer SET budget = ?
                   WHERE user_id = ?""",
                (budget, session["buyer"])
            )

            watch_ids_to_remove = [watch_id for watch_id in session["basket"]]
            for watch_id in watch_ids_to_remove:
                watch = db.execute(
                    """SELECT * FROM watches
                       WHERE watch_id = ?;""",
                    (watch_id,)
                ).fetchone()

                quantity = watch["quantity"]
                seller_id = watch["user_id"]
                title = watch["title"]
                size = watch["size"]
                material = watch["material"]
                weight = watch["weight"]
                description = watch["description"]
                watch_picture = watch["watch_picture"]
                date = send_current_time()
                quantity_in_basket = session["basket"][watch_id]["quantity"]
                new_quantity = quantity - quantity_in_basket
                price_for_watch_id = session["basket"][watch_id]["price"]

                db.execute(
                    """INSERT INTO selling_history
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        seller_id,
                        session["buyer"],
                        watch_id,
                        title,
                        price_for_watch_id,
                        size,
                        material,
                        weight,
                        description,
                        quantity_in_basket,
                        watch_picture,
                        date,
                    )
                )

                if new_quantity == 0:
                    db.execute("DELETE FROM watches WHERE watch_id = ?", (watch_id,))
                else:
                    db.execute(
                        "UPDATE watches SET quantity = ? WHERE watch_id = ?",
                        (new_quantity, watch_id)
                    )

                db.execute(
                    "UPDATE seller SET income = income + ? WHERE user_id = ?",
                    (price_for_watch_id, seller_id)
                )
                session["basket"].pop(watch_id)

            db.commit()
            return redirect(url_for("auth.logout"))

    session.modified = True
    return render_template(
        "basket.html",
        basket=session["basket"],
        title="Basket",
        message=message,
        total_cost=total_cost,
        names=names,
        form=form,
        message_to_pay=message_to_pay,
    )


@buyer_bp.route("/add_to_basket/<int:watch_id>")
@login_required_buyer
def add_to_basket(watch_id):
    db = get_db()
    watch = db.execute(
        """SELECT quantity, price FROM watches
           WHERE watch_id = ?;""",
        (watch_id,)
    ).fetchone()

    if "basket" not in session:
        session["basket"] = {}

    if watch_id not in session["basket"]:
        session["basket"][watch_id] = {"quantity": 1, "price": watch["price"]}
    else:
        if session["basket"][watch_id]["quantity"] >= watch["quantity"]:
            flash(f"Only {watch['quantity']} left in stock")
            return redirect(url_for("watches.main"))

        session["basket"][watch_id]["quantity"] += 1
        session["basket"][watch_id]["price"] += watch["price"]

    session.modified = True
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/add_one_to_basket/<int:watch_id>")
@login_required_buyer
def add_one_to_basket(watch_id):
    db = get_db()
    watch = db.execute(
        """SELECT quantity, price FROM watches
           WHERE watch_id = ?;""",
        (watch_id,)
    ).fetchone()

    if session["basket"][watch_id]["quantity"] >= watch["quantity"]:
        flash(f"Only {watch['quantity']} left in stock")
    else:
        session["basket"][watch_id]["quantity"] += 1
        session["basket"][watch_id]["price"] += watch["price"]

    session.modified = True
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/remove_from_basket/<int:watch_id>")
@login_required_buyer
def remove_from_basket(watch_id):
    db = get_db()
    watch = db.execute(
        """SELECT quantity, price FROM watches
           WHERE watch_id = ?;""",
        (watch_id,)
    ).fetchone()

    if session["basket"][watch_id]["quantity"] > 1:
        session["basket"][watch_id]["quantity"] -= 1
        session["basket"][watch_id]["price"] -= watch["price"]
    else:
        session["basket"].pop(watch_id)

    session.modified = True
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/remove_all/<int:watch_id>")
@login_required_buyer
def remove_all(watch_id):
    session["basket"].pop(watch_id)
    session.modified = True
    return redirect(url_for("buyer.basket"))
