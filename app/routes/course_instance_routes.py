from flask import Blueprint, request, jsonify
from app import db
from app.models.course_instance_model import CourseInstance
from app.schemas.course_instance_schema import course_instance_schema, course_instances_schema, course_instances_detail_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

course_instance_bp = Blueprint('course_instance_bp', __name__)


@course_instance_bp.route('/', methods=['GET'])
def get_all_course_instances():
    """
    Obtener todas las instancias de cursos
    ---
    tags:
      - Instancias de Cursos
    responses:
      200:
        description: Lista de instancias
        schema:
          type: array
          items:
            $ref: '#/definitions/CourseInstance'
    """
    instances = CourseInstance.query.all()
    return course_instances_schema.jsonify(instances), 200



@course_instance_bp.route('/<int:coi_id>', methods=['GET'])
def get_course_instance(coi_id):
    """
    Obtener una instancia de curso por ID
    ---
    tags:
      - Instancias de Cursos
    parameters:
      - in: path
        name: coi_id
        type: integer
        required: true
    responses:
      200:
        schema:
          $ref: '#/definitions/CourseInstance'
      404:
        description: Instancia no encontrada
    """
    instance = CourseInstance.query.get_or_404(coi_id)
    return course_instance_schema.jsonify(instance), 200

@course_instance_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_course_instances():
    """
    Obtener instancias creadas por el docente autenticado
    ---
    tags:
      - Instancias de Cursos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de instancias
    """
    user_id = get_jwt_identity()
    instances = CourseInstance.query.filter_by(coi_created_by=user_id).all()
    return course_instances_schema.jsonify(instances), 200

@course_instance_bp.route('/my/detail', methods=['GET'])
@jwt_required()
def get_my_course_instances_detail():
    """
    Obtener detalles de instancias creadas por el docente autenticado
    ---
    tags:
      - Instancias de Cursos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de instancias con detalles
    """
    user_id = get_jwt_identity()
    instances = CourseInstance.query.filter_by(coi_created_by=user_id).all()
    return course_instances_detail_schema.jsonify(instances), 200

@course_instance_bp.route('/', methods=['POST'])
@jwt_required()
def create_course_instance():
    """
    Crear una nueva instancia de curso
    ---
    tags:
      - Instancias de Cursos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cou_id
            - coi_name
            - coi_isn_code
            - coi_start_date
          properties:
            cou_id:
              type: integer
            coi_name:
              type: string
            coi_code:
              type: string
            coi_start_date:
              type: string
              format: date
            coi_end_date:
              type: string
              format: date
    responses:
      201:
        description: Instancia creada
        schema:
          $ref: '#/definitions/CourseInstance'
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    instance = CourseInstance(
        cou_id=data['cou_id'],
        coi_name=data['coi_name'],
        coi_ins_code=data['coi_ins_code'],
        coi_start_date=data['coi_start_date'],
        coi_end_date=data.get('coi_end_date'),
        coi_created_by=user_id
    )

    db.session.add(instance)
    db.session.commit()

    return course_instance_schema.jsonify(instance), 201

@course_instance_bp.route('/<int:coi_id>', methods=['PATCH'])
@jwt_required()
def update_course_instance(coi_id):
    """
    Actualizar una instancia de curso
    ---
    tags:
      - Instancias de Cursos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coi_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            coi_name:
              type: string
            coi_status:
              type: string
            coi_start_date:
              type: string
              format: date
            coi_finish_date:
              type: string
              format: date
    responses:
      200:
        description: Instancia actualizada
    """
    instance = CourseInstance.query.get_or_404(coi_id)
    data = request.get_json()

    for field in ['coi_name', 'coi_status', 'coi_start_date', 'coi_finish_date']:
        if field in data:
            setattr(instance, field, data[field])

    db.session.commit()
    return course_instance_schema.jsonify(instance), 200



@course_instance_bp.route('/<int:coi_id>', methods=['DELETE'])
@jwt_required()
def delete_course_instance(coi_id):
    """
    Eliminar una instancia de curso
    ---
    tags:
      - Instancias de Cursos
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coi_id
        type: integer
        required: true
    responses:
      200:
        description: Instancia eliminada
    """
    instance = CourseInstance.query.get_or_404(coi_id)
    db.session.delete(instance)
    db.session.commit()

    return jsonify({'message': 'Instancia eliminada correctamente'}), 200

