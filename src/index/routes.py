"""Routes module of 'index' package."""

from __future__ import annotations

from flask import Blueprint # type: ignore
from flask import render_template, request # type: ignore
from src.database import session_var
from src.users.models import User, UserSession


bp = Blueprint("index", __name__, template_folder="templates")


@bp.route("/")
@bp.route("/index")
def index() -> str:
    """Handle index page."""
    session = session_var.get()

    # Verificar si la cookie de la sesión está presente
    session_id = request.cookies.get('session_id')
    if session_id:
        user_session = session.query(UserSession).filter_by(session_id=session_id).first()
        if user_session:
            # El usuario está autenticado, obtenemos el objeto `User`
            current_user = session.query(User).filter_by(id=user_session.user_id).first()
        else:
            current_user = None
    else:
        current_user = None

    users = session.query(User).all()
    active_sessions = session.query(UserSession).all()
    active_user_ids = {user_session.user_id for user_session in active_sessions}
    print(f"usuario recuperado: {current_user}")

    
    # Pasar user_id al template para determinar si el usuario está autenticado
    return render_template("index.html", users=users, active_user_ids=active_user_ids, current_user=current_user)