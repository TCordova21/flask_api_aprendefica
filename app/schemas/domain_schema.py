from app import ma
from app.models.domain_model import Domain

class DomainSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Domain

    dom_id = ma.auto_field()
    cou_id = ma.auto_field()
    dom_name = ma.auto_field()
    dom_description = ma.auto_field()
    dom_created_at = ma.auto_field()

domain_schema = DomainSchema()
domains_schema = DomainSchema(many=True)
