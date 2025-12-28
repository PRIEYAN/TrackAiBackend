import google.generativeai as genai
from app.config import Config
from typing import Optional, Dict, Any
import time
import base64
import os


class AIService:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.enabled = Config.ENABLE_AI_EXTRACTION
        else:
            self.enabled = False
    
    def extract_document_data(self, file_path: str, document_type: str) -> tuple[Optional[Dict[str, Any]], float, str]:
        if not self.enabled:
            return None, 0.0, "ai_disabled"
        
        try:
            start_time = time.time()
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            mime_type = self._get_mime_type(file_path)
            
            prompt = self._get_extraction_prompt(document_type)
            
            file_part = {
                "mime_type": mime_type,
                "data": file_data
            }
            
            response = model.generate_content([prompt, file_part])
            
            processing_time = int((time.time() - start_time) * 1000)
            
            extracted_data = self._parse_response(response.text)
            confidence = self._calculate_confidence(extracted_data)
            
            return extracted_data, confidence, "gemini-1.5-pro"
        except Exception as e:
            print(f"AI extraction error: {str(e)}")
            return None, 0.0, "error"
    
    def detect_document_type(self, file_path: str) -> tuple[str, float]:
        if not self.enabled:
            return "other", 0.0
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            mime_type = self._get_mime_type(file_path)
            
            prompt = """Analyze this document and determine its type. 
            Return only one of: invoice, packing_list, commercial_invoice, certificate_of_origin, 
            bill_of_lading, house_bl, master_bl, telex_release, or other.
            Response format: TYPE|CONFIDENCE (0.0-1.0)"""
            
            file_part = {
                "mime_type": mime_type,
                "data": file_data
            }
            
            response = model.generate_content([prompt, file_part])
            result = response.text.strip().split('|')
            
            if len(result) == 2:
                doc_type = result[0].strip().lower()
                confidence = float(result[1].strip())
                return doc_type, confidence
            
            return "other", 0.5
        except Exception:
            return "other", 0.0
    
    def predict_customs_delay(self, port: str, rms_examination: bool, duty_amount: float, 
                             documents_complete: bool) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "delayRisk": "MEDIUM",
                "predictedDelayDays": 3,
                "confidenceScore": 0.5,
                "reasons": ["AI service not available"],
                "recommendation": "Please ensure all documents are complete"
            }
        
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = f"""Analyze customs clearance delay risk for:
            Port: {port}
            RMS Examination: {rms_examination}
            Duty Amount: ${duty_amount}
            Documents Complete: {documents_complete}
            
            Return JSON format:
            {{
                "delayRisk": "LOW|MEDIUM|HIGH",
                "predictedDelayDays": <integer>,
                "confidenceScore": <float 0.0-1.0>,
                "reasons": ["reason1", "reason2"],
                "recommendation": "string"
            }}"""
            
            response = model.generate_content(prompt)
            import json
            return json.loads(response.text)
        except Exception:
            return {
                "delayRisk": "MEDIUM",
                "predictedDelayDays": 3,
                "confidenceScore": 0.5,
                "reasons": ["Analysis unavailable"],
                "recommendation": "Please ensure all documents are complete"
            }
    
    def predict_rate(self, origin: str, destination: str, carrier: str, 
                     container_type: str, current_rate: float) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "predictedRateUSD": current_rate,
                "trend": "STABLE",
                "confidenceScore": 0.5,
                "recommendation": "AI service not available"
            }
        
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = f"""Predict freight rate trend for:
            Origin: {origin}
            Destination: {destination}
            Carrier: {carrier}
            Container Type: {container_type}
            Current Rate: ${current_rate}
            
            Return JSON format:
            {{
                "predictedRateUSD": <float>,
                "trend": "UP|DOWN|STABLE",
                "confidenceScore": <float 0.0-1.0>,
                "recommendation": "string"
            }}"""
            
            response = model.generate_content(prompt)
            import json
            return json.loads(response.text)
        except Exception:
            return {
                "predictedRateUSD": current_rate,
                "trend": "STABLE",
                "confidenceScore": 0.5,
                "recommendation": "Analysis unavailable"
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _get_extraction_prompt(self, document_type: str) -> str:
        base_prompt = """Extract structured data from this document. Return JSON format with relevant fields."""
        
        prompts = {
            "invoice": base_prompt + """ Fields: invoice_number, date, amount, currency, items (array with description, quantity, unit_price, total), buyer_name, seller_name, tax_amount, payment_terms, summary, company_name, due_date, po_number, notes.""",
            "packing_list": base_prompt + """ Fields: packing_list_number, date, total_packages, total_weight_kg, total_volume_cbm, items (array with description, quantity, weight_kg, volume_cbm, hs_code).""",
            "commercial_invoice": base_prompt + """ Fields: invoice_number, date, exporter, importer, items (array with description, quantity, unit_price, total, hs_code), total_amount, currency, incoterm.""",
            "certificate_of_origin": base_prompt + """ Fields: certificate_number, issue_date, exporter, importer, origin_country, items (array with description, hs_code).""",
            "bill_of_lading": base_prompt + """ Fields: bl_number, shipper, consignee, notify_party, vessel_name, voyage_number, port_of_loading, port_of_discharge, container_numbers (array), packages, weight_kg, volume_cbm.""",
        }
        
        return prompts.get(document_type, base_prompt)
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        import json
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
        except Exception:
            pass
        return {}
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        if not extracted_data:
            return 0.0
        required_fields = ['invoice_number', 'date', 'amount']
        found_fields = sum(1 for field in required_fields if field in extracted_data)
        return min(found_fields / len(required_fields), 0.95)

