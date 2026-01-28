from app import db

class SubtopicDependency(db.Model):
    __tablename__ = 'subtopic_dependency'

    sub_id = db.Column(
        db.Integer,
        db.ForeignKey('subtopic.sub_id', ondelete='CASCADE'),
        primary_key=True
    )
    prerequisite_id = db.Column(
        db.Integer,
        db.ForeignKey('subtopic.sub_id', ondelete='CASCADE'),
        primary_key=True
    )
