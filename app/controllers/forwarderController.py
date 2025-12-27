from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.shipment import Shipment
from app.models.user import User
from app.utils.auth import get_current_user
from app.views.response_formatter import success_response, error_response
from mongoengine import Q
import logging

logger = logging.getLogger(__name__)

forwarder_bp = Blueprint('forwarder', __name__)


@forwarder_bp.route('/show-shipments', methods=['GET', 'OPTIONS'])
@jwt_required()
def show_shipments():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        checkForwarder = User.objects(id=user.id, role='forwarder').first()
        if not checkForwarder:
            return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
        
        # Get all shipments without forwarder_id (available for bidding)
        shipments = Shipment.objects(Q(forwarder_id__exists=False) | Q(forwarder_id=None))
        
        return success_response([shipment.to_dict() for shipment in shipments], status_code=200)
    except Exception as e:
        logger.error(f"Error in show_shipments: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@forwarder_bp.route('/my-profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def my_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        checkForwarder = User.objects(id=user.id, role='forwarder').first()
        if not checkForwarder:
            return error_response("Unauthorized", "User is not a forwarder", "auth", True, status_code=401)
        
        return success_response(checkForwarder.to_dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error in my_profile: {str(e)}", exc_info=True)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)