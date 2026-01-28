from app import ma
from app.models.enrollment_model import Enrollment
from app.schemas.user_schema import user_schema
from app.schemas.course_instance_schema import course_instance_schema, course_instance_with_course_schema
from app.schemas.course_schema import course_schema 


class EnrollmentSchema(ma.SQLAlchemySchema):


    class Meta:
        model = Enrollment
        load_instance = True

    enr_id = ma.auto_field(dump_only=True)

    usr_id = ma.auto_field(dump_only=True)
    coi_id = ma.auto_field(required=True)

    enr_date = ma.auto_field(dump_only=True)
    enr_status = ma.auto_field()
    enr_progress = ma.auto_field(dump_only=True)

    last_accessed_at = ma.auto_field(dump_only=True)

enrollment_schema = EnrollmentSchema()
enrollments_schema = EnrollmentSchema(many=True)



class EnrollmentDetailSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Enrollment
        load_instance = True

    enr_id = ma.auto_field(dump_only=True)
    enr_status = ma.auto_field()
    enr_progress = ma.auto_field()
    enr_date = ma.auto_field()
    last_accessed_at = ma.auto_field()

    user = ma.Nested(user_schema)
    course_instance = ma.Nested(course_instance_with_course_schema)
   

enrollment_detail_schema = EnrollmentDetailSchema()
enrollments_detail_schema = EnrollmentDetailSchema(many=True)


class EnrollmentBasicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Enrollment
        load_instance = True

    enr_id = ma.auto_field(dump_only=True)
    coi_id = ma.auto_field(required=True)
    usr_id = ma.auto_field(required=True)
    enr_status = ma.auto_field()
    enr_progress = ma.auto_field()
    enr_date = ma.auto_field()
    last_accessed_at = ma.auto_field()

    course_instance = ma.Nested(course_instance_with_course_schema)


enrollment_basic_schema = EnrollmentBasicSchema()
enrollments_basic_schema = EnrollmentBasicSchema(many=True)

# app/schemas/enrollment_schema.py

class EnrollmentStudentListSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Enrollment
        load_instance = True

    enr_id = ma.auto_field(dump_only=True)
    enr_status = ma.auto_field()
    enr_progress = ma.auto_field()
    enr_date = ma.auto_field()
    last_accessed_at = ma.auto_field()

    # Usamos Nested pero podemos especificar solo los campos que queremos del usuario
    # para no traer fechas de creación, roles, etc.
    user = ma.Nested(user_schema, only=("usr_id", "usr_first_name", "usr_last_name", "usr_email"))

# Instancias para el uso en el controlador
enrollment_student_list_schema = EnrollmentStudentListSchema()
enrollments_student_list_schema = EnrollmentStudentListSchema(many=True)    