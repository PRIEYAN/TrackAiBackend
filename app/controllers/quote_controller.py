from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.quote import Quote
from app.models.shipment import Shipment
from app.utils.auth import get_current_user, require_role
from app.utils.validators import validate_request_json
from app.views.response_formatter import success_response, error_response, validation_error_response
from datetime import datetime

quote_bp = Blueprint('quote', __name__)


@quote_bp.route('/shipments/<shipment_id>/quotes', methods=['GET'])
@jwt_required()
def get_shipment_quotes(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "quotes", True, status_code=404)
        
        quotes = Quote.objects(shipment_id=shipment).all()
        return success_response([quote.to_dict(include_forwarder_info=True) for quote in quotes], status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@quote_bp.route('/shipments/<shipment_id>/accept-quote', methods=['POST'])
@jwt_required()
def accept_quote(shipment_id):
    try:
        user = get_current_user()
        if not user or user.role != 'supplier':
            return error_response("Forbidden", "Only suppliers can accept quotes", "quotes", True, status_code=403)
        
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "quotes", True, status_code=404)
        
        if str(shipment.supplier_id.id) != str(user.id):
            return error_response("Forbidden", "Not authorized for this shipment", "quotes", True, status_code=403)
        
        quote_id = request.args.get('quote_id')
        if not quote_id:
            return error_response("Invalid input", "quote_id query parameter is required", "quotes", True, status_code=400)
        
        try:
            quote = Quote.objects(id=quote_id, shipment_id=shipment).first()
        except:
            quote = None
        if not quote:
            return error_response("Not Found", "Quote not found", "quotes", True, status_code=404)
        
        if quote.status != 'pending':
            return error_response("Bad Request", f"Quote already {quote.status}", "quotes", True, status_code=400)
        
        if quote.validity_date and quote.validity_date < datetime.utcnow():
            quote.status = 'expired'
            quote.save()
            return error_response("Bad Request", "Quote has expired", "quotes", True, status_code=400)
        
        quote.status = 'accepted'
        quote.save()
        shipment.status = 'booked'
        shipment.forwarder_id = quote.forwarder_id
        shipment.save()
        
        return success_response(quote.to_dict(include_forwarder_info=True), status_code=200)
    except Exception as e:
        return error_response("Internal Server Error", str(e), "quotes", False, status_code=500)


@quote_bp.route('/quotes/<quote_id>', methods=['PUT'])
@jwt_required()
def update_quote(quote_id):
    try:
        user = get_current_user()
        if not user or user.role != 'forwarder':
            return error_response("Forbidden", "Only forwarders can update quotes", "quotes", True, status_code=403)
        
        try:
            quote = Quote.objects(id=quote_id).first()
        except:
            quote = None
        if not quote:
            return error_response("Not Found", "Quote not found", "quotes", True, status_code=404)
        
        if str(quote.forwarder_id.id) != str(user.id):
            return error_response("Forbidden", "Not authorized for this quote", "quotes", True, status_code=403)
        
        data, error_response_obj, status = validate_request_json()
        if error_response_obj:
            return error_response_obj, status
        
        status_value = data.get('status')
        if status_value not in ['pending', 'rejected']:
            return error_response("Invalid input", "Status must be pending or rejected", "quotes", True, status_code=400)
        
        quote.status = status_value
        quote.remarks = data.get('remarks', quote.remarks)
        quote.save()
        
        return success_response(quote.to_dict(include_forwarder_info=True), status_code=200)
    except Exception as e:
        return error_response("Internal Server Error", str(e), "quotes", False, status_code=500)
