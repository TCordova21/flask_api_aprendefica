from app import ma
from app.models.student_domain_model import StudentDomainProgress

class StudentDomainProgressSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StudentDomainProgress
        include_fk = True
        load_instance = True

    dom_name = ma.Function(lambda obj: obj.domain.dom_name if obj.domain else None)

sdp_schema = StudentDomainProgressSchema()
sdp_list_schema = StudentDomainProgressSchema(many=True)