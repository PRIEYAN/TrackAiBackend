from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.shipment import Shipment
from app.models.user import User
from app.utils.auth import get_current_user
from app.views.response_formatter import success_response, error_response, validation_error_response
from datetime import datetime
import uuid
import logging
from mongoengine import Q

logger = logging.getLogger(__name__)

shipment_bp = Blueprint('shipment', __name__)


@shipment_bp.route('/', methods=['POST', 'OPTIONS'])
@shipment_bp.route('/create', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_shipment():
    if request.method == 'OPTIONS':
        return '', 200
    
    # Log request details
    logger.info("=" * 60)
    logger.info("CREATE SHIPMENT REQUEST")
    logger.info("=" * 60)
    logger.info(f"Method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Is JSON: {request.is_json}")
    logger.info(f"Has Form: {bool(request.form)}")
    logger.info(f"Has Data: {bool(request.data)}")
    
    user = get_current_user()
    if not user:
        logger.error("Unauthorized: User not found")
        return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
    
    logger.info(f"User: {user.email} (Role: {user.role})")
    
    # Parse request data
    data = None
    data_source = None
    
    if request.is_json:
        data = request.get_json()
        data_source = "JSON"
        logger.info("Parsing request as JSON")
    elif request.form:
        data = request.form.to_dict()
        data_source = "FORM_DATA"
        logger.info("Parsing request as Form Data")
    elif request.data:
        try:
            import json
            data = json.loads(request.data)
            data_source = "RAW_JSON"
            logger.info("Parsing request as Raw JSON")
        except Exception as e:
            logger.error(f"Failed to parse raw data as JSON: {e}")
            data = None
    else:
        logger.warning("No data found in request")
        data = None
    
    logger.info(f"Data Source: {data_source}")
    logger.info(f"Received Data: {data}")
    
    if not data:
        logger.error("Invalid input: Request body is required")
        return error_response("Invalid input", "Request body is required", "shipments", True, status_code=400)
    
    errors = []
    
    origin_port = data.get('origin_port')
    destination_port = data.get('destination_port')
    weight = data.get('weight') or data.get('gross_weight_kg')
    volume = data.get('volume') or data.get('volume_cbm')
    
    logger.info("Extracted fields:")
    logger.info(f"  origin_port: {origin_port}")
    logger.info(f"  destination_port: {destination_port}")
    logger.info(f"  weight: {weight}")
    logger.info(f"  volume: {volume}")
    
    if not origin_port:
        errors.append({"loc": ["origin_port"], "msg": "Origin port is required", "type": "value_error"})
    if not destination_port:
        errors.append({"loc": ["destination_port"], "msg": "Destination port is required", "type": "value_error"})
    if weight is None:
        errors.append({"loc": ["weight"], "msg": "Weight is required", "type": "value_error"})
    if volume is None:
        errors.append({"loc": ["volume"], "msg": "Volume is required", "type": "value_error"})
    
    if errors:
        logger.warning(f"Validation errors: {errors}")
        return validation_error_response(errors)
    
    try:
        shipment_number = f"SH{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Creating shipment with number: {shipment_number}")
        
        shipment = Shipment(
            shipment_number=shipment_number,
            supplier_id=user,
            origin_port=origin_port,
            destination_port=destination_port,
            gross_weight_kg=float(weight),
            volume_cbm=float(volume)
        )
        shipment.save()
        
        logger.info(f"Shipment created successfully: {shipment_number} (ID: {shipment.id})")
        logger.info("=" * 60)
        
        return success_response(shipment.to_dict(), status_code=201)
    except Exception as e:
        logger.error(f"Error creating shipment: {str(e)}", exc_info=True)
        logger.info("=" * 60)
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@shipment_bp.route('/<shipment_id>', methods=['GET'])
@jwt_required()
def get_shipment(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        
        if not shipment:
            return error_response("Not Found", "Shipment not found", "shipments", True, status_code=404)
        
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        if str(shipment.supplier_id.id) != str(user.id) and str(shipment.buyer_id.id) != str(user.id) if shipment.buyer_id else True:
            if user.role != 'forwarder' or (shipment.forwarder_id and str(shipment.forwarder_id.id) != str(user.id)):
                return error_response("Forbidden", "Not authorized to view this shipment", "shipments", True, status_code=403)
        
        return success_response(shipment.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)


@shipment_bp.route('/list', methods=['GET'])
@shipment_bp.route('/show', methods=['GET'])
@shipment_bp.route('/show_shipments', methods=['GET'])
@jwt_required()
def list_shipments():
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        status_filter = request.args.get('status')
        
        if user.role == 'supplier':
            query = Q(supplier_id=user)
        elif user.role == 'buyer':
            query = Q(buyer_id=user)
        elif user.role == 'forwarder':
            # Forwarders can see shipments assigned to them OR shipments without a forwarder (to bid on)
            query = Q(forwarder_id=user) | Q(forwarder_id__exists=False) | Q(forwarder_id=None)
        else:
            query = Q()
        
        if status_filter:
            query = query & Q(status=status_filter)
        
        shipments = Shipment.objects(query).order_by('-created_at').all()
        
        return success_response([shipment.to_dict() for shipment in shipments], status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)

@shipment_bp.route('/showAcceptedQuotes', methods=['GET'])
@jwt_required()
def showAcceptedQuotes():
    try:
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        quotes = Shipment.objects(status='booked', supplier_id=user.id).all()
        return success_response([quote.to_dict() for quote in quotes], status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", str(e), "database", True, status_code=503)