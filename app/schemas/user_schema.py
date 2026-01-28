from app import ma
from app.models.user_model import User
from marshmallow import fields, validate

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        ordered = True

    usr_id = ma.auto_field(dump_only=True)
    usr_first_name = ma.auto_field()
    usr_last_name = ma.auto_field()
    usr_email = ma.auto_field()
    rol_id = ma.auto_field()
    usr_status = fields.String(
        validate=validate.OneOf(['activo', 'inactivo', 'pendiente']),
        dump_only=True
    )

    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserCreateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    usr_first_name = ma.auto_field(required=True)
    usr_last_name = ma.auto_field(required=True)
    usr_email = ma.auto_field(required=True)
    usr_password = fields.String(required=True, load_only=True)
    rol_id = ma.auto_field(required=True)


user_create_schema = UserCreateSchema()
