from flask import Blueprint, request, jsonify
from app import db
from app.models.course_model import Course
from app.schemas.course_schema import course_schema, courses_schema
from flask_jwt_extended import jwt_required, get_jwt_identity


course_bp = Blueprint('course_bp', __name__)

@course_bp.route('/', methods=['GET'])
def get_all_courses():
    """
    Obtener todos los cursos
    ---
    tags:
      - Cursos
    responses:
      200:
        description: Lista de cursos
        schema:
          type: array
          items:
            $ref: '#/definitions/Course'
      500:
        description: Error al obtener cursos
    """
    try:
        courses = Course.query.all()
        result = courses_schema.dump(courses)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener los cursos: {str(e)}'}), 500

@course_bp.route('/published', methods=['GET'])
def get_published_courses():
    """
    Obtener todos los cursos con estado 'publicado'
    ---
    tags:
      - Cursos
    responses:
      200:
        description: Lista de cursos disponibles para el público
        schema:
          type: array
          items:
            $ref: '#/definitions/Course'
      500:
        description: Error al filtrar los cursos
    """
    try:
        # Filtramos directamente en la consulta a la base de datos
        published_courses = Course.query.filter_by(cou_status='publicado').all()
        
        # Serializamos los resultados
        result = courses_schema.dump(published_courses)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'error': 'Error al obtener los cursos publicados',
            'details': str(e)
        }), 500

@course_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """
    Obtener un curso por ID
    ---
    tags:
      - Cursos
    parameters:
      - name: course_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Curso encontrado
        schema:
          $ref: '#/definitions/Course'
      404:
        description: Curso no encontrado
      500:
        description: Error al obtener curso
    """
    try:
        course = Course.query.get_or_404(course_id)
        result = course_schema.dump(course)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener el curso: {str(e)}'}), 500


@course_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    """
    Crear un nuevo curso
    ---
    tags:
      - Cursos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cou_course_name
            - cou_description
          properties:
            cou_course_name:
              type: string
              description: Nombre del curso
            cou_description:
              type: string
              description: Descripción del curso
            cou_duration:
              type: integer
              description: Duración del curso (en horas)
            cou_difficulty:
              type: string
              description: Nombre del curso
            cou_visibility:
              type: string
              description: Nombre del curso
    responses:
      201:
        description: Curso creado exitosamente
        schema:
          $ref: '#/definitions/Course'
      500:
        description: Error al crear curso
    """
    try:
        data = request.get_json()

        user_id = get_jwt_identity()

        new_course = Course(
            cou_course_name=data.get('cou_course_name'),
            cou_description=data.get('cou_description'),
            cou_duration=data.get('cou_duration'),
            cou_difficulty=data.get('cou_difficulty'),
            cou_visibility=data.get('cou_visibility'),
            cou_status='borrador', 
            cou_created_by=user_id,     
             cou_thumbnail=data.get('cou_thumbnail')
        )

        db.session.add(new_course)
        db.session.commit()

        result = course_schema.dump(new_course)
        return jsonify(result), 201

    except Exception as e:
        db.session.rollback()
        print("ERROR REAL:", e)  
        return jsonify({'error': str(e)}), 500
    
    
@course_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """
    Actualizar un curso (Incluyendo publicación)
    """
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        
        # Iteramos sobre los datos enviados (cou_course_name, cou_status, etc.)
        for key, value in data.items():
            if hasattr(course, key):
                setattr(course, key, value)
        
        db.session.commit()
        result = course_schema.dump(course)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar curso: {str(e)}'}), 500
    
    

@course_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """
    Eliminar un curso por ID
    ---
    tags:
      - Cursos
    parameters:
      - name: course_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Curso eliminado exitosamente
      404:
        description: Curso no encontrado
      500:
        description: Error al eliminar curso
    """
    try:
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return jsonify({'message': 'Curso eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al eliminar curso: {str(e)}'}), 500

