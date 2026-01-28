import uuid
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID

class DiagnosticSession(db.Model):
    __tablename__ = 'diagnostic_session'

    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asm_id = db.Column(db.Integer, db.ForeignKey('assessment.asm_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.usr_id'), nullable=False)
    course_instance_id = db.Column(db.Integer, db.ForeignKey('course_instance.coi_id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    max_questions = db.Column(db.Integer, default=30)
    current_question_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='IN_PROGRESS')

    # Relaciones opcionales para facilitar consultas
    assessment = db.relationship('Assessment', backref='diagnostic_sessions')
    student = db.relationship('User', backref='diagnostic_sessions')
    course_instance = db.relationship('CourseInstance', backref='diagnostic_sessions')

