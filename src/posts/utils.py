"""Some utilities for working with posts from teacher dashboard"""

from src.posts.models import Post


def create_teacher_response(session, body, topic, author_id):
    """Crear una respuesta del profesor y actualizar el estado del topic."""
    # Crear el nuevo post
    new_post = Post(
        body=body,
        author_id=author_id,
        role="teacher",
        topic_id=topic.id,
        pending_for_teacher=False
    )
    session.add(new_post)

    # Marcar todos los posts previos del topic como resueltos
    previous_posts = session.query(Post).filter_by(topic_id=topic.id, pending_for_teacher=True).all()
    for post in previous_posts:
        post.pending_for_teacher = False

    # Marcar el topic como resuelto
    topic.pending_for_teacher = False
    session.commit()
