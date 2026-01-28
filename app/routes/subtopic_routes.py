from flask import Blueprint, request, jsonify
from app import db
from app.models.subtopic_model import Subtopic
from app.schemas.subtopic_schema import subtopic_schema, subtopics_schema, subtopic_detail_schema, subtopics_detail_schema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import RaiseException
from flask import jsonify
from sqlalchemy.exc import DBAPIError




subtopic_bp = Blueprint("subtopic_bp", __name__, url_prefix="/api/subtopics")

@subtopic_bp.route("/domain/<int:dom_id>", methods=["GET"])
def get_subtopics_by_domain(dom_id):

    """
    Obtener subtemas por dominio
    ---
    tags:
      - Currículo - Subtemas
    parameters:
      - name: dom_id
        in: path
        type: integer
        required: true
        description: ID del dominio
    responses:
      200:
        description: Lista de subtemas
        schema:
          type: array
          items:
            $ref: '#/definitions/Subtopic'
      404:
        description: Dominio sin subtemas
      500:
        description: Error interno
    """

    subtopics = Subtopic.query.filter_by(dom_id=dom_id).all()
    return subtopics_schema.jsonify(subtopics), 200

@subtopic_bp.route("/<int:sub_id>", methods=["GET"])
def get_subtopic(sub_id):
    """
    Obtener un subtema por ID
    ---
    tags:
      - Currículo - Subtemas
    parameters:
      - name: sub_id
        in: path
        type: integer
        required: true
    responses:
        200:
            description: Subtema encontrado
            schema:
            $ref: '#/definitions/Subtopic'
        404:
            description: Subtema no encontrado
        500:
            description: Error al obtener subtema
        """

    subtopic = Subtopic.query.get_or_404(sub_id)
    return subtopic_schema.jsonify(subtopic), 200

@subtopic_bp.route("/", methods=["POST"])
#@jwt_required()
def create_subtopic():
    """
    Crear subtema (prerrequisitos opcionales)
    ---
    tags:
      - Currículo - Subtemas
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - dom_id
            - sub_name
          properties:
            dom_id:
              type: integer
            sub_name:
              type: string
            sub_description:
              type: string
            prerequisites:
              type: array
              items:
                type: integer
    responses:
      201:
        description: Subtema creado exitosamente
        schema:
          $ref: '#/definitions/Subtopic'
      400:
        description: Datos inválidos
      409:
        description: Subtema duplicado
      500:
        description: Error interno
    """

    data = request.get_json()
    prerequisites_ids = data.pop("prerequisites", [])

    subtopic = Subtopic(**data)

    if prerequisites_ids:
        subtopic.prerequisites = Subtopic.query.filter(
            Subtopic.sub_id.in_(prerequisites_ids)
        ).all()

    db.session.add(subtopic)
    db.session.commit()

    return subtopic_schema.jsonify(subtopic), 201




@subtopic_bp.route('/<int:sub_id>', methods=['PUT'])
def update_subtopic(sub_id):

    subtopic = Subtopic.query.get_or_404(sub_id)
    data = request.get_json()

    try:
        subtopic.sub_name = data.get('sub_name', subtopic.sub_name)
        subtopic.sub_description = data.get(
            'sub_description',
            subtopic.sub_description
        )

        if 'prerequisites' in data:
            new_ids = data['prerequisites']
            new_prerequisites = Subtopic.query.filter(
                Subtopic.sub_id.in_(new_ids)
            ).all()
            subtopic.prerequisites = new_prerequisites

        db.session.commit()

        return subtopic_schema.jsonify(subtopic), 200

    except DBAPIError as e:
        db.session.rollback()

       
        message = (
            getattr(e.orig, "diag", None)
            and e.orig.diag.message_primary
        ) or str(e.orig)

        return jsonify({
            "error": message
        }), 400



@subtopic_bp.route('/<int:sub_id>/dependencies', methods=['PUT'])
#@jwt_required()
def update_subtopic_dependencies(sub_id):
    """
    Actualizar prerrequisitos de un subtema (KST)
    ---
    tags:
      - Currículo - Subtemas
    security:
      - Bearer: []
    parameters:
      - name: sub_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - prerequisites
          properties:
            prerequisites:
              type: array
              items:
                type: integer
              example: [2, 3]
    responses:
      200:
        description: Dependencias actualizadas
      400:
        description: Datos inválidos
      404:
        description: Subtema no encontrado
    """

    data = request.get_json()
    prerequisites_ids = data.get('prerequisites')

    if prerequisites_ids is None:
        return jsonify({'error': 'prerequisites es obligatorio'}), 400

    subtopic = Subtopic.query.get_or_404(sub_id)

    prerequisites = Subtopic.query.filter(
        Subtopic.sub_id.in_(prerequisites_ids)
    ).all()

    subtopic.prerequisites = prerequisites
    db.session.commit()

    return subtopic_schema.jsonify(subtopic), 200


