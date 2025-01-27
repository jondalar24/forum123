"""Forms module of 'topics' package."""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class TopicForm(FlaskForm):  # type: ignore
    """A class for a topic creation form."""

    title = TextAreaField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Create topic")

class EditTopicForm(FlaskForm):  # type: ignore
    """A class for a topic editing form."""
    
    title = TextAreaField("Edit Title", validators=[DataRequired()])
    description = TextAreaField("Edit Description", validators=[DataRequired()])
    pending_for_teacher = SelectField(
        "Estado Pendiente",
        choices=[("True", "Pendiente"), ("False", "Resuelto")]
    )
    submit = SubmitField("Update topic")