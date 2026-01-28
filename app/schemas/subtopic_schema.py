from app import ma
from app.models.subtopic_model import Subtopic
from marshmallow import fields

class SubtopicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Subtopic
        load_instance = True

    sub_id = fields.Int(dump_only=True)
    dom_id = fields.Int(required=True)
    sub_name = fields.Str(required=True)
    sub_description = fields.Str()

    prerequisites = fields.Method("get_prerequisites")

    def get_prerequisites(self, obj):
        return [p.sub_id for p in obj.prerequisites]



subtopic_schema = SubtopicSchema()
subtopics_schema = SubtopicSchema(many=True)


class SubtopicDetailSchema(SubtopicSchema):
    prerequisites = ma.Nested(SubtopicSchema, many=True)

subtopic_detail_schema = SubtopicDetailSchema()
subtopics_detail_schema = SubtopicDetailSchema(many=True)
