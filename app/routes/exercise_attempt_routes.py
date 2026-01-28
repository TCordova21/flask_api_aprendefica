from flask import Blueprint, request, jsonify
from app import db
from app.models.exercise_attempt_model import ExerciseAttempt
from app.schemas.exercise_attempt_schema import exercise_attempt_schema

attempt_exercise_bp = Blueprint('attempt_exercise_bp', __name__, url_prefix='/api/exercise-attempts')

@attempt_exercise_bp.route('/', methods=['POST'])
def save_attempt():
    """
    Registrar un intento de ejercicio
    ---
    tags:
      - Estudiante - Intentos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - ex_id
            - enr_id
            - exa_answer
            - exa_is_correct
          properties:
            ex_id:
              type: integer
              example: 29
            enr_id:
              type: integer
              example: 10
            exa_answer:
              type: string
              example: "2"
            exa_is_correct:
              type: boolean
              example: true
    responses:
      201:
        description: Intento registrado con éxito
      400:
        description: Datos inválidos
      500:
        description: Error interno del servidor
    """
    data = request.get_json()
    
    ex_id = data.get('ex_id')
    enr_id = data.get('enr_id')

    if not ex_id or not enr_id:
        return jsonify({'error': 'ex_id y enr_id son obligatorios'}), 400

    # Lógica de autoincremento para el número de intento
    last_attempt_no = db.session.query(db.func.max(ExerciseAttempt.exa_attempt_no))\
        .filter_by(ex_id=ex_id, enr_id=enr_id).scalar()
    
    # Si no hay intentos previos, el escalar devuelve None
    data['exa_attempt_no'] = (last_attempt_no + 1) if last_attempt_no else 1

    try:
        # Usamos el esquema para cargar/validar o directamente el modelo como en tus ejemplos
        attempt = ExerciseAttempt(**data)
        db.session.add(attempt)
        db.session.commit()
        
        return exercise_attempt_schema.jsonify(attempt), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500