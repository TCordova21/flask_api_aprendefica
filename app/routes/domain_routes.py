from flask import Blueprint, request, jsonify
from app import db
from app.models.domain_model import Domain
from app.models.student_knowledge_state_model import StudentKnowledgeState
from app.schemas.domain_schema import domain_schema, domains_schema 
from flask_jwt_extended import jwt_required, get_jwt_identity

domain_bp = Blueprint("domain_bp", __name__, url_prefix="/api/domains")

@domain_bp.route("/course/<int:cou_id>", methods=["GET"])

def get_domains_by_course(cou_id):
    """
    Obtener dominios por curso
    ---
    tags:
      - Currículo - Dominios
    parameters:
      - name: cou_id
        in: path
        type: integer
        required: true
        description: ID del curso
    responses:
      200:
        description: Lista de dominios del curso
        schema:
          type: array
          items:
            $ref: '#/definitions/Domain'
      404:
        description: Curso sin dominios
      500:
        description: Error interno
    """
    domains = Domain.query.filter_by(cou_id=cou_id).all()
    return domains_schema.jsonify(domains), 200


@domain_bp.route("/", methods=["POST"])
def create_domain():

    """
    Crear un dominio para un curso
    ---
    tags:
      - Currículo - Dominios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - cou_id
            - dom_name
          properties:
            cou_id:
              type: integer
              example: 10
            dom_name:
              type: string
              example: Álgebra
            dom_description:
              type: string
              example: Dominio de álgebra básica
    responses:
      201:
        description: Dominio creado exitosamente
        schema:
          $ref: '#/definitions/Domain'
      400:
        description: Datos inválidos
      409:
        description: Dominio duplicado
      500:
        description: Error interno
    """

    data = request.get_json()
    domain = Domain(**data)
    db.session.add(domain)
    db.session.commit()
    return domain_schema.jsonify(domain), 201


@domain_bp.route('/<int:dom_id>/graph/<int:enr_id>', methods=['GET'])
def get_kst_graph(dom_id, enr_id):
    domain = Domain.query.get_or_404(dom_id)
    
    # 1. Obtener lo que el estudiante YA domina
    mastered_records = StudentKnowledgeState.query.filter_by(
        enr_id=enr_id, mastery_level='dominado'
    ).all()
    mastered_ids = {ms.sub_id for ms in mastered_records}

    nodes = []
    edges = []

    # 2. Construir mapa de dependencias para el algoritmo KST
    for sub in domain.subtopics:
        # Algoritmo de Frontera: ¿Están todos sus prerrequisitos dominados?
        prereqs_ids = {p.sub_id for p in sub.prerequisites}
        
        # Un subtema está en la "Frontera" si:
        # NO está dominado Y (No tiene prerrequisitos O todos sus prerrequisitos están dominados)
        is_in_fringe = (sub.sub_id not in mastered_ids) and (prereqs_ids.issubset(mastered_ids))
        
        # Determinar estatus para el frontend
        status = 'locked'
        if sub.sub_id in mastered_ids:
            status = 'completed'
        elif is_in_fringe:
            status = 'fringe' # ¡Esta es la zona de aprendizaje activo!

        nodes.append({
            "id": str(sub.sub_id),
            "type": "kstNode",
            "data": { 
                "label": sub.sub_name,
                "status": status,
                "is_fringe": is_in_fringe
            },
            "position": {"x": 0, "y": 0}
        })

        for prereq in sub.prerequisites:
            edges.append({
                "id": f"e{prereq.sub_id}-{sub.sub_id}",
                "source": str(prereq.sub_id),
                "target": str(sub.sub_id),
                "animated": is_in_fringe, # Animamos el camino hacia la frontera
                "style": { "stroke": "#cf3136" if sub.sub_id in mastered_ids else "#d1d5db" }
            })

    return jsonify({"nodes": nodes, "edges": edges}), 200

@domain_bp.route("/<int:dom_id>", methods=["PUT"])
@jwt_required()
def update_domain(dom_id):
    """
    Actualizar un dominio existente
    ---
    tags:
      - Currículo - Dominios
    security:
      - Bearer: []
    parameters:
      - name: dom_id
        in: path
        type: integer
        required: true
        description: ID del dominio a actualizar
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            dom_name:
              type: string
              example: Álgebra Lineal
            dom_description:
              type: string
              example: Actualización del dominio de álgebra
    responses:
      200:
        description: Dominio actualizado exitosamente
        schema:
          $ref: '#/definitions/Domain'
      404:
        description: Dominio no encontrado
      500:
        description: Error interno
    """
    try:
        domain = Domain.query.get_or_404(dom_id)
        data = request.get_json()

        # Actualizamos solo los campos que vengan en el JSON
        domain.dom_name = data.get("dom_name", domain.dom_name)
        domain.dom_description = data.get("dom_description", domain.dom_description)
        # Si permites cambiar el curso al que pertenece:
        domain.cou_id = data.get("cou_id", domain.cou_id)

        db.session.commit()
        return domain_schema.jsonify(domain), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "No se pudo actualizar el dominio", "details": str(e)}), 500


@domain_bp.route("/<int:dom_id>", methods=["DELETE"])
#@jwt_required()
def delete_domain(dom_id):
    """
    Eliminar un dominio
    ---
    tags:
      - Currículo - Dominios
    security:
      - Bearer: []
    parameters:
      - name: dom_id
        in: path
        type: integer
        required: true
        description: ID del dominio a eliminar
    responses:
      200:
        description: Dominio eliminado exitosamente
      404:
        description: Dominio no encontrado
      500:
        description: Error interno (posiblemente por restricciones de llave foránea)
    """
    try:
        domain = Domain.query.get_or_404(dom_id)
        
        db.session.delete(domain)
        db.session.commit()
        
        return jsonify({"message": f"Dominio {dom_id} eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        # Nota: Esto fallará si hay subtemas asociados y no tienes "CASCADE delete" en la BD
        return jsonify({
            "error": "No se pudo eliminar el dominio", 
            "details": "Asegúrese de que el dominio no tenga subtemas asociados o configure el borrado en cascada."
        }), 500