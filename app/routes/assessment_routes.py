from flask import Blueprint, request, jsonify
from app import db
from app.models.assessment_model import Assessment
from app.schemas.assessment_schema import assessment_schema, assessments_schema, assessment_basic_schema, assessments_basic_schema


assessment_bp = Blueprint('assessment_bp', __name__, url_prefix='/api/assessments')
@assessment_bp.route('/', methods=['POST'])
def create_assessment():
    """
    Crear una nueva evaluación
    ---
    tags:
      - Currículo - Evaluaciones
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cou_id
            - asm_title
            - asm_type
            - asm_status
            - asm_created_by
          properties:
            cou_id:
              type: integer
              example: 1
            asm_title:
              type: string
              example: Evaluación de Matemáticas Básicas
            asm_description:
              type: string
              example: Esta evaluación cubre los conceptos básicos de matemáticas.
            asm_type:
              type: string
              example: quiz
            asm_status:
              type: string
              example: draft
            created_by:
              type: integer
              example: 2
    responses:
      201:
        description: Evaluación creada
      500:
        description: Error interno
    """
    data = request.get_json()

    assessment = Assessment(**data)
    db.session.add(assessment)
    db.session.commit()

    return assessment_schema.jsonify(assessment), 201

@assessment_bp.route('/', methods=['GET'])  
def get_all_assessments():
    """
    Obtener todas las evaluaciones registradas en el sistema
    ---
    tags:
      - Currículo - Evaluaciones
    responses:
        200:
            description: Lista de todas las evaluaciones
            schema:
            type: array
            items:
                $ref: '#/definitions/Assessment'
        500:
            description: Error al obtener evaluaciones
            schema:
            type: object
            properties:
                error:
                type: string
                example: Error al obtener evaluaciones
        """
    try:
        assessments = Assessment.query.all()
        return assessments_schema.jsonify(assessments), 200
    except Exception as e:
        return jsonify({
            'error': f'Error al obtener evaluaciones: {str(e)}'
        }), 500
    
@assessment_bp.route('/basic', methods=['GET'])  
def get_all_assessments_basic():
    """
    Obtener todas las evaluaciones registradas en el sistema (campos básicos)
    ---
    tags:
      - Currículo - Evaluaciones
    responses:
        200:
            description: Lista de todas las evaluaciones (campos básicos)
            schema:
            type: array
            items:
                $ref: '#/definitions/AssessmentBasic'
        500:
            description: Error al obtener evaluaciones
            schema:
            type: object
            properties:
                error:
                type: string
                example: Error al obtener evaluaciones
        """
    try:
        assessments = Assessment.query.all()
        return assessments_basic_schema.jsonify(assessments), 200
    except Exception as e:
        return jsonify({
            'error': f'Error al obtener evaluaciones: {str(e)}'
        }), 500
    
@assessment_bp.route('/<int:asm_id>', methods=['GET'])
def get_assessment(asm_id):
    """
    Obtener una evaluación por ID
    ---
    tags:
      - Currículo - Evaluaciones    
    parameters:
      - name: asm_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Evaluación encontrada
      404:
        description: Evaluación no encontrada
    """
    assessment = Assessment.query.get_or_404(asm_id)
    return assessment_schema.jsonify(assessment), 200


@assessment_bp.route('/course/<int:course_id>', methods=['GET'])

def get_assessments_by_course(course_id):
    """
    Obtener evaluaciones por ID de curso
    ---
    tags:
      - Currículo - Evaluaciones
    parameters:
      - name: course_id
        in: path
        type: integer
        required: true
        description: ID del curso para filtrar las evaluaciones
    responses:
      200:
        description: Lista de evaluaciones encontrada
        schema:
          type: array
          items:
            $ref: '#/definitions/Assessment'
      404:
        description: No se encontraron evaluaciones para este curso
      500:
        description: Error interno del servidor
    """
    try:
        assessments = Assessment.query.filter_by(cou_id=course_id).all()
        # Marshmallow se encarga de convertir la lista de objetos a JSON
        return jsonify(assessments_schema.dump(assessments)), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


