from flask import Blueprint, jsonify, request
from app.models.role_model import Role
from app.schemas.role_schema import roles_schema, role_schema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db

role_bp = Blueprint('role_bp', __name__)


@role_bp.route('/', methods=['GET'])
#@jwt_required()  # Requiere autenticación JWT para acceder a esta ruta
def get_all_roles():

    """
    Obtener todos los roles
    ---
    tags:
      - Roles
    responses:
        200:
            description: Lista de roles
            schema:
            type: array
            items:
                $ref: '#/definitions/Role'
        500:
            description: Error al obtener roles
        """

    try:
        roles = Role.query.all()                   
        result = roles_schema.dump(roles)         
        return jsonify(result), 200              
    except Exception as e:
        return jsonify({'error': f'Error al obtener roles: {str(e)}'}), 500
    


@role_bp.route('/<int:rol_id>', methods=['GET'])
def get_role(rol_id):

    """
    Obtener rol por ID  
    ---
    tags:
      - Roles
    parameters:
      - name: rol_id   
        in: path
        type: integer
        required: true
    responses:
        200:
            description: Rol encontrado
            schema:
                $ref: '#/definitions/Role'
        404:
            description: Rol no encontrado
        500:
            description: Error al obtener rol
    """

    try:
        role = Role.query.get_or_404(rol_id)
        result = role_schema.dump(role)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener rol: {str(e)}'}), 500



@role_bp.route('/', methods=['POST'])
def create_role():

    """
    Crear un nuevo rol
    ---
    tags:
      - Roles
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            rol_name:
              type: string
              description: Nombre del rol
            rol_description:
              type: string
              description: Descripción del rol
    responses:
        201:
            description: Rol creado exitosamente
            schema:
                $ref: '#/definitions/Role'
        500:
            description: Error al crear rol
    """

    try:
        data = request.get_json()
        new_role = Role(**data)  # Unpack the JSON data into the Role model
        db.session.add(new_role)
        db.session.commit()
        result = role_schema.dump(new_role)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': f'Error al crear rol: {str(e)}'}), 500
    


@role_bp.route('/<int:rol_id>', methods=['PUT'])
def update_role(rol_id):

    """
    Actualizar un rol por ID
    ---
    tags:
      - Roles
    parameters:
      - name: rol_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            rol_name:
              type: string
            rol_description:
              type: string
    responses:
        200:
            description: Rol actualizado exitosamente
            schema:
                $ref: '#/definitions/Role'
        404:
            description: Rol no encontrado
        500:
            description: Error al actualizar rol
    """

    try:
        role = Role.query.get_or_404(rol_id)
        data = request.get_json()
        
        # Update role attributes
        for key, value in data.items():
            setattr(role, key, value)
        
        db.session.commit()
        result = role_schema.dump(role)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al actualizar rol: {str(e)}'}), 500
    


@role_bp.route('/<int:rol_id>', methods=['DELETE'])
def delete_role(rol_id):    

    """
    Eliminar un rol por ID
    ---
    tags:
      - Roles
    parameters:
      - name: rol_id
        in: path
        type: integer
        required: true
    responses:
        200:
            description: Rol eliminado exitosamente
        404:
            description: Rol no encontrado
        500:
            description: Error al eliminar rol
    """

    try:
        role = Role.query.get_or_404(rol_id)
        db.session.delete(role)
        db.session.commit()
        return jsonify({'message': 'Rol eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar rol: {str(e)}'}), 500

# This code defines a Flask blueprint for handling role-related routes in a web application.
# It includes routes for getting all roles, getting a specific role by ID, creating a new role,
# updating an existing role, and deleting a role. Each route interacts with a database using SQLAlchemy
# and returns JSON responses. Error handling is included to return appropriate error messages in case of exceptions.