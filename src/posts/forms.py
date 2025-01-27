"""Forms module of 'posts' package."""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):  # type: ignore
    """A class for a post creation form."""

    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Create post")

class EditPostForm(FlaskForm):  # type: ignore
    """A class for a post editing form."""
    
    body = TextAreaField("Edit Body", validators=[DataRequired()])
    submit = SubmitField("Update post")