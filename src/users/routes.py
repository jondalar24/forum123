"""Routes module of 'users' package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, flash
from flask import make_response, redirect, render_template, request, url_for

from src.users.forms import LoginForm, RegistrationForm
from src.users.models import User, UserSession
from src.database import session_var

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response


bp = Blueprint("users", __name__, template_folder="templates")

def is_user_active(user_id):
    session = session_var.get()
    active_session = session.query(UserSession).filter_by(user_id=user_id).first()
    if active_session:
        return True
    return False

@bp.route("/registration", methods=["POST", "GET"])
def registration() -> str | Response:
    """Handle user's registration form."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.get_user_by_username(form.username.data)
        if user:
            flash("El usuario ya existe")
            return redirect(url_for("users.login"))
        User.create_user(form.username.data, form.password.data, form.role.data)
        return redirect(url_for("users.login"))
    return render_template("registration.html", form=form)


@bp.route("/login", methods=["POST", "GET"])
def login() -> str | Response:
    """Handle user's login form."""
    form = LoginForm()
    if form.validate_on_submit() and (user := User.get_user_by_credentials(form.username.data, form.password.data)):
        user_session = user.create_session()

        if user.role=="teacher":
            response = make_response(redirect(url_for("ia.dashboard_teacher")))
        else:
            response = make_response(redirect(url_for("topics.topics")))
        response.set_cookie("session_id", user_session.session_id, max_age=60*60*24, path='/')
        return response
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout() -> Response:
    """Log out users."""
    session_id = request.cookies.get("session_id")
    session_to_delete = None
    print(f"Attempting to logout session: {session_id}")
    if session_id is not None:
        session_to_delete = UserSession.get_user_session_by_session_id(session_id)
        print(f"Session to delete: {session_to_delete}")
    if session_to_delete:
        session_to_delete.delete()
        print("session deteled")
    else:
        print("No session found to delete")
    response = make_response(redirect(url_for("users.login")))
    response.set_cookie("session_id", '', expires=0)  # Limpiar la cookie
    return response

