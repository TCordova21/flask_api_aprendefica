from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from app import db
from app.models.enrollment_model import Enrollment
from app.schemas.enrollment_schema import enrollment_schema, enrollments_schema, enrollment_detail_schema, enrollments_detail_schema, enrollment_basic_schema, enrollments_student_list_schema 
from app.models.course_instance_model import CourseInstance
from datetime import datetime

enrollment_bp = Blueprint('enrollment', __name__)  

@enrollment_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_enrollments():
    """
    Obtener todas las inscripciones registradas en el sistema
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de todas las inscripciones
        schema:
          type: array
          items:
            $ref: '#/definitions/Enrollment'
      500:
        description: Error al obtener inscripciones
        schema:
          type: object
          properties:
            error:
              type: string
              example: Error al obtener inscripciones
    """
    try:
        enrollments = Enrollment.query.all()
        return enrollments_schema.jsonify(enrollments), 200
    except Exception as e:
        return jsonify({
            'error': f'Error al obtener inscripciones: {str(e)}'
        }), 500

from sqlalchemy import text

@enrollment_bp.route('/', methods=['POST'])
@jwt_required()
def create_enrollment():
    """
    Crea una nueva inscripción para el usuario autenticado usando el código de la instancia y la función SQL.
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coi_ins_code
          properties:
            coi_ins_code:
              type: string
              example: "ABC123"
              description: Código de inscripción de la instancia del curso
    responses:
      201:
        description: Inscripción creada exitosamente e inicializada
      400:
        description: Error en la validación o lógica de la base de datos
      401:
        description: No autorizado
    """

    user_id = get_jwt_identity()
    data = request.get_json()
    coi_ins_code = data.get('coi_ins_code')

    if not coi_ins_code:
        return jsonify({'error': 'coi_ins_code es obligatorio'}), 400

    try:
        query = text("SELECT public.enroll_student_by_code(:usr_id, :code)")
        
        result = db.session.execute(query, {
            "usr_id": user_id,
            "code": coi_ins_code
        })
        
        enr_id = result.scalar()
        db.session.commit()
        new_enrollment = Enrollment.query.get(enr_id)
        return enrollment_schema.jsonify(new_enrollment), 201

    except Exception as e:
        db.session.rollback()
        
        raw_error = str(e.orig) if hasattr(e, 'orig') else str(e)
        clean_error = "Error al inscribirse"
        if "RAISE EXCEPTION" in raw_error or "P0001" in raw_error:
            clean_error = raw_error.split('\n')[0].replace('P0001:', '').strip()

        return jsonify({'error': clean_error}), 400


@enrollment_bp.route('/my', methods=['GET'])
@jwt_required()
def my_enrollments():
    """
    Obtener las inscripciones del usuario autenticado
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de inscripciones del usuario
        schema:
          type: array
          items:
            $ref: '#/definitions/Enrollment'
      401:
        description: No autorizado (token inválido o ausente)
      500:
        description: Error al obtener las inscripciones
    """
    user_id = get_jwt_identity()

    enrollments = Enrollment.query.filter_by(
        usr_id=user_id
    ).all()

    return enrollments_detail_schema.jsonify(enrollments), 200

from sqlalchemy import desc, nulls_last

@enrollment_bp.route('/my/lastEnrollment', methods=['GET'])
@jwt_required()
def get_last_enrollment():
    """
    Obtener la última inscripción del usuario autenticado
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    responses:
      200:
        description: Última inscripción del usuario (serializada con Schema)
        schema:
          $ref: '#/definitions/Enrollment'
      404:
        description: No se encontraron inscripciones
      500:
        description: Error al obtener la inscripción
    """
    try:
        user_id = get_jwt_identity()

        # Consulta robusta con nulos al final
        enrollment = Enrollment.query.filter_by(usr_id=user_id)\
            .order_by(
                nulls_last(desc(Enrollment.last_accessed_at)),
                desc(Enrollment.enr_date)
            ).first()

        if not enrollment:
            return jsonify({'message': 'No se encontraron inscripciones'}), 404

        # Usamos el estándar de Marshmallow para serializar el objeto
        return enrollment_basic_schema.jsonify(enrollment), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@enrollment_bp.route('/<int:enr_id>/withdraw', methods=['PATCH'])
@jwt_required()
def withdraw_enrollment(enr_id):
    """
    Retirar una inscripción del usuario autenticado
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    parameters:
      - name: enr_id
        in: path
        type: integer
        required: true
        description: ID de la inscripción a retirar
    responses:
      200:
        description: Inscripción retirada correctamente
        schema:
          type: object
          properties:
            message:
              type: string
              example: Inscripción retirada correctamente
      401:
        description: No autorizado
      404:
        description: Inscripción no encontrada o no pertenece al usuario
      500:
        description: Error al retirar la inscripción
    """
    user_id = get_jwt_identity()

    enrollment = Enrollment.query.filter_by(
        enr_id=enr_id,
        usr_id=user_id
    ).first_or_404()

    enrollment.enr_status = 'retirado'
    db.session.commit()

    return jsonify({'message': 'Inscripción retirada correctamente'}), 200


@enrollment_bp.route('/api/course-instance/<int:coi_id>/students', methods=['GET'])
def get_instance_students(coi_id):
    """
    Obtener lista optimizada de estudiantes por instancia
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    parameters:
      - name: coi_id
        in: path
        type: integer
        required: true
        description: ID de la instancia del curso
    responses:
      200:
        description: Lista de estudiantes (sin datos repetidos de curso)
        schema:
          type: array
          items:
            type: object
            properties:
              enr_id:
                type: integer
              enr_status:
                type: string
              enr_progress:
                type: number
              enr_date:
                type: string
              last_accessed_at:
                type: string
              user:
                type: object
                properties:
                  usr_id:
                    type: integer
                  usr_first_name:
                    type: string
                  usr_last_name:
                    type: string
                  usr_email:
                    type: string
    """
    try:
        from sqlalchemy.orm import joinedload
        # Query optimizado: solo traemos el usuario
        enrollments = Enrollment.query.options(
            joinedload(Enrollment.user)
        ).filter_by(coi_id=coi_id).all()

        # Usamos el nuevo schema optimizado
        return jsonify(enrollments_student_list_schema.dump(enrollments)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
  
@enrollment_bp.route('/<int:enr_id>/access', methods=['POST'])
@jwt_required()
def update_last_access(enr_id):
    """
    Registra la fecha y hora del último acceso al curso.
    ---
    tags:
      - Inscripciones
    security:
      - Bearer: []
    parameters:
      - name: enr_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Acceso registrado exitosamente
      403:
        description: No autorizado (no es el dueño de la inscripción)
      404:
        description: Inscripción no encontrada
    """
    try:
        user_id = get_jwt_identity()
        # Buscamos la inscripción y verificamos pertenencia en un solo paso
        enrollment = Enrollment.query.filter_by(enr_id=enr_id, usr_id=user_id).first_or_404()
        
        enrollment.last_accessed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "message": "Acceso registrado",
            "last_accessed_at": enrollment.last_accessed_at.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500