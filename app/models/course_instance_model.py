from app import db

class CourseInstance(db.Model):
    __tablename__ = 'course_instance'

    coi_id = db.Column(db.Integer, primary_key=True)

    cou_id = db.Column(
        db.Integer,
        db.ForeignKey('course.cou_id', ondelete='CASCADE'),
        nullable=False
    )

    coi_name = db.Column(db.String(100), nullable=False)
    coi_ins_code = db.Column(db.String(10), unique=True, nullable=False)

    coi_created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.usr_id', ondelete='CASCADE'),
        nullable=False
    )

    coi_status = db.Column(db.String(20), nullable=False, default='activa')
    coi_start_date = db.Column(db.Date)
    coi_end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    course = db.relationship(
        'Course',
        backref=db.backref('instances', cascade='all, delete-orphan'),
        passive_deletes=True
    )

    def __repr__(self):
        return f"<CourseInstance {self.coi_code}>"
