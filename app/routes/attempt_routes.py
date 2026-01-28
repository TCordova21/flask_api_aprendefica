from flask import Blueprint, request, jsonify
from app import db
from app.models.assessment_attempt_model import AssessmentAttempt
from app.schemas.assessment_attempt_schema import assessment_attempt_schema, assessment_attempts_schema
from sqlalchemy import func
from datetime import datetime

attempt_bp = Blueprint("attempt_bp", __name__, url_prefix="/api/attempts")

@attempt_bp.route("/start", methods=["POST"])
def start_attempt():
    """
    Registrar el inicio de un intento
    ---
    tags:
      - Evaluación - Intentos
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            asm_id: {type: integer}
            enr_id: {type: integer}
    """
    data = request.get_json()
    asm_id = data.get('asm_id')
    enr_id = data.get('enr_id')

    # Calcular el número de intento automáticamente
    last_attempt = db.session.query(func.max(AssessmentAttempt.attempt_no))\
        .filter_by(asm_id=asm_id, enr_id=enr_id).scalar() or 0
    
    new_attempt = AssessmentAttempt(
        asm_id=asm_id,
        enr_id=enr_id,
        attempt_no=last_attempt + 1
    )
    
    db.session.add(new_attempt)
    db.session.commit()
    return assessment_attempt_schema.jsonify(new_attempt), 201

@attempt_bp.route("/<int:asma_id>/finish", methods=["PUT"])
def finish_attempt(asma_id):
    """
    Finalizar intento y registrar puntaje
    """
    attempt = AssessmentAttempt.query.get_or_404(asma_id)
    data = request.get_json()

    attempt.finished_at = datetime.utcnow()
    attempt.score = data.get('score')
    attempt.is_passed = data.get('is_passed', False)
    attempt.feedback = data.get('feedback')

    db.session.commit()
    return assessment_attempt_schema.jsonify(attempt), 200

@attempt_bp.route("/enrollment/<int:enr_id>", methods=["GET"])
def get_student_attempts(enr_id):
    """
    Obtener historial de intentos de un estudiante
    """
    attempts = AssessmentAttempt.query.filter_by(enr_id=enr_id).order_by(AssessmentAttempt.attempt_no.desc()).all()
    return assessment_attempts_schema.jsonify(attempts), 200