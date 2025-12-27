from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.auth import get_current_user
from app.utils.validators import validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
from app.models.shipment import Shipment
from datetime import datetime, timedelta
import random

carrier_bp = Blueprint('carrier', __name__)


@carrier_bp.route('/booking/create', methods=['POST'])
@jwt_required()
def create_booking():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    carrier = data.get('carrier')
    origin = data.get('origin')
    destination = data.get('destination')
    container_type = data.get('containerType')
    quantity = data.get('quantity')
    
    if not carrier:
        errors.append({"loc": ["carrier"], "msg": "Carrier is required", "type": "value_error"})
    if not origin:
        errors.append({"loc": ["origin"], "msg": "Origin is required", "type": "value_error"})
    if not destination:
        errors.append({"loc": ["destination"], "msg": "Destination is required", "type": "value_error"})
    if not container_type:
        errors.append({"loc": ["containerType"], "msg": "Container type is required", "type": "value_error"})
    if not quantity or not isinstance(quantity, int) or quantity < 1:
        errors.append({"loc": ["quantity"], "msg": "Quantity must be a positive integer", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    booking_number = f"{carrier[:3].upper()}{random.randint(100000, 999999)}"
    etd = datetime.utcnow() + timedelta(days=random.randint(7, 14))
    
    return success_response({
        "bookingNumber": booking_number,
        "carrier": carrier,
        "status": "CONFIRMED",
        "vessel": f"MV {carrier} EXPRESS",
        "etd": etd.isoformat()
    })


@carrier_bp.route('/booking/status/<booking_number>', methods=['GET'])
@jwt_required()
def get_booking_status(booking_number):
    return success_response({
        "bookingNumber": booking_number,
        "carrier": "MAERSK",
        "status": "CONFIRMED",
        "containerAllocated": True
    })


@carrier_bp.route('/schedule/search', methods=['GET'])
@jwt_required()
def search_schedule():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    
    if not origin or not destination:
        return error_response("Invalid input", "Origin and destination are required", "carriers", True, status_code=400)
    
    etd = datetime.utcnow() + timedelta(days=random.randint(7, 14))
    eta = etd + timedelta(days=random.randint(20, 35))
    transit_days = (eta - etd).days
    
    return success_response({
        "carrier": "MAERSK",
        "vessel": "MV MAERSK EXPRESS",
        "etd": etd.isoformat(),
        "eta": eta.isoformat(),
        "transitDays": transit_days
    })


@carrier_bp.route('/rates/quote', methods=['POST'])
@jwt_required()
def get_rate_quote():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    origin = data.get('origin')
    destination = data.get('destination')
    container_type = data.get('containerType')
    
    if not origin:
        errors.append({"loc": ["origin"], "msg": "Origin is required", "type": "value_error"})
    if not destination:
        errors.append({"loc": ["destination"], "msg": "Destination is required", "type": "value_error"})
    if not container_type:
        errors.append({"loc": ["containerType"], "msg": "Container type is required", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    base_rate = random.uniform(1000, 5000)
    validity = datetime.utcnow() + timedelta(days=30)
    
    return success_response({
        "carrier": "MAERSK",
        "containerType": container_type,
        "rateUSD": round(base_rate, 2),
        "currency": "USD",
        "validity": validity.isoformat()
    })


@carrier_bp.route('/tracking/container/<container_number>', methods=['GET'])
@jwt_required()
def track_container(container_number):
    return success_response({
        "containerNumber": container_number,
        "carrier": "MAERSK",
        "currentLocation": "Port of Singapore",
        "status": "IN_TRANSIT",
        "lastUpdated": datetime.utcnow().isoformat()
    })


@carrier_bp.route('/ai/rates/predict', methods=['POST'])
@jwt_required()
def predict_rate():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    errors = []
    origin = data.get('origin')
    destination = data.get('destination')
    carrier = data.get('carrier')
    container_type = data.get('containerType')
    current_rate = data.get('currentRateUSD')
    
    if not origin:
        errors.append({"loc": ["origin"], "msg": "Origin is required", "type": "value_error"})
    if not destination:
        errors.append({"loc": ["destination"], "msg": "Destination is required", "type": "value_error"})
    if not carrier:
        errors.append({"loc": ["carrier"], "msg": "Carrier is required", "type": "value_error"})
    if not container_type:
        errors.append({"loc": ["containerType"], "msg": "Container type is required", "type": "value_error"})
    if current_rate is None or not isinstance(current_rate, (int, float)):
        errors.append({"loc": ["currentRateUSD"], "msg": "Current rate is required and must be a number", "type": "value_error"})
    
    if errors:
        return validation_error_response(errors)
    
    from app.services.ai_service import AIService
    ai_service = AIService()
    prediction = ai_service.predict_rate(origin, destination, carrier, container_type, current_rate)
    
    return success_response(prediction)


@carrier_bp.route('/AllQuotes', methods=['POST'])
@jwt_required()
def getAllQuotes():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    user = get_current_user()
    if not user:
        return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
    
    quotes = Shipment.objects(status='quoted', supplier_id=user.id).all()
    return success_response([quote.to_dict() for quote in quotes])

@carrier_bp.route('/acceptQuote', methods=['POST'])
@jwt_required()
def acceptQuote():
    data, error_response_obj, status = validate_request_json()
    if error_response_obj:
        return error_response_obj, status
    
    user = get_current_user()
    if not user:
        return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
    
    errors = []
    quote_id = data.get('quote_id')
    if not quote_id:
        errors.append({"loc": ["quote_id"], "msg": "Quote ID is required", "type": "value_error"})
    if errors:
        return validation_error_response(errors)
    
    shipment = Shipment.objects(id=quote_id, supplier_id=user.id, status='quoted').first()
    if not shipment:
        return error_response("Not Found", "Quote not found or not available", "quotes", True, status_code=404)
    
    shipment.status = 'booked'
    shipment.quote_status = 'accepted'
    shipment.forwarder_id = shipment.quote_forwarder_id
    shipment.save()
    return success_response(shipment.to_dict())