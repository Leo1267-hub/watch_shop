from flask import Blueprint, render_template, session

from app.database import get_db
from app.forms import EditBudget, EditPassword
from app.utils.auth import login_required_buyer


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
