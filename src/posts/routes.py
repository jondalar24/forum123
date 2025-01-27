"""Routes module of 'posts' package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint
from flask import redirect, render_template, url_for, flash

from src.posts.forms import PostForm, EditPostForm
from src.topics.models import Topic
from src.posts.models import Post
from src.users.utils import get_current_user
from src.database import session_var

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response # type: ignore


bp = Blueprint("posts", __name__, template_folder="templates")


@bp.route("/topics/<int:topic_id>/posts/create", methods=["POST", "GET"])
def create_post(topic_id: int) -> str | Response:  # noqa: CFQ004
    """Handle post creation page."""
    if (current_user := get_current_user()) is None:
        return redirect(url_for("users.login"))
    form = PostForm()
    if not (topic := Topic.get(topic_id)):
        return render_template("404.html", current_user=current_user.id)
    if form.validate_on_submit():
        #Determinar el estado del boolean según rol del usuario
        pending_for_teacher = False if current_user.role == "teacher" else True
        #crear el topic
        topic.create_post(form.body.data, current_user.id, current_user.role, pending_for_teacher=pending_for_teacher)
        return redirect(url_for("topics.topic_page", topic_id=topic.id))
    return render_template("posts-create.html", form=form, topic=topic, current_user=current_user)

"""@bp.route("/posts/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id: int) -> Response:
    #Permitir al administrador eliminar un post individualmente.
    session = session_var.get()
    post = session.query(Post).filter_by(id=post_id).first()

    if post:
        session.delete(post)
        session.commit()
        flash("El post ha sido eliminado.", "success")
    else:
        flash("El post no existe.", "danger")

    return redirect(url_for("admin.list_posts"))

@bp.route("/posts/edit/<int:post_id>", methods=["POST", "GET"])
def edit_post(post_id: int):
    #Opción de edición para el administrador
    session = session_var.get()
    post = session.query(Post).filter_by(id=post_id).first()

    if post is None:
        flash("Post does not exist.", "danger")
        return redirect(url_for("admin.list_posts"))

    form = EditPostForm(obj=post)  
    if form.validate_on_submit():
        post.body = form.body.data  # Update the post's body
        session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("admin.list_posts"))

    return render_template("edit_post.html", form=form, post=post)
    """