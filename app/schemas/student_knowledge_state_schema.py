from app import ma
from app.models.student_knowledge_state_model import StudentKnowledgeState


class StudentKnowledgeStateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StudentKnowledgeState
        include_fk = True
        load_instance = True

    # Campo anidado opcional para ver detalles del subtema
    sub_name = ma.Function(lambda obj: obj.subtopic.sub_name if obj.subtopic else None)



# Instancias para uso en rutas
sks_schema = StudentKnowledgeStateSchema()
sks_list_schema = StudentKnowledgeStateSchema(many=True)
