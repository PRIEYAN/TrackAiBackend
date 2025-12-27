from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from mongoengine import connect, disconnect
import os
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()


def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Enable logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)) * 60
    
    # MongoDB connection
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://tvk002006_db_user:iamdariyalmogger@mogger.zfl7uwb.mongodb.net/?appName=mogger')
    db_name = os.getenv('MONGODB_DB_NAME', 'tradeflow')
    
    try:
        connect(db=db_name, host=mongodb_uri, alias='default')
    except Exception as e:
        print(f"Warning: MongoDB connection failed: {e}")
    
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # Initialize extensions
    jwt.init_app(app)
    
    # CORS configuration - Allow all origins for Flutter/mobile apps
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app, 
             resources={r"/*": {"origins": "*"}},
             allow_credentials=True,
             allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    else:
        CORS(app, 
             origins=cors_origins.split(','),
             allow_credentials=True,
             allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    
    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.shipment_controller import shipment_bp
    from app.controllers.carrier_controller import carrier_bp
    from app.controllers.customs_controller import customs_bp
    from app.controllers.document_controller import document_bp
    from app.controllers.quote_controller import quote_bp
    from app.controllers.tracking_controller import tracking_bp
    from app.controllers.health_controller import health_bp
    from app.controllers.forwarderController import forwarder_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(shipment_bp, url_prefix='/api/shipments')
    app.register_blueprint(carrier_bp, url_prefix='/api/carriers')
    app.register_blueprint(customs_bp, url_prefix='/api/customs')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(quote_bp, url_prefix='/api/quotes')
    app.register_blueprint(tracking_bp, url_prefix='/api/tracking')
    app.register_blueprint(forwarder_bp, url_prefix='/api/forwarder')
    app.register_blueprint(health_bp)
    
    # Error handlers
    from app.utils.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

