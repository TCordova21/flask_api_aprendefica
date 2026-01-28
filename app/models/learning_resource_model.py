from app import db 

class LearningResource(db.Model):
    __tablename__= 'learning_resource'

    lrn_id = db.Column(db.Integer, primary_key=True)

    sub_id = db.Column(
        db.Integer,
        db.ForeignKey('subtopic.sub_id', ondelete='CASCADE'),
        nullable=False
    )

    lrn_title = db.Column(db.String(150), nullable=False)
    lrn_description = db.Column(db.Text)

    lrn_type = db.Column(
        db.String(30),
        nullable=False
    )

    lrn_url = db.Column(db.Text)
    lrn_content = db.Column(db.Text)

    lrn_order = db.Column(db.Integer, nullable=False, default=1)

    lrn_status = db.Column(
        db.String(20),
        nullable=False,
        default='activo'
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    # 🔗 Relación
    subtopic = db.relationship(
        'Subtopic',
        backref=db.backref('learning_resources', cascade='all, delete-orphan')
    )