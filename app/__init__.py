from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request 
from flasgger import Swagger
from flask_compress import Compress
from sqlalchemy import event 

db = SQLAlchemy()

# --- BLOQUE DE AUDITORÍA CENTRALIZADA ---
@event.listens_for(db.session, "after_begin")
def set_audit_user_context(session, transaction, connection):
    """
    Inyecta el ID del usuario en la sesión de PostgreSQL cada vez que 
    comienza una transacción de SQLAlchemy.
    """
    try:
  
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if user_id:
           
            connection.execute(
                db.text("SET LOCAL app.current_user_id = :uid"), 
                {"uid": str(user_id)}
            )
    except Exception:
      
        pass

ma = Marshmallow()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()
compress = Compress()

template = {
    "swagger": "2.0",
    "info": {
        "title": "API de Aprendizaje",
        "description": "Documentación de la API REST para el software de aprendizaje",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Token JWT. Usa el formato: **Bearer <tu_token>**"
        }
    },
    "security": [
        {"Bearer": []}
    ]
}

swagger = Swagger(template=template)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    compress.init_app(app)

    CORS(app)  # luego puedes restringir

    Migrate(app, db)

    from app.routes.user_routes import user_bp
    from app.routes.role_routes import role_bp
    from app.routes.course_routes import course_bp
    from app.routes.course_instance_routes import course_instance_bp
    from app.routes.enrollment_routes import enrollment_bp
    from app.routes.domain_routes import domain_bp
    from app.routes.subtopic_routes import subtopic_bp
    from app.routes.learning_resource_routes import learning_resource_bp
    from app.routes.exercise_routes import exercise_bp
    from app.routes.assessment_routes import assessment_bp
    from app.routes.assessment_exercise_routes import assessment_exercise_bp
    from app.routes.diagnostic_session_routes import diagnostic_bp
    from app.routes.attempt_routes import attempt_bp
    from app.routes.exercise_attempt_routes import attempt_exercise_bp
    from app.routes.audit_routes import audit_bp

    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(role_bp, url_prefix="/api/roles")
    app.register_blueprint(course_bp, url_prefix="/api/courses")
    app.register_blueprint(course_instance_bp, url_prefix="/api/course_instances")
    app.register_blueprint(enrollment_bp, url_prefix="/api/enrollments")
    app.register_blueprint(domain_bp, url_prefix="/api/domains")
    app.register_blueprint(subtopic_bp, url_prefix="/api/subtopics")
    app.register_blueprint(learning_resource_bp, url_prefix="/api/learning_resources")
    app.register_blueprint(exercise_bp, url_prefix="/api/exercises")
    app.register_blueprint(assessment_bp, url_prefix="/api/assessment")
    app.register_blueprint(assessment_exercise_bp, url_prefix="/api/assessment_exercise")
    app.register_blueprint(diagnostic_bp, url_prefix="/api/diagnostic")
    app.register_blueprint(attempt_bp, url_prefix="/api/attempts")
    app.register_blueprint(attempt_exercise_bp, url_prefix="/api/exercise-attempts")
    app.register_blueprint(audit_bp, url_prefix="/api/audits")

    return app
