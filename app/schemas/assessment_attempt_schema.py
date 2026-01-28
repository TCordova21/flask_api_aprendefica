from app import ma
from app.models.assessment_attempt_model import AssessmentAttempt

class AssessmentAttemptSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AssessmentAttempt
        load_instance = True
        include_fk = True

assessment_attempt_schema = AssessmentAttemptSchema()
assessment_attempts_schema = AssessmentAttemptSchema(many=True)