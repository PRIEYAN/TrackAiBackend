from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from bson import ObjectId
from app.models.document import DocumentModel, ExtractionJob
from app.models.shipment import Shipment
from app.utils.auth import get_current_user
from app.services.storage_service import StorageService
from app.services.ai_service import AIService
from app.views.response_formatter import success_response, error_response
import os
import uuid
import requests
from datetime import datetime

document_bp = Blueprint('document', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_MIME_TYPES = {'application/pdf', 'image/png', 'image/jpeg', 'image/jpg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
@document_bp.route('/uploadInvoice', methods=['POST'])
@jwt_required()
def upload_invoice():
    temp_path = None
    try:
        shipment_id = request.form.get("shipment_id")
        if not shipment_id:
            return error_response("Missing field", "shipment_id is required", "documents", True, 400)

        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, 404)

        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, 401)

        file = request.files.get("file")
        if not file:
            return error_response("Missing file", "Invoice file is required", "documents", True, 400)

        if file.filename == '':
            return error_response("Invalid input", "No file selected", "documents", True, 400)

        if not allowed_file(file.filename):
            return error_response("Invalid input", "Invalid file type. Allowed: PDF, JPEG, PNG", "documents", True, 400)

        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        os.makedirs(upload_folder, exist_ok=True)
        temp_path = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)

        storage_service = StorageService()
        storage_path = storage_service.generate_document_path(shipment_id, filename)
        file_url = storage_service.upload_file(temp_path, storage_path)

        if not file_url:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return error_response("Internal Server Error", "Failed to upload file to storage", "documents", False, 500)

        ai_service = AIService()
        extracted_data, confidence, method = ai_service.extract_document_data(temp_path, "invoice")

        invoice_data = {
            "invoice_number": extracted_data.get("invoice_number") if extracted_data else None,
            "invoice_date": extracted_data.get("date") if extracted_data else None,
            "buyer_name": extracted_data.get("buyer_name") if extracted_data else None,
            "seller_name": extracted_data.get("seller_name") if extracted_data else None,
            "hsn_code": extracted_data.get("hs_code") if extracted_data else None,
            "total_amount": extracted_data.get("amount") if extracted_data else None,
            "currency": extracted_data.get("currency") if extracted_data else None,
            "tax_amount": extracted_data.get("tax_amount") if extracted_data else None,
            "extracted_raw": extracted_data
        }

        invoice_details = {
            "unique_invoice_number": extracted_data.get("invoice_number") if extracted_data else None,
            "company_name": extracted_data.get("company_name") or extracted_data.get("seller_name") if extracted_data else None,
            "buyer_company_name": extracted_data.get("buyer_name") if extracted_data else None,
            "seller_company_name": extracted_data.get("seller_name") if extracted_data else None,
            "summary": extracted_data.get("summary") if extracted_data else None,
            "date_of_invoice": extracted_data.get("date") if extracted_data else None,
            "payment_terms": extracted_data.get("payment_terms") if extracted_data else None,
            "due_date": extracted_data.get("due_date") if extracted_data else None,
            "po_number": extracted_data.get("po_number") if extracted_data else None,
            "total_amount": extracted_data.get("amount") if extracted_data else None,
            "currency": extracted_data.get("currency") if extracted_data else None,
            "tax_amount": extracted_data.get("tax_amount") if extracted_data else None,
            "items": extracted_data.get("items") if extracted_data else None,
            "notes": extracted_data.get("notes") if extracted_data else None,
            "extracted_at": datetime.utcnow().isoformat(),
            "confidence": confidence
        }

        if not shipment.metadata:
            shipment.metadata = {}
        shipment.metadata['invoice_details'] = invoice_details
        shipment.save()

        mime_type = file.content_type or 'application/octet-stream'
        file_size = os.path.getsize(temp_path)

        document = DocumentModel(
            shipment_id=shipment,
            uploaded_by=user,
            type="invoice",
            file_name=filename,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            extracted_data=invoice_data,
            confidence_score=confidence,
            extraction_method=method,
            needs_review=confidence < 0.8
        )
        document.save()

        extraction_job = ExtractionJob(
            document_id=document,
            status='completed' if extracted_data else 'failed'
        )
        extraction_job.save()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        return success_response(
            "Invoice uploaded and processed",
            {
                "file_url": file_url,
                "extracted_data": invoice_data,
                "invoice_details": invoice_details,
                "confidence": confidence,
                "document_id": str(document.id),
                "shipment_id": str(shipment.id)
            }
        )
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return error_response("Internal Server Error", str(e), "documents", False, 500)

