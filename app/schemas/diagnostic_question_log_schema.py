from app import ma
from app.models.diagnostic_question_log_model import DiagnosticQuestionLog

class DiagnosticQuestionLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DiagnosticQuestionLog
        load_instance = True
        include_fk = True

diagnostic_question_log_schema = DiagnosticQuestionLogSchema()
diagnostic_question_logs_schema = DiagnosticQuestionLogSchema(many=True)