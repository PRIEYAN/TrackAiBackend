from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.utils.auth import get_current_user
from app.views.response_formatter import success_response, error_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        return success_response(user.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", "Database error", "database", True, status_code=503)

