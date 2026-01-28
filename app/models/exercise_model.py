from app import db

class Exercise(db.Model):
    __tablename__ = 'exercise'

    ex_id = db.Column(db.Integer, primary_key=True)

    sub_id = db.Column(
        db.Integer,
        db.ForeignKey('subtopic.sub_id', ondelete='CASCADE'),
        nullable=False
    )

    ex_statement = db.Column(db.Text, nullable=False)
    ex_expression = db.Column(db.Text)
    ex_instruction = db.Column(db.Text)
    ex_expected_answer = db.Column(db.Text, nullable=False)
    ex_difficulty = db.Column(db.Integer)
    ex_is_active = db.Column(db.Boolean, default=True)

    ex_created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('sub_id',  name='uq_exercise_sub_order'),
    )
