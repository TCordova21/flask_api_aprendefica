from app import db
from app.models.subtopic_dependency_model import SubtopicDependency

class Subtopic(db.Model):
    __tablename__ = 'subtopic'

    sub_id = db.Column(db.Integer, primary_key=True)
    dom_id = db.Column(db.Integer, db.ForeignKey('domain.dom_id', ondelete='CASCADE'), nullable=False)
    sub_name = db.Column(db.String(200), nullable=False)
    sub_description = db.Column(db.Text)
    sub_created_at = db.Column(db.DateTime, server_default=db.func.now())

    domain = db.relationship(
        'Domain',
        back_populates='subtopics'
    )
   

      # 🔗 prerrequisitos (KST)
    prerequisites = db.relationship(
        'Subtopic',
        secondary='subtopic_dependency',
        primaryjoin=sub_id == SubtopicDependency.sub_id,
        secondaryjoin=sub_id == SubtopicDependency.prerequisite_id,
        lazy='select'

    )

