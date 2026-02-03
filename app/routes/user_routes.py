from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.models.user_model import User
from app.schemas.user_schema import users_schema, user_schema, user_create_schema  
from app import db
from app import bcrypt 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

user_bp = Blueprint('user_bp', __name__)




@user_bp.route('/', methods=['GET'])
@jwt_required()  
def get_all_users():

    """
    Obtener todos los usuarios
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de usuarios
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
      401:
        description: Token inválido o no enviado
      500:
        description: Error al obtener usuarios
    """

    try:
        users = User.query.all()                   
        result = users_schema.dump(users)         
        return jsonify(result), 200              
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuarios: {str(e)}'}), 500



@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):

    """
    Obtener todos los usuarios por ID   
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - name: user_id   
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuario encontrado
        schema:
          $ref: '#/definitions/User'
      404:
        description: Usuario no encontrado
      500:
        description: Error al obtener usuario
    """
    try:
        user = User.query.get_or_404(user_id)
        result = user_schema.dump(user)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuario: {str(e)}'}), 500
    

@user_bp.route('/', methods=['POST'])
#@jwt_required()
def create_user():
    """
    Crear un nuevo usuario
    ---
    tags:
      - Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            usr_first_name:
              type: string
            usr_last_name:
              type: string
            usr_email:
              type: string
            usr_password:
              type: string
            rol_id:
              type: integer
    responses:
      201:
        description: Usuario creado exitosamente
    """


    try:
        data = request.get_json()
        user_data = user_create_schema.load(data)
        email_lower = user_data.usr_email.lower()
        if User.query.filter(func.lower(User.usr_email) == email_lower).first():
            return jsonify({'error': 'El correo ya está registrado'}), 400

        hashed_password = bcrypt.generate_password_hash(
            user_data.usr_password
        ).decode('utf-8')

        new_user = User(
            usr_first_name=user_data.usr_first_name,
            usr_last_name=user_data.usr_last_name,
            usr_email=user_data.usr_email,
            usr_password=hashed_password,
            rol_id=user_data.rol_id
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(user_schema.dump(new_user)), 201

    except Exception as e:
        db.session.rollback()
        if "UniqueViolation" in str(e) or "already exists" in str(e):
            return jsonify({'error': 'El correo ya está registrado'}), 400
            
        return jsonify({'error': 'Error interno del servidor'}), 500

from app import bcrypt

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):

    """
    Actualizar un usuario por ID
    ---
    tags:
      - Usuarios
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            usr_name:
              type: string
            usr_lastname:
              type: string
            usr_email:
              type: string
            usr_password:
              type: string
            rol_id:
              type: integer
    security:
      - Bearer: []
    responses:
      200:
        description: Usuario actualizado exitosamente
      404:
        description: Usuario no encontrado
      500:
        description: Error al actualizar usuario
    """

    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # Campos permitidos
        allowed_fields = ['usr_name', 'usr_lastname', 'usr_email', 'usr_password', 'rol_id']

        for key in allowed_fields:
            if key in data:
                if key == 'usr_password':
                    hashed = bcrypt.generate_password_hash(data[key]).decode('utf-8')
                    setattr(user, key, hashed)
                else:
                    setattr(user, key, data[key])

        db.session.commit()
        return jsonify(user_schema.dump(user)), 200

    except Exception as e:
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):

    """
    Eliminar un usuario por ID
    ---
    tags:
      - Usuarios
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Usuario eliminado exitosamente
      404:
        description: Usuario no encontrado
      500:
        description: Error al eliminar usuario
    """

    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuario con id {user_id} eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar usuario: {str(e)}'}), 500
    
   
@user_bp.route('/login', methods=['POST'])
def login():
    """
    Iniciar sesión de usuario
    ---
    tags:
      - Autenticación
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            usr_email:
              type: string
              example: "tito@example.com"
            usr_password:
              type: string
              example: "P455WPORD?"
    responses:
      200:
        description: Token generado correctamente
        schema:
          type: object
          properties:
            access_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                lastname:
                  type: string
                email:
                  type: string
                rol_id:
                  type: integer
      401:
        description: Credenciales inválidas
      500:
        description: Error interno del servidor
    """
    try:
        data = request.get_json()
        email = data.get('usr_email')
        password = data.get('usr_password')

        if not email or not password:
            return jsonify({'error': 'Correo y contraseña son requeridos'}), 400

        user = User.query.filter_by(usr_email=email).first()

        if not user:
            return jsonify({'error': 'El correo no se encuentra registrado'}), 401
        
        if not bcrypt.check_password_hash(user.usr_password, password):
            return jsonify({'error': 'La contraseña es incorrecta'}), 401

        access_token = create_access_token(
            identity=str(user.usr_id),
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.usr_id,
                'name': user.usr_first_name,
                'lastname': user.usr_last_name,
                'email': user.usr_email,
                'rol_id': user.rol_id
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error en el login: {str(e)}'}), 500
    

    # Rutas para manejar el perfil del usuario
    # Estas rutas permiten obtener y actualizar el perfil del usuario autenticado

@user_bp.route('/profile', methods=['GET'])
#@jwt_required()
def get_profile():

    """
    Obtener perfil del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Datos del usuario autenticado
        schema:
          $ref: '#/definitions/User'
      401:
        description: Token inválido o no enviado
      500:
        description: Error al obtener perfil
    """

    try:
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener perfil: {str(e)}'}), 500
