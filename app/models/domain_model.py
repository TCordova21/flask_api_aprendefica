from app import db

class Domain(db.Model):
    __tablename__ = 'domain'

    dom_id = db.Column(db.Integer, primary_key=True)
    cou_id = db.Column(db.Integer, db.ForeignKey('course.cou_id', ondelete='CASCADE'), nullable=False)
    dom_name = db.Column(db.String(150), nullable=False)
    dom_description = db.Column(db.Text)
    dom_created_at = db.Column(db.DateTime, server_default=db.func.now())

    # 👇 usa STRING, no la clase directa
    subtopics = db.relationship(
        'Subtopic',
        back_populates='domain',
        cascade='all, delete-orphan'
    )
