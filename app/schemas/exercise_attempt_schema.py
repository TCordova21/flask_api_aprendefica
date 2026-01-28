from app import ma
from app.models.exercise_attempt_model import ExerciseAttempt

class ExerciseAttemptSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ExerciseAttempt
        load_instance = True

    exa_id = ma.auto_field(dump_only=True)
    ex_id = ma.auto_field(required=True)
    enr_id = ma.auto_field(required=True)
    exa_attempt_no = ma.auto_field()
    exa_answer = ma.auto_field(required=True)
    exa_is_correct = ma.auto_field()
    exa_created_at = ma.auto_field(dump_only=True)

exercise_attempt_schema = ExerciseAttemptSchema()
exercise_attempts_schema = ExerciseAttemptSchema(many=True)