@document_bp.route('/shipments/<shipment_id>/upload', methods=['POST'])
@jwt_required()
def upload_document(shipment_id):
    temp_path = None
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", "User not found", "auth", True, status_code=401)
        
        if 'file' not in request.files:
            return error_response("Invalid input", "No file provided", "documents", True, status_code=400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response("Invalid input", "No file selected", "documents", True, status_code=400)
        
        if not allowed_file(file.filename):
            return error_response("Invalid input", "Invalid file type. Allowed: PDF, JPEG, PNG", "documents", True, status_code=400)
        
        document_type = request.form.get('document_type', 'invoice')
        valid_types = ['invoice', 'packing_list', 'commercial_invoice', 'certificate_of_origin', 
                      'bill_of_lading', 'house_bl', 'master_bl', 'telex_release', 'other']
        if document_type not in valid_types:
            document_type = 'invoice'
        
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        os.makedirs(upload_folder, exist_ok=True)
        temp_path = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
        file.save(temp_path)
        
        storage_service = StorageService()
        storage_path = storage_service.generate_document_path(shipment_id, filename)
        file_url = storage_service.upload_file(temp_path, storage_path)
        
        if not file_url:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return error_response("Internal Server Error", "Failed to upload file to storage", "documents", False, status_code=500)
        
        mime_type = file.content_type or 'application/octet-stream'
        file_size = os.path.getsize(temp_path)
        
        document = DocumentModel(
            shipment_id=shipment,
            uploaded_by=user,
            type=document_type,
            file_name=filename,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type
        )
        document.save()
        
        extraction_job = ExtractionJob(
            document_id=document,
            status='pending'
        )
        extraction_job.save()
        
        from threading import Thread
        thread = Thread(target=process_document_extraction, args=(str(document.id), temp_path))
        thread.start()
        
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        return success_response(document.to_dict(), status_code=200)
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return error_response("Internal Server Error", str(e), "documents", False, status_code=500)


def process_document_extraction(document_id: str, file_path: str):
    from app import create_app
    app = create_app()
    with app.app_context():
        try:
            document = DocumentModel.objects(id=document_id).first()
            if not document:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                return
            
            ai_service = AIService()
            extracted_data, confidence, method = ai_service.extract_document_data(file_path, document.type)
            
            document.extracted_data = extracted_data
            document.confidence_score = confidence
            document.extraction_method = method
            document.needs_review = confidence < 0.8
            document.save()
            
            extraction_job = ExtractionJob.objects(document_id=document).first()
            if extraction_job:
                extraction_job.status = 'completed' if extracted_data else 'failed'
                extraction_job.save()
        except Exception as e:
            try:
                document = DocumentModel.objects(id=document_id).first()
                if document:
                    extraction_job = ExtractionJob.objects(document_id=document).first()
                    if extraction_job:
                        extraction_job.status = 'failed'
                        extraction_job.error_message = str(e)
                        extraction_job.save()
            except:
                pass
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)


@document_bp.route('/shipments/<shipment_id>/list', methods=['GET'])
@jwt_required()
def get_shipment_documents(shipment_id):
    try:
        try:
            shipment = Shipment.objects(id=shipment_id).first()
        except:
            shipment = None
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        documents = DocumentModel.objects(shipment_id=shipment).all()
        return success_response([doc.to_dict() for doc in documents], status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@document_bp.route('/<document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    try:
        document = DocumentModel.objects(id=document_id).first()
        if not document:
            return error_response("Not Found", "Document not found", "documents", True, status_code=404)
        
        return success_response(document.to_dict(), status_code=200)
    except Exception as e:
        return error_response("Service Unavailable", f"Database error: {str(e)}", "database", True, status_code=503)


@document_bp.route('/<document_id>/extract', methods=['POST'])
@jwt_required()
def extract_document(document_id):
    return error_response("Not Implemented", "Extraction from stored files not implemented", "documents", True, status_code=501)


@document_bp.route('/<document_id>/autofill', methods=['POST'])
@jwt_required()
def autofill_shipment(document_id):
    try:
        document = DocumentModel.objects(id=document_id).first()
        if not document:
            return error_response("Not Found", "Document not found", "documents", True, status_code=404)
        
        if not document.extracted_data:
            return error_response("Bad Request", "Document has no extracted data", "documents", True, status_code=400)
        
        shipment = document.shipment_id
        if not shipment:
            return error_response("Not Found", "Shipment not found", "documents", True, status_code=404)
        
        data = request.get_json() or {}
        fields = data.get('fields', ['gross_weight_kg', 'net_weight_kg', 'volume_cbm', 
                                     'total_packages', 'hs_code', 'goods_description'])
        
        extracted = document.extracted_data
        updated_fields = []
        extracted_values = {}
        
        field_mapping = {
            'gross_weight_kg': ['total_weight_kg', 'gross_weight', 'weight_kg'],
            'net_weight_kg': ['net_weight', 'net_weight_kg'],
            'volume_cbm': ['volume_cbm', 'volume', 'total_volume'],
            'total_packages': ['total_packages', 'packages', 'quantity'],
            'hs_code': ['hs_code', 'hscode', 'harmonized_code'],
            'goods_description': ['description', 'goods_description', 'item_description']
        }
        
        for field in fields:
            if field in field_mapping:
                for key in field_mapping[field]:
                    if key in extracted:
                        value = extracted[key]
                        if value:
                            setattr(shipment, field, value)
                            updated_fields.append(field)
                            extracted_values[field] = value
                            break
        
        shipment.save()
        
        return success_response({
            "document_id": str(document.id),
            "shipment_id": str(shipment.id),
            "updated_fields": updated_fields,
            "confidence": document.confidence_score,
            "extracted_values": extracted_values
        }, status_code=200)
    except Exception as e:
        return error_response("Internal Server Error", str(e), "documents", False, status_code=500)
