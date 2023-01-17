"""forum123's route module."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask import Blueprint
from flask import make_response, redirect, render_template, request, url_for

from src.database import session
from src.forms import LoginForm, RegistrationForm
from src.models import User, UserSession

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response


bp = Blueprint("routes", __name__)


@bp.route("/")
@bp.route("/index")
def index() -> str:
    """Handle index page."""
    users = session.query(User).all()
    session_id = request.cookies.get("session_id")
    user_session = session.query(UserSession).filter_by(session_id=session_id).first()

    current_user = None
    if user_session is not None:
        current_user = session.query(User).filter_by(id=user_session.user_id).one()

    return render_template("index.html", users=users, current_user=current_user)


@bp.route("/registration", methods=["POST", "GET"])
def registration() -> str:
    """Handle user's registration form."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
    return render_template("registration.html", form=form)


@bp.route("/login", methods=["POST", "GET"])
def login() -> str | Response:
    """Handle user's login form."""
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session_id = str(uuid.uuid4())
            user_session = UserSession(session_id=session_id, user_id=user.id)
            session.add(user_session)
            session.commit()

            response = make_response(redirect(url_for("routes.index")))
            response.set_cookie("session_id", session_id)
            return response
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout() -> Response:
    """Log out users."""
    session_id = request.cookies.get("session_id")
    if session_to_delete := session.query(UserSession).filter_by(session_id=session_id).first():
        session.delete(session_to_delete)
        session.commit()
    return redirect(url_for("routes.login"))
