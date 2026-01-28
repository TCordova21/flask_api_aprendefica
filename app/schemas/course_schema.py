from app import ma
from app.models.course_model import Course

class CourseSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Course
        load_instance = True

    cou_id = ma.auto_field(dump_only=True)
    cou_course_name = ma.auto_field()
    cou_description = ma.auto_field()
    cou_difficulty = ma.auto_field()
    cou_visibility = ma.auto_field()
    cou_duration = ma.auto_field()

    cou_status = ma.auto_field()
    cou_created_by = ma.auto_field(dump_only=True)
    cou_thumbnail = ma.auto_field()

    created_at = ma.auto_field(dump_only=True)

# Una sola instancia
course_schema = CourseSchema()

# Lista de instancias
courses_schema = CourseSchema(many=True)


