from app import ma
from app.models.audit_model import AuditLog

class AuditLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AuditLog
        include_fk = True
        load_instance = True

    # Para que el frontend reciba el nombre del usuario y no solo el ID
    user_name = ma.Function(lambda obj: f"{obj.user.usr_first_name} {obj.user.usr_last_name}" if obj.user else "Sistema/Manual")

audit_schema = AuditLogSchema()
audits_schema = AuditLogSchema(many=True)