
from app import ma
from app.models.exercise_model import Exercise

class ExerciseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Exercise
        load_instance = True

    ex_id = ma.auto_field(dump_only=True)
    sub_id = ma.auto_field(required=True)
    ex_statement = ma.auto_field(required=True)
    ex_expression = ma.auto_field()
    ex_instruction = ma.auto_field()
    ex_expected_answer = ma.auto_field(required=True)
    ex_difficulty = ma.auto_field()
    ex_is_active = ma.auto_field()

    ex_created_at = ma.auto_field(dump_only=True)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

class ExerciseSchemaBasic(ma.SQLAlchemySchema):
    class Meta:
        model = Exercise
        load_instance = True

    ex_id = ma.auto_field(dump_only=True)
    ex_statement = ma.auto_field(required=True)
    ex_expression = ma.auto_field()
    ex_instruction = ma.auto_field()
    ex_expected_answer = ma.auto_field(required=True)


exercise_schema_basic = ExerciseSchema()
exercises_schema_basic = ExerciseSchema(many=True)