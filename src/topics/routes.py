"""Routes module of 'topics' package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint # type: ignore
from flask import redirect, render_template, url_for, flash # type: ignore

from src.topics.forms import TopicForm, EditTopicForm
from src.topics.models import Topic
from src.users.utils import get_current_user
from src.database import session_var

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response # type: ignore


bp = Blueprint("topics", __name__, template_folder="templates")


@bp.route("/topics/<int:topic_id>")
def topic_page(topic_id: int) -> str | Response:
    """Handle topic page."""
    if (current_user := get_current_user()) is None:
        return redirect(url_for("users.login"))
    if not (topic := Topic.get(topic_id)):
        return render_template("404.html", current_user=current_user)
    return render_template("topic.html", current_user=current_user, topic=topic)


@bp.route("/topics")
def topics() -> str | Response:
    """Handle topics page."""
    if (current_user := get_current_user()) is not None:
        topic_list = Topic.get_topics()
        return render_template("topics.html", topic_list=topic_list, current_user=current_user)
    return redirect(url_for("users.login"))


@bp.route("/topics/create", methods=["POST", "GET"])
def create_topic() -> str | Response:
    """Handle create topic page."""
    if (current_user := get_current_user()) is None:
        return redirect(url_for("users.login"))
    # Renderizar si aún no hay POST (hacer un GET)
    form = TopicForm()
    if not form.validate_on_submit():
        return render_template("topics-create.html", form=form, current_user=current_user)
    #Determinar el estado del boolean según rol del usuario
    pending_for_teacher = False if current_user.role == "teacher" else True
    #crear el topic
    Topic.create_topic(form.title.data, form.description.data, 
                       current_user.id, current_user.role,
                       pending_for_teacher=pending_for_teacher
    )
    return redirect(url_for("topics.topics"))


"""@bp.route("/topics/delete/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id: int) -> Response:
    #Permitir al administrador eliminar un topic y todos sus posts.
    session = session_var.get()
    topic = session.query(Topic).filter_by(id=topic_id).first()

    if topic:
        session.delete(topic)  # Esto eliminará el topic y todos los posts relacionados
        session.commit()
        flash("Topic y todos los posts asociados han sido eliminados.", "success")
    else:
        flash("El topic no existe.", "danger")

    return redirect(url_for("admin.list_posts"))

@bp.route("/topics/edit/<int:topic_id>", methods=["POST", "GET"])
def edit_topic(topic_id: int):
    #Edit a topic
    session = session_var.get()
    topic = session.query(Topic).filter_by(id=topic_id).first()

    if topic is None:
        flash("Topic does not exist.", "danger")
        return redirect(url_for("admin.list_posts"))

    form = EditTopicForm(obj=topic)  # Populate form with existing data
    if form.validate_on_submit():
        topic.title = form.title.data  # Update the topic's title
        topic.description = form.description.data  # Update the topic's description
        topic.pending_for_teacher = form.pending_for_teacher.data == "True"
        session.commit()
        flash("Topic updated successfully.", "success")
        return redirect(url_for("admin.list_posts"))

    return render_template("edit_topic.html", form=form, topic=topic)
    """