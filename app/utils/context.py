from flask import g, session


def load_logged_in_user():
    g.seller = session.get("seller")
    g.buyer = session.get("buyer")
    g.admin = session.get("admin")