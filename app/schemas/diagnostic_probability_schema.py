from app import ma
from app.models.diagnostic_probability_model import DiagnosticProbability

class DiagnosticProbabilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DiagnosticProbability
        load_instance = True
        include_fk = True

    # Incluimos el nombre del subtema para que el frontend pueda graficar
    sub_name = ma.Function(lambda obj: obj.subtopic.sub_name if obj.subtopic else None)

diagnostic_probability_schema = DiagnosticProbabilitySchema()
diagnostic_probabilities_schema = DiagnosticProbabilitySchema(many=True)