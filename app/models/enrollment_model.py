from app import db

class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    enr_id = db.Column(db.Integer, primary_key=True)

    usr_id = db.Column(
        db.Integer,
        db.ForeignKey('users.usr_id', ondelete='CASCADE'),
        nullable=False
    )

    coi_id = db.Column(
        db.Integer,
        db.ForeignKey('course_instance.coi_id', ondelete='RESTRICT'),
        nullable=False
    )

    enr_date = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    enr_status = db.Column(
        db.String(20),
        nullable=False,
        default='activo'
    )

    enr_progress = db.Column(
        db.Numeric(5, 2),
        default=0
    )

    last_accessed_at = db.Column(db.DateTime)

    # Evita duplicados
    __table_args__ = (
        db.UniqueConstraint('usr_id', 'coi_id', name='uq_enrollment_user_instance'),
    )

    # Relaciones
    user = db.relationship('User', backref='enrollments')
    course_instance = db.relationship('CourseInstance', backref='enrollments')

    def __repr__(self):
        return f"<Enrollment user={self.usr_id} instance={self.coi_id}>"
