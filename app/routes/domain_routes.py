from flask import Blueprint, request, jsonify
from app import db
from app.models.domain_model import Domain
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


@domain_bp.route('/<int:dom_id>/graph', methods=['GET'])
#@jwt_required()
def get_domain_graph(dom_id):
    """
    Obtener grafo KST de un dominio
    ---
    tags:
      - Currículo - KST
    security:
      - Bearer: []
    parameters:
      - name: dom_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Grafo del dominio
    """

    domain = Domain.query.get_or_404(dom_id)

    nodes = []
    edges = []

    for sub in domain.subtopics:
        nodes.append({
            "id": sub.sub_id,
            "label": sub.sub_name
        })

        for prereq in sub.prerequisites:
            edges.append({
                "from": prereq.sub_id,
                "to": sub.sub_id
            })

    return jsonify({
        "nodes": nodes,
        "edges": edges
    }), 200


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