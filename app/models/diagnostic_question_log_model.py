from app import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class DiagnosticQuestionLog(db.Model):
    __tablename__ = 'diagnostic_question_log'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('diagnostic_session.session_id', ondelete='CASCADE'), nullable=False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subtopic.sub_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.ex_id'), nullable=False)
    status = db.Column(db.String(15), nullable=False, default='asked') # 'asked' o 'answered'
    asked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime, nullable=True)
    student_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)

    # Relaciones para facilitar consultas en schemas
    exercise = db.relationship('Exercise', backref='question_logs')
    subtopic = db.relationship('Subtopic', backref='question_logs')