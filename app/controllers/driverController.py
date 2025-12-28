from flask import Blueprint, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from app.models.driver import Driver
from app.models.shipment import Shipment
from app.utils.auth import hash_password, verify_password
from app.utils.validators import validate_email_format, validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
import logging

logger = logging.getLogger(__name__)

driver_bp = Blueprint('driver', __name__)


def get_current_driver():
    """Get current driver from JWT token"""
    email = get_jwt_identity()
    claims = get_jwt()
    driver_id = claims.get('driver_id')
    
    if driver_id:
        return Driver.objects(id=driver_id).first()
    else:
        # Fallback to email lookup
        return Driver.objects(email=email).first()


def create_driver_token(driver: Driver) -> dict:
    access_token = create_access_token(
        identity=driver.email,
        additional_claims={"role": "driver", "driver_id": str(driver.id)}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,  # 30 minutes
        "driver": driver.to_dict()
    }


@driver_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Accept both JSON and form data
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
    
    username = data.get('username')
    if not username:
        errors.append({"loc": ["username"], "msg": "Username is required", "type": "value_error"})
    elif len(username) < 3:
        errors.append({"loc": ["username"], "msg": "Username must be at least 3 characters", "type": "value_error"})
    else:
        existing_driver = Driver.objects(username=username).first()
        if existing_driver:
            return error_response("Bad Request", "Driver with this username already exists", "auth", True, status_code=400)
    
    email = data.get('email')
    if not email:
        errors.append({"loc": ["email"], "msg": "Email is required", "type": "value_error"})
    else:
        is_valid, msg = validate_email_format(email)
        if not is_valid:
            errors.append({"loc": ["email"], "msg": msg, "type": "value_error"})
        else:
            existing_driver = Driver.objects(email=email).first()
            if existing_driver:
                return error_response("Bad Request", "Driver with this email already exists", "auth", True, status_code=400)
    
    password = data.get('password')
    if not password:
        errors.append({"loc": ["password"], "msg": "Password is required", "type": "value_error"})
    elif len(password) < 8:
        errors.append({"loc": ["password"], "msg": "Password must be at least 8 characters", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    try:
        driver = Driver(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=True
        )
        driver.save()
        
        token_data = create_driver_token(driver)
        return success_response(token_data, status_code=201)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in driver registration: {error_msg}", exc_info=True)
        if 'duplicate' in error_msg.lower() or 'already exists' in error_msg.lower() or 'E11000' in error_msg:
            if 'username' in error_msg.lower():
                return error_response("Bad Request", "Driver with this username already exists", "auth", True, status_code=400)
            return error_response("Bad Request", "Driver with this email already exists", "auth", True, status_code=400)
        return error_response("Service Unavailable", error_msg, "database", True, status_code=503)


@driver_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json()
    elif request.form:
        data = request.form.to_dict()
    elif request.data:
        try:
            import json
            data = json.loads(request.data)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            data = None
    else:
        data = None
    
    if not data:
        return error_response("Invalid input", "Request body is required. Send JSON with email/username and password.", "auth", True, status_code=400)
    
    email_or_username = data.get('email') or data.get('username')
    password = data.get('password')
    
    if not email_or_username or not password:
        return error_response("Invalid input", "Email/username and password are required", "auth", True, status_code=400)
    
    try:
        # Try to find driver by email or username
        driver = Driver.objects(email=email_or_username).first()
        if not driver:
            driver = Driver.objects(username=email_or_username).first()
        
        if not driver or not verify_password(password, driver.hashed_password):
            return error_response("Unauthorized", "Incorrect email/username or password", "auth", True, status_code=401)
        
        if not driver.is_active:
            return error_response("Forbidden", "Driver account is inactive", "auth", True, status_code=403)
        
        token_data = create_driver_token(driver)
        return success_response(token_data, status_code=200)
    except Exception as e:
        logger.error(f"Error in driver login: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@driver_bp.route('/my-profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def my_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        driver = get_current_driver()
        if not driver:
            return error_response("Unauthorized", "Driver not found", "auth", True, status_code=401)
        
        if not driver.is_active:
            return error_response("Forbidden", "Driver account is inactive", "auth", True, status_code=403)
        
        return success_response(driver.to_dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error in my_profile: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@driver_bp.route('/my-shipments', methods=['GET', 'OPTIONS'])
@jwt_required()
def my_shipments():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        driver = get_current_driver()
        if not driver:
            return error_response("Unauthorized", "Driver not found", "auth", True, status_code=401)
        
        # Get the most recent shipment assigned to the driver
        shipment = Shipment.objects(assigned_driver_id=driver).order_by('-created_at').first()
        if not shipment:
            return success_response(None, status_code=200)  # Return empty instead of 404
        
        return success_response(shipment.to_dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error in my_shipments: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)