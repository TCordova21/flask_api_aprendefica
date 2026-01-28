from app import db

class Course(db.Model):
    __tablename__ = 'course'

    cou_id = db.Column(db.Integer, primary_key=True)
    cou_course_name = db.Column(db.String(100), nullable=False)
    cou_description = db.Column(db.Text, nullable=False)
    cou_duration = db.Column(db.Integer)
    cou_difficulty  = db.Column(db.String(20), nullable=False)
    cou_visibility  = db.Column(db.String(20), nullable=False)
    cou_status = db.Column(db.String(20), nullable=False, default='borrador')
    cou_created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.usr_id', ondelete='RESTRICT'),
        nullable=False
    )

    cou_thumbnail = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Course {self.cou_course_name}>"
    


