from app import ma
from app.models.diagnostic_session_model import DiagnosticSession

class DiagnosticSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DiagnosticSession
        load_instance = True
        include_fk = True # Para ver los IDs de las llaves foráneas

    # Campos que solo se envían al cliente (dump_only)
    session_id = ma.auto_field(dump_only=True)
    started_at = ma.auto_field(dump_only=True)

diagnostic_session_schema = DiagnosticSessionSchema()
diagnostic_sessions_schema = DiagnosticSessionSchema(many=True)

