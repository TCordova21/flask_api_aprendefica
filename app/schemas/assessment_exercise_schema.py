from app import ma
from app.models.assessment_exercise_model import AssessmentExercise
from app.schemas.exercise_schema import exercise_schema

class AssessmentExerciseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AssessmentExercise
        load_instance = True

    ase_id = ma.auto_field(dump_only=True)
    asm_id = ma.auto_field(required=True)
   

# Esquema para ver el detalle del ejercicio dentro de la evaluación
class AssessmentExerciseDetailSchema(AssessmentExerciseSchema):
  
    exercise = ma.Nested("ExerciseSchemaBasic", dump_only=True)
    pass

assessment_exercise_schema = AssessmentExerciseSchema()
assessment_exercises_schema = AssessmentExerciseSchema(many=True)
assessment_exercise_detail_schema = AssessmentExerciseDetailSchema()
assessment_exercises_detail_schema = AssessmentExerciseDetailSchema(many=True)

class AssessmentExerciseDetailByCourseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AssessmentExercise
        load_instance = True

    ase_id = ma.auto_field(dump_only=True)
    asm_id = ma.auto_field()
    ase_order_index = ma.auto_field()
    
    # Anidamos el objeto ejercicio completo
    exercise = ma.Nested(exercise_schema, dump_only=True)

# Instancia para múltiples ejercicios dentro de una evaluación
assessment_exercises_detail_by_course_schema = AssessmentExerciseDetailByCourseSchema(many=True)