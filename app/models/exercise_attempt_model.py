from app import db

class ExerciseAttempt(db.Model):
    __tablename__ = 'exercise_attempt'

    exa_id = db.Column(db.Integer, primary_key=True)
    ex_id = db.Column(
        db.Integer, 
        db.ForeignKey('exercise.ex_id', ondelete='CASCADE'), 
        nullable=False
    )
    enr_id = db.Column(
        db.Integer, 
        db.ForeignKey('enrollment.enr_id', ondelete='CASCADE'), 
        nullable=False
    )
    
    exa_attempt_no = db.Column(db.Integer, nullable=False, default=1)
    exa_answer = db.Column(db.Text, nullable=False)
    exa_is_correct = db.Column(db.Boolean)
    exa_created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('ex_id', 'enr_id', 'exa_attempt_no', name='uq_exa_attempt'),
    )