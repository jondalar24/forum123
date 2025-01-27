"""Models module of 'topics' package."""

from __future__ import annotations

from typing import Final, TYPE_CHECKING

from sqlalchemy import Column, DateTime, desc, ForeignKey, func, Boolean, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base, session_var
from src.posts.models import Post

if TYPE_CHECKING:
    from datetime import datetime
    from src.users.models import User
    #from src.posts.models import Post


class Topic(Base):
    """A model class for topics table."""

    __tablename__ = "topics"

    id: int = Column(Integer, primary_key=True)  # noqa: A003
    author_id: int = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role: str = Column(String(50), nullable = False)
    created_at: datetime = Column(DateTime, server_default=func.now(), nullable=False)
    description: str = Column(Text, nullable=False)
    title: str = Column(String(30), nullable=False)
    author: User = relationship("User", uselist=False)
    pending_for_teacher = Column(Boolean, default=True)

    # añadir un delete on cascade para eliminar todos los posts al borrar un topic
    posts = relationship("Post", back_populates="topic",order_by="Post.created_at", cascade="all, delete-orphan", lazy="dynamic")

    SORTING_FIELDS: Final = ("created_at", "title")
    SORTING_ORDER: Final = ("asc", "desc")

    @classmethod    
    def create_topic(cls, title: str, description: str, author_id: int, role:str,pending_for_teacher:bool) -> Topic:
        
        """Use this method to create a new topic."""
        new_topic = cls(title=title,
                        description=description,
                        author_id=author_id, role=role,
                        pending_for_teacher=pending_for_teacher)
        
        session = session_var.get()
        session.add(new_topic)
        session.commit()
        
        return new_topic

    def create_post(self, body: str, author_id: int, role:str, pending_for_teacher:bool) -> Post:
        #from src.posts.models import Post
        """Use this method to create a new post."""
        if pending_for_teacher is None:
            pending_for_teacher = True if role != "teacher" else False
        
        new_post = Post(body=body,
                        author_id=author_id, 
                        topic_id=self.id, 
                        role=role,
                        pending_for_teacher=pending_for_teacher)
        session = session_var.get()
        session.add(new_post)
        session.commit()
        
        return new_post

    @staticmethod
    def get_topics(sorting: dict[str, str] | None = None,
                   author_ids: list[int] | None = None,
                   created_before: datetime | None = None,
                   created_after: datetime | None = None) -> list[Topic]:
        """Use this method to get all topics from topics table."""
        sorting = {"field": "created_at", "order": "asc"} if sorting is None else sorting
        session = session_var.get()
        topics_query = session.query(Topic)
        if author_ids:
            topics_query = topics_query.filter(Topic.author_id.in_(author_ids))
        if created_after:
            topics_query = topics_query.filter(Topic.created_at > created_after)
        if created_before:
            topics_query = topics_query.filter(Topic.created_at < created_before)
        if sorting["order"] == "desc":
            return topics_query.order_by(desc(sorting["field"])).all()
        topics_ordened = topics_query.order_by(sorting["field"]).all()
        
        return topics_ordened
    
    @classmethod
    def delete_topic_by_id(cls, topic_id: int) -> bool:
        session = session_var.get()
        topic = session.query(cls).filter_by(id=topic_id).first()
        if topic:
            session.delete(topic)  # Esto eliminará el topic y todos los posts relacionados
            session.commit()
            return True
        
        return False

    @staticmethod
    def get(topic_id: int) -> Topic | None:
        """Use this method to get a topic with a certain id."""
        session = session_var.get()
        topics = session.query(Topic).filter_by(id=topic_id).first()
        
        return topics
