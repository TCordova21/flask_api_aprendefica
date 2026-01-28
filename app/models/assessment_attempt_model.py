from app import db
from datetime import datetime

class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempt'

    asma_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asm_id = db.Column(db.Integer, db.ForeignKey('assessment.asm_id', ondelete='CASCADE'), nullable=False)
    enr_id = db.Column(db.Integer, db.ForeignKey('enrollment.enr_id', ondelete='CASCADE'), nullable=False)
    attempt_no = db.Column(db.Integer, nullable=False, default=1)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    is_passed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Numeric(5, 2), nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    # Relaciones
    assessment = db.relationship('Assessment', backref='attempts')
    enrollment = db.relationship('Enrollment', backref='assessment_attempts')