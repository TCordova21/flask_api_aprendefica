from flask import Blueprint, request, jsonify
from app import db
from app.models.assessment_exercise_model import AssessmentExercise
from app.models.course_instance_model import CourseInstance
from app.models.assessment_model import Assessment
from app.schemas.assessment_exercise_schema import (
    assessment_exercise_schema, 
    assessment_exercises_schema,
    assessment_exercises_detail_schema,
    assessment_exercises_detail_by_course_schema

)
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

assessment_exercise_bp = Blueprint('assessment_exercise_bp', __name__)

@assessment_exercise_bp.route('/assessment/<int:asm_id>', methods=['GET'])
#@jwt_required()
def get_exercises_by_assessment(asm_id):
    """
    Obtener ejercicios de una evaluación específica
    ---
    tags:
      - Evaluación - Ejercicios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: asm_id
        type: integer
        required: true
        description: ID de la evaluación
    responses:
      200:
        description: Lista de ejercicios asociados a la evaluación
        schema:
          type: array
          items:
            $ref: '#/definitions/AssessmentExercise'
    """
    exercises = AssessmentExercise.query.filter_by(asm_id=asm_id).order_by(AssessmentExercise.ase_order_index).all()
    return assessment_exercises_detail_schema.jsonify(exercises), 200



@assessment_exercise_bp.route('/', methods=['POST'])
#@jwt_required()
def add_exercise_to_assessment():
    """
    Asignar un ejercicio a una evaluación
    ---
    tags:
      - Evaluación - Ejercicios
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - asm_id
            - ex_id
          properties:
            asm_id:
              type: integer
              description: ID de la evaluación
            ex_id:
              type: integer
              description: ID del ejercicio
            ase_order_index:
              type: integer
              default: 1
              description: Posición del ejercicio en la evaluación
    responses:
      201:
        description: Ejercicio asignado correctamente
      409:
        description: Conflicto - El ejercicio ya existe en esta evaluación o el índice de orden está ocupado
      400:
        description: Error en la solicitud
    """
    data = request.get_json()
    
    try:
        new_relation = AssessmentExercise(
            asm_id=data['asm_id'],
            ex_id=data['ex_id'],
            ase_order_index=data.get('ase_order_index', 1)
        )
        db.session.add(new_relation)
        db.session.commit()
        return assessment_exercise_schema.jsonify(new_relation), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'El ejercicio ya está en la evaluación o el orden ya está tomado'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@assessment_exercise_bp.route('/<int:ase_id>', methods=['DELETE'])
@jwt_required()
def remove_exercise(ase_id):
    """
    Eliminar la relación entre un ejercicio y una evaluación
    ---
    tags:
      - Evaluación - Ejercicios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: ase_id
        type: integer
        required: true
        description: ID de la relación (ase_id)
    responses:
      200:
        description: Relación eliminada correctamente
      404:
        description: No se encontró la relación
    """
    relation = AssessmentExercise.query.get_or_404(ase_id)
    db.session.delete(relation)
    db.session.commit()
    return jsonify({'message': 'Ejercicio quitado de la evaluación correctamente'}), 200

@assessment_exercise_bp.route('/instance/<int:coi_id>/diagnostic', methods=['GET'])
# @jwt_required()  # Descomenta si necesitas seguridad
def get_diagnostic_exercises_by_instance(coi_id):
    """
    Obtener ejercicios de evaluación tipo DIAGNÓSTICO por instancia de curso
    ---
    tags:
      - Evaluación - Ejercicios
    security:
      - Bearer: []
    parameters:
      - in: path
        name: coi_id
        type: integer
        required: true
        description: ID de la instancia del curso
    responses:
      200:
        description: Lista de ejercicios de diagnóstico encontrados
        schema:
          type: array
          items:
            $ref: '#/definitions/AssessmentExerciseDetailByCourse'
      404:
        description: Instancia no encontrada
    """
    # 1. Buscamos la instancia para obtener el cou_id
    instance = CourseInstance.query.get_or_404(coi_id)
    
    # 2. Consultamos AssessmentExercise unido a Assessment
    # Filtramos por el curso de la instancia Y que el tipo sea 'diagnostico'
    exercises = db.session.query(AssessmentExercise)\
        .join(Assessment, AssessmentExercise.asm_id == Assessment.asm_id)\
        .filter(
            Assessment.cou_id == instance.cou_id,
            Assessment.asm_type == 'diagnostico'
        )\
        .order_by(AssessmentExercise.ase_order_index)\
        .all()

    return assessment_exercises_detail_by_course_schema.jsonify(exercises), 200


@assessment_exercise_bp.route('/remove/<int:asm_id>/<int:ex_id>', methods=['DELETE'])
def remove_exercise_from_assessment(asm_id, ex_id):
    """
    Desvincular un ejercicio de una evaluación
    ---
    tags:
       - Evaluación - Ejercicios
    parameters:
      - name: asm_id
        in: path
        type: integer
        required: true
        description: ID de la evaluación
      - name: ex_id
        in: path
        type: integer
        required: true
        description: ID del ejercicio a eliminar
    responses:
      200:
        description: Ejercicio desvinculado exitosamente
        schema:
          type: object
          properties:
            message:
              type: string
              example: Relación eliminada
      404:
        description: No se encontró la relación entre la evaluación y el ejercicio
      500:
        description: Error interno del servidor
    """
    try:
        # Buscamos la relación en la tabla intermedia
        rel = AssessmentExercise.query.filter_by(asm_id=asm_id, ex_id=ex_id).first()
        
        if rel:
            db.session.delete(rel)
            db.session.commit()
            return jsonify({"message": "Relación eliminada"}), 200
            
        return jsonify({"error": "No encontrado"}), 404

    except Exception as e:
        db.session.rollback() # Siempre es bueno hacer rollback si falla
        return jsonify({"error": str(e)}), 500