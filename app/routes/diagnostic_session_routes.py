from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.diagnostic_session_model import DiagnosticSession
from app.schemas.diagnostic_session_schema import diagnostic_session_schema
from app.models.diagnostic_probability_model import DiagnosticProbability
from app.schemas.diagnostic_probability_schema import diagnostic_probabilities_schema
from app.models.enrollment_model import Enrollment
from app.models.subtopic_model import Subtopic
from app.models.domain_model import Domain
from app.models.course_instance_model import CourseInstance
from app.models.assessment_attempt_model import AssessmentAttempt
from app.models.student_domain_model import StudentDomainProgress
from app.models.student_knowledge_state_model import StudentKnowledgeState
from sqlalchemy import case, func, text
from flask import jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.exercise_model import Exercise
from app.schemas.exercise_schema import exercise_schema
from app.models.diagnostic_session_model import DiagnosticSession
from app.models.diagnostic_question_log_model import DiagnosticQuestionLog 
from datetime import datetime
import random


diagnostic_bp = Blueprint('diagnostic', __name__)



@diagnostic_bp.route('/start', methods=['POST'])
@jwt_required()
def start_diagnostic():
    """
    Iniciar una nueva sesión diagnóstica y registrar el intento oficial
    ---
    tags:
      - Diagnóstico
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - asm_id
            - course_instance_id
          properties:
            asm_id:
              type: integer
              description: ID de la evaluación (Assessment)
            course_instance_id:
              type: integer
              description: ID de la instancia de curso (CourseInstance)
            max_questions:
              type: integer
              default: 30
    responses:
      201:
        description: Sesión e Intento creados exitosamente
      200:
        description: Retorna sesión existente si está activa
      404:
        description: Estudiante no matriculado o curso inexistente
      500:
        description: Error interno
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    asm_id = data.get('asm_id')
    coi_id = data.get('course_instance_id')
    max_q = data.get('max_questions', 30)

    if not asm_id or not coi_id:
        return jsonify({"error": "asm_id y course_instance_id son requeridos"}), 400

    try:
        # 1. Validar Matrícula (Enrollment)
        enrollment = Enrollment.query.filter_by(usr_id=user_id, coi_id=coi_id).first()
        if not enrollment:
            return jsonify({"error": "Estudiante no matriculado en esta instancia"}), 404

        # 2. Verificar si ya existe una sesión KST activa
        active_session = DiagnosticSession.query.filter_by(
            student_id=user_id,
            course_instance_id=coi_id,
            status='IN_PROGRESS'
        ).first()

        if active_session:
            # Si existe, buscamos el asma_id asociado (opcionalmente podrías guardarlo en DiagnosticSession)
            return jsonify({
                "message": "Ya tienes una sesión en progreso",
                "session_id": str(active_session.session_id),
                "enr_id": enrollment.enr_id
            }), 200

        # 3. Registrar el Intento Administrativo (AssessmentAttempt)
        last_attempt_no = db.session.query(func.max(AssessmentAttempt.attempt_no))\
            .filter_by(asm_id=asm_id, enr_id=enrollment.enr_id).scalar() or 0
        
        new_attempt = AssessmentAttempt(
            asm_id=asm_id,
            enr_id=enrollment.enr_id,
            attempt_no=last_attempt_no + 1,
            started_at=func.now()
        )
        db.session.add(new_attempt)
        db.session.flush() # Para generar asma_id

        # 4. Crear la Sesión KST
        new_session = DiagnosticSession(
            asm_id=asm_id,
            student_id=user_id,
            course_instance_id=coi_id,
            max_questions=max_q,
            status='IN_PROGRESS'
        )
        db.session.add(new_session)
        db.session.flush() # Para generar session_id (UUID)

        # 5. Inicializar Probabilidades KST (P=0.5)
        instance = CourseInstance.query.get(coi_id)
        subtopics = db.session.query(Subtopic.sub_id).join(Domain).filter(
            Domain.cou_id == instance.cou_id
        ).all()

        if not subtopics:
            return jsonify({"error": "Este curso no tiene contenidos configurados para evaluar"}), 400

        for sub in subtopics:
            prob = DiagnosticProbability(
                session_id=new_session.session_id,
                sub_id=sub.sub_id,
                p_mastery=0.500 
            )
            db.session.add(prob)

        db.session.commit()

        # Retornamos todo lo necesario para el Frontend
        return jsonify({
            "session_id": str(new_session.session_id),
            "asma_id": new_attempt.asma_id,
            "enr_id": enrollment.enr_id,
            "message": "Sesión e intento iniciados"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "No se pudo iniciar la evaluación", "details": str(e)}), 500

@diagnostic_bp.route('/session/<uuid:session_id>', methods=['GET'])
@jwt_required()
def get_diagnostic_status(session_id):
    """
    Obtener el estado actual de una sesión de diagnóstico
    ---
    tags:
      - Diagnóstico
    parameters:
      - name: session_id
        in: path
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Datos generales de la sesión
    """
    session = DiagnosticSession.query.get_or_404(session_id)
    return diagnostic_session_schema.jsonify(session), 200


@diagnostic_bp.route('/session/<uuid:session_id>/probabilities', methods=['GET'])
@jwt_required()
def get_session_probabilities(session_id):
    """
    Obtener las probabilidades actuales de dominio (Estado Latente)
    ---
    tags:
      - Diagnóstico
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista de subtemas con sus probabilidades de maestría
    """
    probs = DiagnosticProbability.query.filter_by(session_id=session_id).all()
    if not probs:
        return jsonify({"message": "No se encontraron probabilidades para esta sesión"}), 404
        
    return jsonify(diagnostic_probabilities_schema.dump(probs)), 200


@diagnostic_bp.route('/session/<uuid:session_id>/next-question', methods=['GET'])
@jwt_required()


def _get_next_logic(session_id):
    # 1. Obtener datos de la sesión
    session_data = DiagnosticSession.query.get(session_id)
    if not session_data or session_data.current_question_count >= session_data.max_questions:
        return {"message": "finalizado"}, 200

    # 2. Verificar si hay una pregunta ya enviada pero no respondida (evita saltar preguntas al recargar)
    pending_log = DiagnosticQuestionLog.query.filter_by(session_id=session_id, status='asked').first()
    if pending_log:
        exercise = Exercise.query.get(pending_log.exercise_id)
        return {
            "session_id": str(session_id),
            "exercise": exercise_schema.dump(exercise),
            "current_count": session_data.current_question_count
        }, 200

    # 3. Selección de Subtema optimizada (Candidatos en SQL, selección en Python)
    # Traemos los 10 temas más cercanos al nivel de desafío ideal (0.7)
    query_subtopic = text("""
        SELECT dp.sub_id FROM diagnostic_probability dp
        WHERE dp.session_id = :session_id AND dp.p_mastery <= 0.85
        AND (
            NOT EXISTS (SELECT 1 FROM subtopic_dependency sd WHERE sd.sub_id = dp.sub_id)
            OR NOT EXISTS (
                SELECT 1 FROM subtopic_dependency sd
                JOIN diagnostic_probability dp_parent ON sd.prerequisite_id = dp_parent.sub_id
                WHERE sd.sub_id = dp.sub_id AND dp_parent.session_id = :session_id AND dp_parent.p_mastery <= 0.85
            )
        )
        ORDER BY ABS(dp.p_mastery - 0.7) ASC
        LIMIT 10
    """)
    
    res_sub_list = db.session.execute(query_subtopic, {"session_id": session_id}).fetchall()
    
    if not res_sub_list:
        return {"message": "finalizado"}, 200

    # Elegimos uno al azar de los mejores candidatos desde Python (mucho más rápido que SQL RANDOM)
    target_sub_id = random.choice(res_sub_list)[0]

    # 4. Obtener IDs de ejercicios permitidos para este examen
    allowed_res = db.session.execute(
        text("SELECT ex_id FROM assessment_exercise WHERE asm_id = :asm_id"),
        {"asm_id": session_data.asm_id}
    ).fetchall()
    allowed_ids = [r[0] for r in allowed_res]
    
    if not allowed_ids:
        return {"message": "finalizado"}, 200

    # 5. Buscar ejercicio del subtema elegido que no haya sido respondido
    exercise = db.session.query(Exercise).filter(
        Exercise.sub_id == target_sub_id,
        Exercise.ex_id.in_(allowed_ids),
        Exercise.ex_is_active == True
    ).filter(
        ~Exercise.ex_id.in_(
            db.session.query(DiagnosticQuestionLog.exercise_id)
            .filter_by(session_id=session_id, status='answered')
        )
    ).order_by(func.random()).first()

    # 6. Fallback: Si el subtema elegido no tiene ejercicios disponibles, 
    # tomar cualquier ejercicio disponible del examen
    if not exercise:
        exercise = db.session.query(Exercise).filter(
            Exercise.ex_id.in_(allowed_ids),
            Exercise.ex_is_active == True
        ).filter(
            ~Exercise.ex_id.in_(
                db.session.query(DiagnosticQuestionLog.exercise_id)
                .filter_by(session_id=session_id, status='answered')
            )
        ).order_by(func.random()).first()

    if not exercise:
        return {"message": "finalizado"}, 200

    # 7. Registrar el nuevo log y retornar
    new_log = DiagnosticQuestionLog(
        session_id=session_id, 
        sub_id=exercise.sub_id, 
        exercise_id=exercise.ex_id, 
        status='asked'
    )
    db.session.add(new_log)
    db.session.commit()

    return {
        "session_id": str(session_id),
        "exercise": exercise_schema.dump(exercise),
        "current_count": session_data.current_question_count
    }, 200
@diagnostic_bp.route('/session/<uuid:session_id>/submit-answer', methods=['POST'])
@jwt_required()
def submit_answer(session_id):
    data = request.get_json()
    ex_id = data.get('exercise_id')
    user_ans_raw = data.get('user_answer', "")
    dont_know = data.get('dont_know', False)

    try:
        log = DiagnosticQuestionLog.query.filter_by(session_id=session_id, exercise_id=ex_id, status='asked').first_or_404()
        exercise = Exercise.query.get(ex_id)
        
        is_correct = False
        if not dont_know:
            is_correct = (user_ans_raw.strip().lower() == exercise.ex_expected_answer.strip().lower())

        log.student_answer = "SABE_NO_SABE" if dont_know else user_ans_raw
        log.is_correct = is_correct
        log.status = 'answered'
        log.answered_at = datetime.utcnow()

        prob_record = DiagnosticProbability.query.filter_by(session_id=session_id, sub_id=log.sub_id).first()
        p_old = float(prob_record.p_mastery)
        slip, guess = 0.1, 0.2

        if is_correct:
            p_new = (p_old * (1 - slip)) / ((p_old * (1 - slip)) + ((1 - p_old) * guess))
        else:
            p_new = (p_old * slip) / ((p_old * slip) + ((1 - p_old) * (1 - guess)))

        prob_record.p_mastery = min(max(p_new, 0.01), 0.99)

        if is_correct:
            db.session.execute(text("""
                UPDATE diagnostic_probability SET p_mastery = LEAST(p_mastery + 0.05, 0.95)
                WHERE session_id = :sid AND sub_id IN (SELECT prerequisite_id FROM subtopic_dependency WHERE sub_id = :sub_id)
            """), {"sid": session_id, "sub_id": log.sub_id})
        else:
            db.session.execute(text("""
                UPDATE diagnostic_probability SET p_mastery = GREATEST(p_mastery - 0.1, 0.05)
                WHERE session_id = :sid AND sub_id IN (SELECT sub_id FROM subtopic_dependency WHERE prerequisite_id = :sub_id)
            """), {"sid": session_id, "sub_id": log.sub_id})

        session_data = DiagnosticSession.query.get(session_id)
        session_data.current_question_count = (session_data.current_question_count or 0) + 1
        db.session.commit()

        next_data, status_code = _get_next_logic(session_id)
        
        return jsonify({
            "is_correct": is_correct,
            "next_question": next_data if status_code == 200 else None,
            "finished": next_data.get("message") == "finalizado" if isinstance(next_data, dict) else False
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@diagnostic_bp.route('/session/<uuid:session_id>/finish', methods=['POST'])
@jwt_required()
def finish_diagnostic(session_id):
    """
    Finalizar evaluación, actualizar SKS, SDP, Intento y Progreso de Matrícula
    ---
    tags: [Diagnóstico]
    security: [{Bearer: []}]
    parameters:
      - in: path
        name: session_id
        type: string
        format: uuid
        required: true
        description: ID de la sesión diagnóstica a cerrar
    responses:
      200:
        description: Evaluación finalizada con éxito. Tablas de progreso y matrícula actualizadas.
        schema:
          type: object
          properties:
            message: {type: string}
            summary:
              type: object
              properties:
                score: {type: number}
                total_topics: {type: integer}
                mastered: {type: integer}
                learned: {type: integer}
                remaining: {type: integer}
            enr_progress: {type: number, description: "Nuevo progreso de la matrícula"}
      404:
        description: No se encontró la sesión o la matrícula
      500:
        description: Error interno al procesar los datos
    """
    try:
        # 1. Obtener sesión y usuario
        session_data = DiagnosticSession.query.get_or_404(session_id)
        user_id = get_jwt_identity()
        
        if session_data.status == 'COMPLETED':
            return jsonify({"message": "Esta sesión ya había sido finalizada previamente"}), 200

        # 2. Obtener el Enrollment (Centralizamos aquí para actualizar progreso luego)
        enrollment = Enrollment.query.filter_by(
            usr_id=user_id, 
            coi_id=session_data.course_instance_id
        ).first()

        if not enrollment:
            return jsonify({"error": "No se encontró matrícula activa para este curso"}), 404

        # 3. Marcar sesión diagnóstica como completada
        session_data.status = 'COMPLETED'
        session_data.ended_at = datetime.utcnow()

        # 4. Obtener todas las probabilidades del motor KST
        probs = DiagnosticProbability.query.filter_by(session_id=session_id).all()
        if not probs:
            return jsonify({"error": "No se encontraron datos de progreso"}), 400

        # 5. ACTUALIZACIÓN DE TABLAS PERMANENTES POR SUBTEMA (SKS)
        count_mastered = 0
        count_learned = 0

        for p in probs:
            status = 'no_dominado'
            if p.p_mastery >= 0.85:
                status = 'dominado'
                count_mastered += 1
            elif p.p_mastery >= 0.50:
                status = 'aprendido'
                count_learned += 1

            sks_record = StudentKnowledgeState.query.filter_by(
                enr_id=enrollment.enr_id, 
                sub_id=p.sub_id
            ).first()
            
            if sks_record:
                sks_record.mastery_level = status
                sks_record.last_updated = datetime.utcnow()

        # 6. Actualizar fecha de progreso en Dominios (SDP)
        db.session.execute(text("""
            UPDATE student_domain_progress 
            SET last_updated = :now 
            WHERE enr_id = :eid
        """), {"now": datetime.utcnow(), "eid": enrollment.enr_id})

        # 7. Sincronizar Puntaje en el registro de intento (AssessmentAttempt)
        total_topics = len(probs)
        final_score = (count_mastered / total_topics) * 100 if total_topics > 0 else 0
        
        attempt = AssessmentAttempt.query.filter_by(
            asm_id=session_data.asm_id,
            enr_id=enrollment.enr_id
        ).order_by(AssessmentAttempt.started_at.desc()).first()

        if attempt:
            attempt.ended_at = datetime.utcnow()
            attempt.score = round(final_score, 2)

        # 8. IMPLEMENTACIÓN DE TU IDEA: Actualizar el progreso en la matrícula (Enrollment)
        # Esto sirve como el "flag" para que no vuelva a entrar al diagnóstico
        # Si el score es 0, ponemos un valor mínimo (0.01) para indicar que ya se hizo
        enrollment.enr_progress = round(max(final_score, 0.01), 2)
        enrollment.last_accessed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "message": "Evaluación finalizada y progreso de matrícula actualizado",
            "enr_progress": float(enrollment.enr_progress),
            "summary": {
                "score": round(final_score, 2),
                "total_topics": total_topics,
                "mastered": count_mastered,
                "learned": count_learned,
                "remaining": total_topics - (count_mastered + count_learned)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno", "details": str(e)}), 500

@diagnostic_bp.route('/session/<uuid:session_id>/progress-report', methods=['GET'])
@jwt_required()
def get_progress_report(session_id):
    """
    Obtener el resumen de dominios y subtemas para el gráfico de pastel
    ---
    tags: [Diagnóstico]
    security: [{Bearer: []}]
    parameters:
      - in: path
        name: session_id
        type: string
        format: uuid
        required: true
        description: ID de la sesión diagnóstica
    responses:
      200:
        description: Lista de dominios con conteo de subtemas
        schema:
          type: array
          items:
            type: object
            properties:
              domain_name: {type: string}
              total: {type: integer}
              mastered: {type: integer}
              label: {type: string}
      404:
        description: Sesión o matrícula no encontrada
      500:
        description: Error interno del servidor
    """
    try:
        # 1. Identificar sesión y estudiante
        session_data = DiagnosticSession.query.get_or_404(session_id)
        user_id = get_jwt_identity()

        # 2. Obtener el enrollment correspondiente
        enrollment = Enrollment.query.filter_by(
            usr_id=user_id, 
            coi_id=session_data.course_instance_id
        ).first()

        if not enrollment:
            return jsonify({"error": "Estudiante no enrolado en este curso"}), 404

        # 3. Query de Agregación Corregida
        # Filtramos directamente por el cou_id del curso de la sesión
        # Para obtener el cou_id, necesitamos el curso asociado a la instancia
        course_instance = CourseInstance.query.get(session_data.course_instance_id)
        target_cou_id = course_instance.cou_id

        report_query = db.session.query(
            Domain.dom_name,
            func.count(Subtopic.sub_id).label('total_subtopics'),
            func.count(case((StudentKnowledgeState.mastery_level == 'dominado', 1))).label('mastered_subtopics')
        ).join(Subtopic, Domain.dom_id == Subtopic.dom_id)\
         .outerjoin(StudentKnowledgeState, 
                    (Subtopic.sub_id == StudentKnowledgeState.sub_id) & \
                    (StudentKnowledgeState.enr_id == enrollment.enr_id))\
         .filter(Domain.cou_id == target_cou_id)\
         .group_by(Domain.dom_id, Domain.dom_name)\
         .all()

        # 4. Formatear para el Frontend
        report = []
        for row in report_query:
            report.append({
                "domain_name": row.dom_name,
                "total": row.total_subtopics,
                "mastered": row.mastered_subtopics,
                "label": f"{row.mastered_subtopics}/{row.total_subtopics}"
            })

        return jsonify(report), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@diagnostic_bp.route('/enrollment/check-access/<int:coi_id>', methods=['GET'])
@jwt_required()
def check_course_access(coi_id):
    """
    Verificar si el estudiante debe realizar el diagnóstico o puede acceder al curso
    ---
    tags: [Acceso]
    security: [{Bearer: []}]
    parameters:
      - in: path
        name: coi_id
        type: integer
        required: true
        description: ID de la instancia del curso
    responses:
      200:
        description: Estado de acceso del estudiante
        schema:
          type: object
          properties:
            can_access_content: {type: boolean}
            must_do_diagnostic: {type: boolean}
            progress: {type: number}
            message: {type: string}
    """
    try:
        user_id = get_jwt_identity()
        
        # Buscar la matrícula del usuario para este curso específico
        enrollment = Enrollment.query.filter_by(
            usr_id=user_id, 
            coi_id=coi_id
        ).first()

        if not enrollment:
            return jsonify({
                "can_access_content": False,
                "must_do_diagnostic": False,
                "error": "No estás enrolado en este curso"
            }), 404

        # Lógica de decisión:
        # Si el progreso es 0 (o nulo), debe hacer el diagnóstico.
        # Si es > 0, ya tiene un punto de partida.
        must_do_diagnostic = enrollment.enr_progress == 0
        
        return jsonify({
            "can_access_content": not must_do_diagnostic,
            "must_do_diagnostic": must_do_diagnostic,
            "progress": float(enrollment.enr_progress),
            "status": enrollment.enr_status,
            "message": "Redirigir a diagnóstico" if must_do_diagnostic else "Acceso permitido al contenido"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# En tu archivo de rutas de Flask
@diagnostic_bp.route('/course/topics-status/<int:coi_id>', methods=['GET'])
@jwt_required()
def get_learning_path(coi_id):
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(usr_id=user_id, coi_id=coi_id).first()
        
        query = text("""
            SELECT 
                s.sub_id as id,
                s.sub_name as name,
                d.dom_name as domain_name,
                COALESCE(sks.mastery_level, 'no_dominado') as status,
                -- Obtenemos los nombres de los prerrequisitos no cumplidos en un solo string
                (SELECT string_agg(p.sub_name, ', ')
                 FROM subtopic_dependency sd
                 JOIN subtopic p ON sd.prerequisite_id = p.sub_id
                 LEFT JOIN student_knowledge_state sks_p 
                    ON p.sub_id = sks_p.sub_id AND sks_p.enr_id = :enr_id
                 WHERE sd.sub_id = s.sub_id 
                   AND (sks_p.mastery_level IS NULL OR sks_p.mastery_level != 'dominado')
                ) as missing_prerequisites
            FROM subtopic s
            JOIN domain d ON s.dom_id = d.dom_id
            JOIN course_instance ci ON d.cou_id = ci.cou_id
            LEFT JOIN student_knowledge_state sks ON s.sub_id = sks.sub_id AND sks.enr_id = :enr_id
            WHERE ci.coi_id = :coi_id
            ORDER BY d.dom_id, s.sub_id
        """)

        result = db.session.execute(query, {"enr_id": enrollment.enr_id, "coi_id": coi_id})
        
        topics = []
        for row in result:
            topics.append({
                "id": row.id,
                "name": row.name,
                "domain_name": row.domain_name,
                "status": row.status,
                "is_locked": bool(row.missing_prerequisites),
                "prerequisites": row.missing_prerequisites # Aquí van los nombres
            })

        return jsonify({"topics": topics}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diagnostic_bp.route('/progress-report/<int:coi_id>', methods=['GET'])
@jwt_required()
def get_progress_report_by_coi(coi_id):
    try:
        user_id = get_jwt_identity()
        enrollment = Enrollment.query.filter_by(usr_id=user_id, coi_id=coi_id).first()
        
        if not enrollment:
            return jsonify({"error": "No enrolado"}), 404

        # IMPORTANTE: Tu frontend espera un objeto con la llave "report"
        report_query = db.session.query(
            Domain.dom_name,
            func.count(Subtopic.sub_id).label('total'),
            func.count(case((StudentKnowledgeState.mastery_level == 'dominado', 1))).label('mastered')
        ).join(Subtopic, Domain.dom_id == Subtopic.dom_id)\
         .outerjoin(StudentKnowledgeState, 
                    (Subtopic.sub_id == StudentKnowledgeState.sub_id) & \
                    (StudentKnowledgeState.enr_id == enrollment.enr_id))\
         .filter(Domain.cou_id == CourseInstance.query.get(coi_id).cou_id)\
         .group_by(Domain.dom_id, Domain.dom_name)\
         .all()

        report_data = [
            {"domain_name": row.dom_name, "total": row.total, "mastered": row.mastered} 
            for row in report_query
        ]

        return jsonify({"report": report_data}), 200 # <-- Ajustado a res.data.report
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@diagnostic_bp.route('/learning/complete-subtopic', methods=['POST'])
@jwt_required()
def complete_subtopic():
    """
    Registrar dominio de un subtema
    ---
    tags:
      - Learning Progress
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            sub_id:
              type: integer
              example: 10
            enr_id:
              type: integer
              example: 1
    responses:
      200:
        description: Progreso actualizado correctamente
      400:
        description: Faltan datos requeridos
      500:
        description: Error de servidor
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    sub_id = data.get('sub_id')
    enr_id = data.get('enr_id')

    if not sub_id or not enr_id:
        return jsonify({"error": "sub_id y enr_id son requeridos"}), 400

    try:
        # 1. Verificar existencia del subtema
        subtopic = Subtopic.query.get(sub_id)
        if not subtopic:
            return jsonify({"error": "Subtema no encontrado"}), 404

        # 2. Actualizar o Crear SKS (Estado de conocimiento)
        sks_record = StudentKnowledgeState.query.filter_by(
            enr_id=enr_id, 
            sub_id=sub_id
        ).first()

        if not sks_record:
            sks_record = StudentKnowledgeState(enr_id=enr_id, sub_id=sub_id)
            db.session.add(sks_record)
        
        sks_record.mastery_level = 'dominado'
        sks_record.last_updated = datetime.utcnow()

        # 3. Actualizar Progreso del Dominio (SDP)
        dom_id = subtopic.dom_id
        total_in_domain = Subtopic.query.filter_by(dom_id=dom_id).count()
        
        # Conteo preciso de dominados en este dominio
        mastered_in_domain = db.session.query(func.count(StudentKnowledgeState.sks_id))\
            .join(Subtopic, StudentKnowledgeState.sub_id == Subtopic.sub_id)\
            .filter(
                StudentKnowledgeState.enr_id == enr_id,
                Subtopic.dom_id == dom_id,
                StudentKnowledgeState.mastery_level == 'dominado'
            ).scalar()

        sdp_record = StudentDomainProgress.query.filter_by(enr_id=enr_id, dom_id=dom_id).first()
        if not sdp_record:
            sdp_record = StudentDomainProgress(enr_id=enr_id, dom_id=dom_id)
            db.session.add(sdp_record)

        if mastered_in_domain >= total_in_domain:
            sdp_record.progress_status = 'dominado'
        elif mastered_in_domain > 0:
            sdp_record.progress_status = 'aprendido'
        else:
            sdp_record.progress_status = 'no_dominado'
        
        sdp_record.last_updated = datetime.utcnow()

        # 4. Actualizar Progreso Global (Enrollment)
        enrollment = Enrollment.query.get(enr_id)
        if enrollment:
            # Total de subtemas del curso
            total_course_subtopics = db.session.query(func.count(Subtopic.sub_id))\
                .join(Domain, Subtopic.dom_id == Domain.dom_id)\
                .join(CourseInstance, Domain.cou_id == CourseInstance.cou_id)\
                .filter(CourseInstance.coi_id == enrollment.coi_id).scalar()

            # Total dominados por el alumno en este curso
            total_course_mastered = db.session.query(func.count(StudentKnowledgeState.sks_id))\
                .join(Subtopic, StudentKnowledgeState.sub_id == Subtopic.sub_id)\
                .join(Domain, Subtopic.dom_id == Domain.dom_id)\
                .join(CourseInstance, Domain.cou_id == CourseInstance.cou_id)\
                .filter(
                    StudentKnowledgeState.enr_id == enr_id, 
                    StudentKnowledgeState.mastery_level == 'dominado',
                    CourseInstance.coi_id == enrollment.coi_id
                ).scalar()

            if total_course_subtopics and total_course_subtopics > 0:
                new_progress = (total_course_mastered / total_course_subtopics) * 100
                enrollment.enr_progress = round(new_progress, 2)
                enrollment.last_accessed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Progreso actualizado",
            "global_progress": float(enrollment.enr_progress) if enrollment else 0
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500