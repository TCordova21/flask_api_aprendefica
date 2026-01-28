from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.learning_resource_model import LearningResource
from app.schemas.learning_resource_schema import (
    learning_resource_schema,
    learning_resources_schema
)

learning_resource_bp = Blueprint('learning_resource_bp', __name__)

@learning_resource_bp.route('/', methods=['POST'])
#@jwt_required()
def create_learning_resource():
    """
    Crear recurso de aprendizaje para un subtema
    ---
    tags:
      - Recursos de Aprendizaje
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - sub_id
            - lrn_title
            - lrn_type
          properties:
            sub_id:
              type: integer
              example: 5
            lrn_title:
              type: string
              example: Introducción a la multiplicación
            lrn_description:
              type: string
            lrn_type:
              type: string
              enum: [video, documento, pdf, link, explicacion]
            lrn_url:
              type: string
              example: https://youtube.com/...
            lrn_content:
              type: string
              example: "<p>Contenido HTML</p>"
            lrn_order:
              type: integer
              example: 1
    responses:
      201:
        description: Recurso creado
      400:
        description: Datos inválidos
      500:
        description: Error interno
    """

    data = request.get_json()
    resource = LearningResource(**data)

    db.session.add(resource)
    db.session.commit()

    return learning_resource_schema.jsonify(resource), 201


@learning_resource_bp.route('/by-subtopic/<int:sub_id>', methods=['GET'])
#@jwt_required()
def get_resources_by_subtopic(sub_id):
    """
    Obtener recursos de un subtema
    ---
    tags:
      - Recursos de Aprendizaje
    security:
      - Bearer: []
    parameters:
      - name: sub_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de recursos
    """

    resources = LearningResource.query.filter_by(
        sub_id=sub_id,
        lrn_status='activo'
    ).order_by(LearningResource.lrn_order).all()

    return learning_resources_schema.jsonify(resources), 200


@learning_resource_bp.route('/<int:lrn_id>', methods=['PUT'])
#@jwt_required()
def update_learning_resource(lrn_id):
    """
    Actualizar recurso de aprendizaje
    ---
    tags:
      - Recursos de Aprendizaje
    security:
      - Bearer: []
    parameters:
      - name: lrn_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: Recurso actualizado
      404:
        description: No encontrado
    """

    resource = LearningResource.query.get_or_404(lrn_id)
    data = request.get_json()

    for key, value in data.items():
        setattr(resource, key, value)

    db.session.commit()

    return learning_resource_schema.jsonify(resource), 200


@learning_resource_bp.route('/<int:lrn_id>', methods=['DELETE'])
#@jwt_required()
def delete_learning_resource(lrn_id):
    """
    Eliminar recurso de aprendizaje
    ---
    tags:
      - Recursos de Aprendizaje
    security:
      - Bearer: []
    parameters:
      - name: lrn_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Recurso eliminado
    """

    resource = LearningResource.query.get_or_404(lrn_id)
    db.session.delete(resource)
    db.session.commit()

    return jsonify({'message': 'Recurso eliminado correctamente'}), 200
