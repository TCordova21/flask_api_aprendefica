from flask import Blueprint, jsonify, request
from app.models.audit_model import AuditLog
from app.schemas.audit_schema import audit_schema, audits_schema
from flask_jwt_extended import jwt_required


audit_bp = Blueprint('audit_bp', __name__)
@audit_bp.route('/', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """
    Obtener lista de logs de auditoría
    ---
    tags:
      - Auditoría
    security:
      - Bearer: []
    parameters:
      - name: table
        in: query
        type: string
        description: Filtrar por nombre de tabla (ej. users, roles)
      - name: action
        in: query
        type: string
        description: Filtrar por acción (INSERT, UPDATE, DELETE)
    responses:
      200:
        description: Lista de logs recuperada exitosamente
        schema:
          type: array
          items:
            $ref: '#/definitions/AuditLog'
    """
    table = request.args.get('table')
    action = request.args.get('action')
    
    query = AuditLog.query

    if table:
        query = query.filter(AuditLog.table_name == table)
    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.changed_at.desc()).limit(200).all()
    return jsonify(audits_schema.dump(logs)), 200

@audit_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_audit_detail(id):
    """
    Obtener detalle de un log específico
    ---
    tags:
      - Auditoría
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID del log de auditoría
    responses:
      200:
        description: Detalle del log recuperado
        schema:
          $ref: '#/definitions/AuditLog'
      404:
        description: Log no encontrado
    """
    log = AuditLog.query.get_or_404(id)
    return jsonify(audit_schema.dump(log)), 200