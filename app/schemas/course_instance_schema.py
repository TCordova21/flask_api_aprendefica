from app import ma
from app.models.course_instance_model import CourseInstance
from app.schemas.course_schema import course_schema

class CourseInstanceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CourseInstance
        load_instance = True

    coi_id = ma.auto_field(dump_only=True)
    cou_id = ma.auto_field(required=True)

    coi_name = ma.auto_field(required=True)
    coi_ins_code = ma.auto_field(required=True)

    coi_created_by = ma.auto_field(dump_only=True)

    coi_status = ma.auto_field()
    coi_start_date = ma.auto_field()
    coi_end_date = ma.auto_field()

    created_at = ma.auto_field(dump_only=True)

# Para una sola instancia
course_instance_schema = CourseInstanceSchema()

# Para múltiples instancias
course_instances_schema = CourseInstanceSchema(many=True)


class CourseInstanceWithCourseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CourseInstance
        load_instance = True

    coi_id = ma.auto_field(dump_only=True)

    coi_name = ma.auto_field()
    coi_ins_code = ma.auto_field()

    coi_status = ma.auto_field()
    coi_start_date = ma.auto_field()
    coi_end_date = ma.auto_field()

    created_at = ma.auto_field(dump_only=True)

    # Relación con curso
    course = ma.Nested(course_schema)


course_instance_with_course_schema = CourseInstanceWithCourseSchema()

class CourseInstanceDetailSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CourseInstance
        load_instance = True

    coi_id = ma.auto_field(dump_only=True)
    cou_id = ma.auto_field()
    coi_name = ma.auto_field()
    coi_ins_code = ma.auto_field()
    coi_status = ma.auto_field()
    coi_start_date = ma.auto_field()
    coi_end_date = ma.auto_field()
    # Relación con curso
    course = ma.Nested(course_schema)

course_instance_detail_schema = CourseInstanceDetailSchema()
course_instances_detail_schema = CourseInstanceDetailSchema(many=True)
   