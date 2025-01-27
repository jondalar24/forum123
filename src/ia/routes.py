from flask import Blueprint, render_template, request, redirect, url_for, flash # type: ignore
from src.topics.models import Topic
from src.posts.models import Post
#from src.posts.forms import PostForm
#from src.topics.forms import TopicForm
from src.ia.worker import ask_forum_question  # Importamos funcion de worker.py
from src.database import session_var
from src.users.utils import get_current_user
from src.posts.utils import create_teacher_response

bp = Blueprint("ia", __name__, url_prefix='/ia', template_folder="templates")

@bp.route('/ask/<int:topic_id>', methods=['GET', 'POST'])
def ask(topic_id):
    current_user = get_current_user()
    if current_user is None:
        return redirect(url_for("users.login"))
    topic = Topic.get(topic_id)
    if not topic:
        return render_template("404.html", current_user=current_user)    
    if request.method == 'POST':
        question = request.form['question']
        print(f"question enviada desde el front en routes.py antes de preguntar a ia: {question}")  # Debugger
        #llamar a la lógica para que gestione la pregunta
        answer = ask_forum_question(question,topic)
        print(f"Respuesta obtenida: {answer}")  # Debugger
        
        #mostrar la respuesta al usuario
        return render_template('response.html', topic=topic, answer=answer, current_user=current_user)
    # Renderizar el formulario para enviar preguntas
    return render_template('ask_ia.html', topic=topic, current_user=current_user)

@bp.route('/dashboard_teacher')
def dashboard_teacher():
    current_user = get_current_user()
    if current_user is None:
        return redirect(url_for("users.login"))
    session = session_var.get()
    current_user = get_current_user()
    # Obtener los topics y posts pendientes
    pending_topics = session.query(Topic).filter_by(pending_for_teacher=True).all()
    pending_posts = session.query(Post).filter_by(pending_for_teacher=True).all()
    
    return render_template('dashboard_teacher.html', pending_topics=pending_topics, pending_posts=pending_posts, current_user=current_user)

@bp.route('/teacher_respond_topic/<int:topic_id>', methods=['POST'])
def teacher_respond_topic(topic_id):
    current_user = get_current_user()
    if current_user is None:
        return redirect(url_for("users.login"))
    
    session = session_var.get()
    topic = session.query(Topic).get(topic_id)
    if not topic:
        return render_template("404.html", current_user=current_user)

    # Procesar la respuesta enviada
    response_body = request.form.get("response")
    if response_body:
        create_teacher_response(session, response_body, topic, current_user.id)
        flash("Respuesta enviada correctamente.", "success")
        return redirect(url_for('ia.dashboard_teacher'))
    
    flash("Por favor, escribe una respuesta antes de enviar.", "danger")
    
    return redirect(url_for('ia.dashboard_teacher'))
    
    

@bp.route('/teacher_respond_post/<int:post_id>', methods=['POST'])
def teacher_respond_post(post_id):
    current_user = get_current_user()
    if current_user is None:
        return redirect(url_for("users.login"))
    
    session = session_var.get()
    post = session.query(Post).get(post_id)
    if not post:
        return render_template("404.html", current_user=current_user)

    topic = post.topic
    if not topic:
        return render_template("404.html", current_user=current_user)

    # Procesar la respuesta enviada
    response_body = request.form.get("response")
    if response_body:
        create_teacher_response(session, response_body, topic, current_user.id)
        post.pending_for_teacher = False  # Marcar el post original como resuelto
        session.commit()
        flash("Respuesta enviada correctamente.", "success")
        return redirect(url_for('ia.dashboard_teacher'))
    
    flash("Por favor, escribe una respuesta antes de enviar.", "danger")
    return redirect(url_for('ia.dashboard_teacher'))
    
    

