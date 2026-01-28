from app import ma
from app.models.role_model import Role

class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Role
        load_instance = True

    rol_id = ma.auto_field()
    rol_name = ma.auto_field()
    rol_description = ma.auto_field()
    created_at = ma.auto_field()

# 👉 Aquí instancias los esquemas para usarlos en tus rutas
roles_schema = RoleSchema(many=True)
role_schema = RoleSchema()