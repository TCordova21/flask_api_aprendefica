# app/routes/exercise_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.exercise_model import Exercise
from app.schemas.exercise_schema import exercise_schema, exercises_schema

exercise_bp = Blueprint('exercise_bp', __name__, url_prefix='/api/exercises')

@exercise_bp.route('/', methods=['POST'])
def create_exercise():
    """
    Crear ejercicio interactivo
    ---
    tags:
      - Currículo - Ejercicios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - sub_id
            - ex_statement
            - ex_expected_answer
          properties:
            sub_id:
              type: integer
              example: 3
            ex_statement:
              type: string
              example: ¿Cuánto es 5 × 4?
            ex_expression:
              type: string
              example: 5*4
            ex_instruction:
              type: string
              example: Multiplica los números
            ex_expected_answer:
              type: string
              example: "20"
            ex_difficulty:
              type: integer
              example: 2
    responses:
      201:
        description: Ejercicio creado
      409:
        description: Orden duplicado
      500:
        description: Error interno
    """
    data = request.get_json()

    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()

    return exercise_schema.jsonify(exercise), 201

@exercise_bp.route('/by-subtopic/<int:sub_id>', methods=['GET'])
def get_exercises_by_subtopic(sub_id):
    """
    Obtener ejercicios por subtema
    ---
    tags:
      - Currículo - Ejercicios
    parameters:
      - name: sub_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de ejercicios
    """
    exercises = Exercise.query.filter_by(
        sub_id=sub_id,
        ex_is_active=True
    ).order_by(Exercise.ex_id).all()

    return exercises_schema.jsonify(exercises), 200

@exercise_bp.route('/<int:ex_id>', methods=['PUT'])
def update_exercise(ex_id):
    """
    Actualizar ejercicio
    ---
    tags:
      - Currículo - Ejercicios
    """
    exercise = Exercise.query.get_or_404(ex_id)
    data = request.get_json()

    for key, value in data.items():
        setattr(exercise, key, value)

    db.session.commit()
    return exercise_schema.jsonify(exercise), 200

@exercise_bp.route('/<int:ex_id>/disable', methods=['PATCH'])
def disable_exercise(ex_id):
    """
    Desactivar ejercicio
    ---
    tags:
      - Currículo - Ejercicios
    """
    exercise = Exercise.query.get_or_404(ex_id)
    exercise.ex_is_active = False
    db.session.commit()

    return jsonify({'message': 'Ejercicio desactivado'}), 200
