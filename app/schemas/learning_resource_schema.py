from app import ma
from app.models.learning_resource_model import LearningResource

class LearningResourceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = LearningResource
        load_instance = True

    lrn_id = ma.auto_field(dump_only=True)
    sub_id = ma.auto_field(required=True)

    lrn_title = ma.auto_field(required=True)
    lrn_description = ma.auto_field()

    lrn_type = ma.auto_field(required=True)
    lrn_url = ma.auto_field()
    lrn_content = ma.auto_field()

    lrn_order = ma.auto_field()
    lrn_status = ma.auto_field()

    created_at = ma.auto_field(dump_only=True)


learning_resource_schema = LearningResourceSchema()
learning_resources_schema = LearningResourceSchema(many=True)
