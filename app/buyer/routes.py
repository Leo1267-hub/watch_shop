from flask import Blueprint, flash, get_flashed_messages, redirect, render_template, session, url_for

from app.database import get_db
from app.forms import BasketForm, EditBudget, EditPassword, MessageForm, QuestionForm
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import login_required_buyer
from app.utils.time import send_current_time


buyer_bp = Blueprint("buyer", __name__)


def _get_watch(db, watch_id):
    return db.execute(
        "SELECT * FROM watches WHERE watch_id = ?",
        (watch_id,)
    ).fetchone()


def _ensure_basket():
    if "basket" not in session:
        session["basket"] = {}


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

    if user is None:
        session.clear()
        flash("Buyer account was not found. Please log in again.")
        return redirect(url_for("auth.login"))

    budget = round(user["budget"], 2)

    if form_budget.validate_on_submit():
        budget = form_budget.new_budget.data
        db.execute(
            """UPDATE buyer SET budget = ?
               WHERE user_id = ?""",
            (budget, user_id)
        )
        db.commit()
        flash("Budget updated")
        return redirect(url_for("buyer.profile"))

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

    _ensure_basket()
    names = {}
    db = get_db()

    invalid_watch_ids = []
    for watch_id in list(session["basket"].keys()):
        watch = _get_watch(db, watch_id)
        if watch is None:
            invalid_watch_ids.append(watch_id)
            continue

        basket_quantity = session["basket"][watch_id]["quantity"]
        if basket_quantity > watch["quantity"]:
            session["basket"][watch_id]["quantity"] = watch["quantity"]
            session["basket"][watch_id]["price"] = watch["price"] * watch["quantity"]
            flash(f"Basket quantity for {watch['title']} was reduced to available stock")

        names[watch_id] = watch["title"]

    for watch_id in invalid_watch_ids:
        session["basket"].pop(watch_id, None)
        flash("A watch was removed from your basket because it no longer exists")

    total_cost = sum(item["price"] for item in session["basket"].values())
    total_cost = round(total_cost, 2)

    if form.validate_on_submit():
        if not session["basket"]:
            flash("Your basket is empty")
            return redirect(url_for("buyer.basket"))

        budget_sql = db.execute(
            """SELECT budget FROM buyer
               WHERE user_id = ?""",
            (session["buyer"],)
        ).fetchone()

        if budget_sql is None:
            session.clear()
            flash("Buyer account was not found. Please log in again.")
            return redirect(url_for("auth.login"))

        budget = budget_sql["budget"]

        if total_cost > budget:
            money_needed = round(total_cost - budget, 2)
            message_to_pay = f"you need {money_needed}€ more to complete purchase"
        else:
            watch_ids_to_remove = [watch_id for watch_id in session["basket"]]

            for watch_id in watch_ids_to_remove:
                watch = _get_watch(db, watch_id)
                if watch is None:
                    session["basket"].pop(watch_id, None)
                    flash("A watch was removed from your basket because it no longer exists")
                    continue

                quantity = watch["quantity"]
                quantity_in_basket = session["basket"][watch_id]["quantity"]

                if quantity_in_basket > quantity:
                    flash(f"Only {quantity} left in stock for {watch['title']}")
                    return redirect(url_for("buyer.basket"))

                seller_id = watch["user_id"]
                title = watch["title"]
                size = watch["size"]
                material = watch["material"]
                weight = watch["weight"]
                description = watch["description"]
                watch_picture = watch["watch_picture"]
                date = send_current_time()
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
                    db.execute("DELETE FROM favourite WHERE watch_id = ?", (watch_id,))
                else:
                    db.execute(
                        "UPDATE watches SET quantity = ? WHERE watch_id = ?",
                        (new_quantity, watch_id)
                    )

                db.execute(
                    "UPDATE seller SET income = income + ? WHERE user_id = ?",
                    (price_for_watch_id, seller_id)
                )
                session["basket"].pop(watch_id, None)
                budget -= price_for_watch_id

            db.execute(
                """UPDATE buyer SET budget = ?
                   WHERE user_id = ?""",
                (budget, session["buyer"])
            )
            db.commit()
            flash("Purchase completed successfully")
            return redirect(url_for("buyer.basket"))

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
    watch = _get_watch(db, watch_id)

    if watch is None:
        flash("Watch not found")
        return redirect(url_for("watches.main"))

    if watch["quantity"] <= 0:
        flash("This watch is out of stock")
        return redirect(url_for("watches.main"))

    if watch["user_id"] == session["buyer"]:
        flash("You cannot buy your own watch")
        return redirect(url_for("watches.main"))

    _ensure_basket()

    if watch_id not in session["basket"]:
        session["basket"][watch_id] = {"quantity": 1, "price": watch["price"]}
    else:
        if session["basket"][watch_id]["quantity"] >= watch["quantity"]:
            flash(f"Only {watch['quantity']} left in stock")
            return redirect(url_for("watches.main"))

        session["basket"][watch_id]["quantity"] += 1
        session["basket"][watch_id]["price"] += watch["price"]

    session.modified = True
    flash("Watch added to basket")
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/add_one_to_basket/<int:watch_id>")
@login_required_buyer
def add_one_to_basket(watch_id):
    db = get_db()
    _ensure_basket()

    if watch_id not in session["basket"]:
        flash("Watch is not in your basket")
        return redirect(url_for("buyer.basket"))

    watch = _get_watch(db, watch_id)
    if watch is None:
        session["basket"].pop(watch_id, None)
        session.modified = True
        flash("Watch no longer exists")
        return redirect(url_for("buyer.basket"))

    if session["basket"][watch_id]["quantity"] >= watch["quantity"]:
        flash(f"Only {watch['quantity']} left in stock")
    else:
        session["basket"][watch_id]["quantity"] += 1
        session["basket"][watch_id]["price"] += watch["price"]
        flash("Basket updated")

    session.modified = True
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/remove_from_basket/<int:watch_id>")
@login_required_buyer
def remove_from_basket(watch_id):
    db = get_db()
    _ensure_basket()

    if watch_id not in session["basket"]:
        flash("Watch is not in your basket")
        return redirect(url_for("buyer.basket"))

    watch = _get_watch(db, watch_id)
    if watch is None:
        session["basket"].pop(watch_id, None)
        session.modified = True
        flash("Watch no longer exists")
        return redirect(url_for("buyer.basket"))

    if session["basket"][watch_id]["quantity"] > 1:
        session["basket"][watch_id]["quantity"] -= 1
        session["basket"][watch_id]["price"] -= watch["price"]
    else:
        session["basket"].pop(watch_id, None)

    session.modified = True
    flash("Basket updated")
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/remove_all/<int:watch_id>")
@login_required_buyer
def remove_all(watch_id):
    _ensure_basket()

    if watch_id not in session["basket"]:
        flash("Watch is not in your basket")
        return redirect(url_for("buyer.basket"))

    session["basket"].pop(watch_id, None)
    session.modified = True
    flash("Watch removed from basket")
    return redirect(url_for("buyer.basket"))


