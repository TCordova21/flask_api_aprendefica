from app import ma
from app.models.assessment_model import Assessment

class AssessmentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Assessment
        load_instance = True

    asm_id = ma.auto_field(dump_only=True)
    cou_id = ma.auto_field(required=True)
    asm_title = ma.auto_field(required=True)
    asm_description = ma.auto_field()
    asm_type = ma.auto_field(required=True)
    asm_status = ma.auto_field(required=True)
    created_at = ma.auto_field(dump_only=True)
    created_by = ma.auto_field(required=True)

# Para una sola instancia
assessment_schema = AssessmentSchema()

# Para múltiples instancias
assessments_schema = AssessmentSchema(many=True)

class AssessmentBasicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Assessment
        load_instance = True

    asm_id = ma.auto_field(dump_only=True)
    asm_title = ma.auto_field()
    asm_type = ma.auto_field()
    asm_status = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    created_by = ma.auto_field()
# Para una sola instancia con campos básicos
assessment_basic_schema = AssessmentBasicSchema()
# Para múltiples instancias con campos básicos
assessments_basic_schema = AssessmentBasicSchema(many=True)