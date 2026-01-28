from app import db

class Assessment(db.Model):
    __tablename__ = 'assessment'

    asm_id = db.Column(db.Integer, primary_key=True)

    cou_id = db.Column(
        db.Integer,
        db.ForeignKey('course.cou_id', ondelete='CASCADE'),
        nullable=False
    )

    asm_title = db.Column(db.Text, nullable=False)
    asm_description = db.Column(db.Text)
    asm_type = db.Column(
        db.String(50),
        nullable=False,
         default='diagnostico'

    )
    asm_status = db.Column(
        db.String(20),
        nullable=False,
        default='borrador'
    )

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.usr_id', ondelete='RESTRICT'),
        nullable=False
    )
    

    def __repr__(self):
        return f"<Assessment {self.asm_title}>"
    