@buyer_bp.route("/add_to_favourite/<int:watch_id>")
@login_required_buyer
def add_to_favourite(watch_id):
    user_id = session["buyer"]
    db = get_db()
    watch = _get_watch(db, watch_id)

    if watch is None:
        flash("Watch not found")
        return redirect(url_for("watches.main"))

    check = db.execute(
        """SELECT * FROM favourite
           WHERE watch_id = ? AND user_id = ?""",
        (watch_id, user_id)
    ).fetchone()

    if check:
        flash("You already have this watch in favourite")
        return redirect(url_for("watches.main"))

    db.execute(
        """INSERT INTO favourite(user_id, watch_id)
           VALUES (?, ?);""",
        (user_id, watch_id)
    )
    db.commit()
    flash("Watch added to favourites")
    return redirect(url_for("buyer.favourite"))


@buyer_bp.route("/favourite", methods=["GET", "POST"])
@login_required_buyer
def favourite():
    user_id = session["buyer"]
    db = get_db()
    favourite_to_check_if_exists = db.execute(
        "SELECT * FROM favourite WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    favourite_that_exists = []
    names = {}

    for watch_dic in favourite_to_check_if_exists:
        watch_id = watch_dic["watch_id"]
        watch = _get_watch(db, watch_id)

        if watch:
            favourite_that_exists.append(watch_id)
            names[watch_id] = {
                "title": watch["title"],
                "seller": watch["user_id"],
                "watch_id": watch_id,
            }
        else:
            db.execute(
                "DELETE FROM favourite WHERE user_id = ? AND watch_id = ?",
                (user_id, watch_id)
            )
            db.commit()
            flash("A favourite was removed because the watch no longer exists")

    return render_template(
        "favourite.html",
        title="favourite",
        names=names,
        favourite_that_exists=favourite_that_exists,
    )


@buyer_bp.route("/remove_from_favourite/<int:watch_id>")
@login_required_buyer
def remove_from_favourite(watch_id):
    db = get_db()
    user_id = session["buyer"]
    favourite = db.execute(
        """SELECT * FROM favourite
           WHERE watch_id = ? AND user_id = ?""",
        (watch_id, user_id)
    ).fetchone()

    if favourite is None:
        flash("Watch is not in your favourites")
        return redirect(url_for("buyer.favourite"))

    db.execute(
        """DELETE FROM favourite
           WHERE watch_id = ? AND user_id = ?""",
        (watch_id, user_id)
    )
    db.commit()
    flash("Watch removed from favourites")
    return redirect(url_for("buyer.favourite"))


@buyer_bp.route("/seller_profile/<user_id>", methods=["POST", "GET"])
@login_required_buyer
def seller_profile(user_id):
    form = MessageForm()
    buyer_id = session["buyer"]
    db = get_db()

    seller_user = db.execute(
        """SELECT * FROM seller
           WHERE user_id = ?""",
        (user_id,)
    ).fetchone()

    if seller_user is None:
        flash(f"There is no seller with username {user_id}")
        return redirect(url_for("watches.main"))

    blocked_sellers = db.execute(
        """SELECT * FROM blocked_sellers
           WHERE buyer_id = ? AND seller_id = ?""",
        (buyer_id, user_id)
    ).fetchone()

    seller_watches = db.execute(
        "SELECT * FROM watches WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    reviews = db.execute(
        """SELECT * FROM reviews
           WHERE seller_id = ?""",
        (user_id,)
    ).fetchall()

    if form.validate_on_submit():
        if blocked_sellers:
            flash("You cannot review a seller while they are blocked")
            return redirect(url_for("buyer.seller_profile", user_id=user_id))

        review = form.message.data.strip()
        if not review:
            flash("Review cannot be empty")
            return redirect(url_for("buyer.seller_profile", user_id=user_id))

        date = send_current_time()
        db.execute(
            """INSERT INTO reviews(seller_id, buyer_id, review, date)
               VALUES (?, ?, ?, ?)""",
            (user_id, buyer_id, review, date)
        )
        db.commit()
        flash("Review was successfully sent")
        return redirect(url_for("buyer.seller_profile", user_id=user_id))

    return render_template(
        "seller_profile.html",
        seller_watches=seller_watches,
        user_id=user_id,
        form=form,
        reviews=reviews,
        blocked_sellers=blocked_sellers,
        title="Seller Profile",
    )


@buyer_bp.route("/block_seller/<seller_id>")
@login_required_buyer
def block_seller(seller_id):
    buyer_id = session["buyer"]
    db = get_db()

    seller_user = db.execute(
        "SELECT * FROM seller WHERE user_id = ?",
        (seller_id,)
    ).fetchone()

    if seller_user is None:
        flash("Seller not found")
        return redirect(url_for("watches.main"))

    already_blocked = db.execute(
        """SELECT * FROM blocked_sellers
           WHERE seller_id = ?
           AND buyer_id = ?""",
        (seller_id, buyer_id)
    ).fetchone()

    if not already_blocked:
        db.execute(
            "INSERT INTO blocked_sellers VALUES (?, ?)",
            (buyer_id, seller_id)
        )
        db.commit()
        flash(f"{seller_id} was blocked")
        return redirect(url_for("buyer.seller_profile", user_id=seller_id))

    flash(f"{seller_id} is already blocked")
    return redirect(url_for("watches.main"))


@buyer_bp.route("/unblock_seller/<seller_id>")
@login_required_buyer
def unblock_seller(seller_id):
    db = get_db()
    buyer_id = session["buyer"]

    seller_user = db.execute(
        "SELECT * FROM seller WHERE user_id = ?",
        (seller_id,)
    ).fetchone()

    if seller_user is None:
        flash("Seller not found")
        return redirect(url_for("watches.main"))

    already_blocked = db.execute(
        """SELECT * FROM blocked_sellers
           WHERE seller_id = ?
           AND buyer_id = ?""",
        (seller_id, buyer_id)
    ).fetchone()

    if already_blocked:
        db.execute(
            "DELETE FROM blocked_sellers WHERE seller_id = ? AND buyer_id = ?",
            (seller_id, buyer_id)
        )
        db.commit()
        flash(f"{seller_id} was unblocked")
        return redirect(url_for("buyer.seller_profile", user_id=seller_id))

    flash(f"{seller_id} is not blocked")
    return redirect(url_for("watches.main"))


@buyer_bp.route("/blocked_sellers")
@login_required_buyer
def blocked_sellers():
    db = get_db()
    buyer_id = session["buyer"]
    blocked_sellers = db.execute(
        """SELECT * FROM blocked_sellers
           WHERE buyer_id = ?""",
        (buyer_id,)
    ).fetchall()
    return render_template(
        "blocked_sellers.html",
        blocked_sellers=blocked_sellers,
        title="blocked sellers",
    )


@buyer_bp.route("/help_buyer", methods=["POST", "GET"])
@login_required_buyer
def help_buyer():
    form = QuestionForm()
    db = get_db()
    user_id = session["buyer"]
    responded_messages_buyer = db.execute(
        """SELECT * FROM responded_messages_buyer
           WHERE buyer_id = ?
           ORDER BY date DESC;""",
        (user_id,)
    ).fetchall()

    if form.validate_on_submit():
        message = form.message.data.strip()
        if not message:
            flash("Message cannot be empty")
            return redirect(url_for("buyer.help_buyer"))

        date = send_current_time()
        db.execute(
            """INSERT INTO messages_to_response_buyer(buyer_id, message, date)
               VALUES (?, ?, ?)""",
            (user_id, message, date)
        )
        db.commit()
        flash("Message was successfully sent")
        return redirect(url_for("buyer.help_buyer"))

    return render_template(
        "help.html",
        form=form,
        responded_messages_buyer=responded_messages_buyer,
        title="Help",
    )


@buyer_bp.route("/change_password", methods=["GET", "POST"])
@login_required_buyer
def change_password():
    message = ""
    form_budget = EditBudget()
    form_password = EditPassword()
    db = get_db()

    user = db.execute(
        "SELECT * FROM buyer WHERE user_id = ?",
        (session["buyer"],)
    ).fetchone()

    if user is None:
        session.clear()
        flash("Buyer account was not found. Please log in again.")
        return redirect(url_for("auth.login"))

    budget = user["budget"]
    user_id = session["buyer"]

    if form_password.validate_on_submit():
        password = user["password"]
        password_to_check = form_password.password_to_check.data

        if not check_password_hash(password, password_to_check):
            form_password.password_to_check.errors.append("wrong password")
        else:
            new_password = generate_password_hash(form_password.new_password.data)
            db.execute(
                "UPDATE buyer SET password = ? WHERE user_id = ?",
                (new_password, user_id)
            )
            db.commit()
            message = "successful!"
            flash("Password changed successfully")
            return redirect(url_for("buyer.profile"))

    return render_template(
        "profile.html",
        title="Profile",
        budget=budget,
        form_password=form_password,
        message=message,
        form_budget=form_budget,
    )
