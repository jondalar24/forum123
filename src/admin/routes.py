from flask import Blueprint, render_template, redirect, url_for, request, flash # type: ignore
from src.users.models import User, UserSession
from src.database import session_var
from src.topics.models import Topic
from src.posts.models import Post
from src.users.models import User
#from src.users.utils import get_current_user
from src.posts.forms import EditPostForm
from src.topics.forms import EditTopicForm

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

# Definir la contraseña de administrador
ADMIN_PASSWORD = "admin" 

@bp.route("/login", methods=["GET", "POST"])
def admin_login():
    """Página de login para el administrador."""    
    if request.method == "POST":
        password = request.form.get("password")
        
        if password == ADMIN_PASSWORD:
            session = session_var.get()
            session.execute("DELETE FROM user_session")
            session.commit()

            # Eliminar la cookie 'session_id'
            response = redirect(url_for("admin.dashboard"))
            response.set_cookie("session_id", '', expires=0)
            return response
        else:
            flash("Contraseña incorrecta", "danger")
    
    return render_template("admin_login.html")

@bp.route("/dashboard")
def dashboard():
    """Panel de control del administrador."""
    return render_template("dashboard.html")


@bp.route("/list_users")
def list_users():
    """Lista de usuarios, solo accesible si está autenticado como admin."""       
    session = session_var.get()
    #pedimos una lista de todos los usuarios
    users = session.query(User).all()
    
    # renderizamos una lista de usuarios con opcion de eliminarlos
    active_sessions = session.query(UserSession).all()
    active_user_ids = {user_session.user_id for user_session in active_sessions}
    return render_template("list_users.html", users=users, active_user_ids=active_user_ids)

@bp.route("/list_posts")
def list_posts():
    """Lista de posts y topics en el panel de administración."""
    session = session_var.get()
    posts = session.query(Post).all()
    topics = session.query(Topic).all()

    return render_template("admin_list_posts.html", posts=posts, topics=topics)

@bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Delete a single post."""
    if Post.delete_post_by_id(post_id):  # Assuming delete_post_by_id method exists
        flash("Post deleted successfully.", "success")
    else:
        flash("Post not found.", "danger")
    return redirect(url_for('admin.list_posts'))

@bp.route('/delete_topic/<int:topic_id>', methods=['POST'])
def delete_topic(topic_id):
    """Delete a topic and its associated posts."""
    if Topic.delete_topic_by_id(topic_id):  # Assuming delete_topic_by_id method exists
        flash("Topic and its associated posts deleted successfully.", "success")
    else:
        flash("Topic not found.", "danger")
    return redirect(url_for('admin.list_posts'))

@bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit a post's content and 'pending_for_teacher' status."""
    session = session_var.get()
    post = session.query(Post).get(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("admin.list_posts"))
    
    topic = post.topic
    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        post.body = form.body.data
        #post.pending_for_teacher = False if post.role == "teacher" else True
        session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("admin.list_posts"))
    return render_template("edit_post.html", form=form, post=post, topic=topic)

@bp.route('/edit_topic/<int:topic_id>', methods=['GET', 'POST'])
def edit_topic(topic_id):
    """Edit a topic's content and 'pending_for_teacher' status."""
    session = session_var.get()
    topic = session.query(Topic).get(topic_id)
    if not topic:
        flash("Topic not found.", "danger")
        return redirect(url_for("admin.list_posts"))
    
    form = EditTopicForm(obj=topic)
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.description = form.description.data
        topic.pending_for_teacher = form.pending_for_teacher.data == "True"
        session.commit()
        flash("Topic updated successfully.", "success")
        return redirect(url_for("admin.list_posts"))
    
    return render_template("edit_topic.html", form=form, topic=topic)

@bp.route('/toggle_pending_topic/<int:topic_id>', methods=['POST'])
def toggle_pending_topic(topic_id):
    """Alterna el estado de 'pending_for_teacher' de un topic."""
    session = session_var.get()
    topic = session.query(Topic).get(topic_id)
    if topic:
        topic.pending_for_teacher = not topic.pending_for_teacher  # Alterna el estado
        session.commit()
        flash("Estado de 'pending_for_teacher' del tema actualizado.", "success")
    else:
        flash("Tema no encontrado.", "danger")
    
    return redirect(url_for('admin.list_posts'))

@bp.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    """Permite eliminar usuarios."""
    session = session_var.get()
    user_to_delete = session.query(User).get(user_id)
    
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
        flash(f"Usuario {user_to_delete.username} eliminado con éxito.", "success")
    else:
        flash("Usuario no encontrado.", "danger")

    
    return redirect(url_for("admin.list_users"))
