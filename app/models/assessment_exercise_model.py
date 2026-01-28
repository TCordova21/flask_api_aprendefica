from app import db

class AssessmentExercise(db.Model):
    __tablename__ = 'assessment_exercise'

    ase_id = db.Column(db.Integer, primary_key=True)
    
    asm_id = db.Column(
        db.Integer, 
        db.ForeignKey('assessment.asm_id', ondelete='CASCADE'), 
        nullable=False
    )
    
    ex_id = db.Column(
        db.Integer, 
        db.ForeignKey('exercise.ex_id', ondelete='CASCADE'), 
        nullable=False
    )

    ase_order_index = db.Column(db.Integer, nullable=False, default=1)
    ase_created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relaciones
    assessment = db.relationship('Assessment', backref=db.backref('assessment_exercises', cascade='all, delete-orphan'))
    exercise = db.relationship('Exercise', backref=db.backref('exercise_assessments', cascade='all, delete-orphan'))

    # Restricciones de unicidad (aunque ya están en DB, es bueno tenerlas presentes)
    __table_args__ = (
        db.UniqueConstraint('asm_id', 'ex_id', name='unique_asm_ex'),
        db.UniqueConstraint('asm_id', 'ase_order_index', name='unique_asm_order'),
    )

    def __repr__(self):
        return f"<AssessmentExercise {self.ase_id} - Order {self.ase_order_index}>"