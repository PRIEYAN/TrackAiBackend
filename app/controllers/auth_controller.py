from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_token, get_current_user
from app.utils.validators import validate_email_format, validate_phone, validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Accept both JSON and form data for Flutter compatibility
    if request.is_json:
        data = request.get_json()
    elif request.form:
        data = request.form.to_dict()
    elif request.data:
        try:
            import json
            data = json.loads(request.data)
        except:
            return error_response("Invalid input", "Request must be valid JSON", "validation", True, status_code=400)
    else:
        return error_response("Invalid input", "Request body is required", "validation", True, status_code=400)
    
    if not data:
        return error_response("Invalid input", "Request body is required", "validation", True, status_code=400)
    
    errors = []
    
    email = data.get('email')
    if not email:
        errors.append({"loc": ["email"], "msg": "Email is required", "type": "value_error"})
    else:
        is_valid, msg = validate_email_format(email)
        if not is_valid:
            errors.append({"loc": ["email"], "msg": msg, "type": "value_error"})
        else:
            existing_user = User.objects(email=email).first()
            if existing_user:
                return error_response("Bad Request", "User with this email already exists", "auth", True, status_code=400)
    
    password = data.get('password')
    if not password:
        errors.append({"loc": ["password"], "msg": "Password is required", "type": "value_error"})
    elif len(password) < 8:
        errors.append({"loc": ["password"], "msg": "Password must be at least 8 characters", "type": "value_error"})
    
    name = data.get('name')
    if not name:
        errors.append({"loc": ["name"], "msg": "Name is required", "type": "value_error"})
    elif len(name) < 2:
        errors.append({"loc": ["name"], "msg": "Name must be at least 2 characters", "type": "value_error"})
    
    phone = data.get('phone')
    if not phone:
        errors.append({"loc": ["phone"], "msg": "Phone is required", "type": "value_error"})
    else:
        is_valid, msg = validate_phone(phone)
        if not is_valid:
            errors.append({"loc": ["phone"], "msg": msg, "type": "value_error"})
    
    role = data.get('role')
    if not role:
        errors.append({"loc": ["role"], "msg": "Role is required", "type": "value_error"})
    elif role not in ['supplier', 'forwarder', 'buyer']:
        errors.append({"loc": ["role"], "msg": "Role must be supplier, forwarder, or buyer", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    try:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            name=name,
            company_name=data.get('company_name'),
            phone=phone,
            role=role,
            gstin=data.get('gstin'),
            country=data.get('country', 'IN')
        )
        user.save()
        return success_response(user.to_dict(), status_code=201)
    except Exception as e:
        error_msg = str(e)
        if 'duplicate' in error_msg.lower() or 'already exists' in error_msg.lower() or 'E11000' in error_msg:
            return error_response("Bad Request", "User with this email already exists", "auth", True, status_code=400)
        return error_response("Service Unavailable", error_msg, "database", True, status_code=503)


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Log request details for debugging
    from flask import current_app
    if current_app:
        current_app.logger.debug(f"Login request - Content-Type: {request.content_type}")
        current_app.logger.debug(f"Login request - Headers: {dict(request.headers)}")
        current_app.logger.debug(f"Login request - Data: {request.data}")
        current_app.logger.debug(f"Login request - is_json: {request.is_json}")
        current_app.logger.debug(f"Login request - form: {request.form}")
    
    # Accept both JSON and form data for Flutter compatibility
    if request.is_json:
        data = request.get_json()
    elif request.form:
        data = request.form.to_dict()
    elif request.data:
        try:
            import json
            data = json.loads(request.data)
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Failed to parse JSON: {e}")
            data = None
    else:
        data = None
    
    if not data:
        return error_response("Invalid input", "Request body is required. Send JSON with email and password.", "auth", True, status_code=400)
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return error_response("Invalid input", "Email and password are required", "auth", True, status_code=400)
    
    try:
        user = User.objects(email=email).first()
        if not user or not verify_password(password, user.hashed_password):
            return error_response("Unauthorized", "Incorrect email or password", "auth", True, status_code=401)
        
        token_data = create_token(user)
        return success_response(token_data, status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)

