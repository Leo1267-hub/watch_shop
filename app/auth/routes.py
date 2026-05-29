from flask import Blueprint, render_template, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_db
from app.forms import RegistrationForm, LoginForm


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        role = form.role.data.lower()

        if role == "admin":
            if user_id == "admin":
                if password == "0621":
                    session.clear()
                    session["admin"] = user_id
                    return redirect(url_for("admin"))
                else:
                    form.password.errors.append("wrong password")
            else:
                form.user_id.errors.append("user id doesnt exist")

            return render_template("login.html", form=form, title="Login")

        if role not in {"seller", "buyer"}:
            form.role.errors.append("Invalid role")
            return render_template("login.html", form=form, title="Login")

        db = get_db()
        user = db.execute(
            f"SELECT * FROM {role} WHERE user_id = ?;",
            (user_id,)
        ).fetchone()

        if user is None:
            form.user_id.errors.append("user id doesnt exist")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("wrong password")
        else:
            session.clear()
            session[role] = user_id

            if role == "seller":
                return redirect(url_for("seller.seller"))

            return redirect(url_for("watches.main"))

    return render_template("login.html", form=form, title="Login")


@auth_bp.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("watches.main"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        role = form.role.data.lower()

        if role not in {"seller", "buyer"}:
            form.role.errors.append("Invalid role")
            return render_template("register.html", form=form, title="Registration")

        db = get_db()

        clash = db.execute(
            f"SELECT * FROM {role} WHERE user_id = ?;",
            (user_id,)
        ).fetchone()

        if clash is not None or user_id == "admin":
            form.user_id.errors.append("user id already taken")
        else:
            db.execute(
                f"INSERT INTO {role} (user_id, password) VALUES (?, ?);",
                (user_id, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for("auth.login"))

    return render_template("register.html", form=form, title="Registration")