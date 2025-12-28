# Document API cURL Examples

## Base URL
All endpoints use the base URL: `http://localhost:8000/api/documents`

**Note:** All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

---

## 1. Upload Invoice

Upload an invoice document for a shipment. The invoice will be automatically processed using AI extraction.

**Endpoint:** `POST /api/documents/uploadInvoice`

**Request:**
- Content-Type: `multipart/form-data`
- Required fields:
  - `shipment_id` (string) - The shipment ID to attach the invoice to
  - `file` (file) - The invoice file (PDF, JPEG, or PNG)

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/documents/uploadInvoice \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "shipment_id=SHIPMENT_ID_HERE" \
  -F "file=@/path/to/invoice.pdf"
```

**One-liner:**
```bash
curl -X POST http://localhost:8000/api/documents/uploadInvoice -H "Authorization: Bearer YOUR_TOKEN" -F "shipment_id=SHIPMENT_ID" -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Invoice uploaded and processed",
  "data": {
    "file_url": "https://storage.example.com/shipments/.../invoice.pdf",
    "extracted_data": {
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15",
      "buyer_name": "ABC Company",
      "seller_name": "XYZ Corp",
      "hsn_code": "1234.56.78",
      "total_amount": 10000.00,
      "currency": "USD",
      "tax_amount": 1000.00,
      "extracted_raw": {...}
    },
    "confidence": 0.95,
    "document_id": "DOCUMENT_ID_HERE"
  }
}
```

---

## 2. Upload Document

Upload any type of document for a shipment. Supports multiple document types.

**Endpoint:** `POST /api/documents/shipments/<shipment_id>/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Required fields:
  - `file` (file) - The document file (PDF, JPEG, or PNG)
- Optional fields:
  - `document_type` (string) - Type of document. Default: `invoice`
    - Valid types: `invoice`, `packing_list`, `commercial_invoice`, `certificate_of_origin`, `bill_of_lading`, `house_bl`, `master_bl`, `telex_release`, `other`

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/documents/shipments/SHIPMENT_ID_HERE/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "file=@/path/to/document.pdf" \
  -F "document_type=packing_list"
```

**Upload Packing List:**
```bash
curl -X POST http://localhost:8000/api/documents/shipments/SHIPMENT_ID_HERE/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "file=@packing_list.pdf" \
  -F "document_type=packing_list"
```

**Upload Bill of Lading:**
```bash
curl -X POST http://localhost:8000/api/documents/shipments/SHIPMENT_ID_HERE/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -F "file=@bill_of_lading.pdf" \
  -F "document_type=bill_of_lading"
```

**One-liner:**
```bash
curl -X POST http://localhost:8000/api/documents/shipments/SHIPMENT_ID/upload -H "Authorization: Bearer YOUR_TOKEN" -F "file=@document.pdf" -F "document_type=invoice"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "DOCUMENT_ID_HERE",
    "shipment_id": "SHIPMENT_ID_HERE",
    "uploaded_by": "USER_ID_HERE",
    "type": "packing_list",
    "file_name": "packing_list.pdf",
    "file_url": "https://storage.example.com/shipments/.../packing_list.pdf",
    "file_size": 245678,
    "mime_type": "application/pdf",
    "extracted_data": {...},
    "confidence_score": 0.92,
    "extraction_method": "gemini-1.5-pro",
    "needs_review": false,
    "metadata": {},
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## 3. Get Shipment Documents

Retrieve all documents associated with a specific shipment.

**Endpoint:** `GET /api/documents/shipments/<shipment_id>/list`

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/documents/shipments/SHIPMENT_ID_HERE/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/documents/shipments/SHIPMENT_ID/list -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "DOCUMENT_ID_1",
      "shipment_id": "SHIPMENT_ID_HERE",
      "type": "invoice",
      "file_name": "invoice.pdf",
      "file_url": "https://storage.example.com/...",
      "confidence_score": 0.95,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "DOCUMENT_ID_2",
      "shipment_id": "SHIPMENT_ID_HERE",
      "type": "packing_list",
      "file_name": "packing_list.pdf",
      "file_url": "https://storage.example.com/...",
      "confidence_score": 0.92,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

---

## 4. Get Document Details

Retrieve detailed information about a specific document.

**Endpoint:** `GET /api/documents/<document_id>`

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/documents/DOCUMENT_ID_HERE \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/documents/DOCUMENT_ID -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "DOCUMENT_ID_HERE",
    "shipment_id": "SHIPMENT_ID_HERE",
    "uploaded_by": "USER_ID_HERE",
    "type": "invoice",
    "file_name": "invoice.pdf",
    "file_url": "https://storage.example.com/shipments/.../invoice.pdf",
    "file_size": 245678,
    "mime_type": "application/pdf",
    "extracted_data": {
      "invoice_number": "INV-2024-001",
      "date": "2024-01-15",
      "amount": 10000.00,
      "currency": "USD",
      "items": [...],
      "buyer_name": "ABC Company",
      "seller_name": "XYZ Corp",
      "tax_amount": 1000.00
    },
    "confidence_score": 0.95,
    "extraction_method": "gemini-1.5-pro",
    "needs_review": false,
    "metadata": {},
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## 5. Extract Document (Re-extract)

Re-extract data from a stored document. Currently returns 501 Not Implemented.

**Endpoint:** `POST /api/documents/<document_id>/extract`

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID_HERE/extract \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID/extract -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": false,
  "error": "Not Implemented",
  "reason": "Extraction from stored files not implemented",
  "module": "documents",
  "safe_for_demo": true
}
```

---

## 6. Autofill Shipment from Document

Automatically fill shipment fields using extracted data from a document.

**Endpoint:** `POST /api/documents/<document_id>/autofill`

**Request:**
- Content-Type: `application/json`
- Optional fields:
  - `fields` (array) - List of fields to autofill. Default: `["gross_weight_kg", "net_weight_kg", "volume_cbm", "total_packages", "hs_code", "goods_description"]`
    - Valid fields: `gross_weight_kg`, `net_weight_kg`, `volume_cbm`, `total_packages`, `hs_code`, `goods_description`

**cURL Example (All Fields):**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID_HERE/autofill \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "fields": ["gross_weight_kg", "net_weight_kg", "volume_cbm", "total_packages", "hs_code", "goods_description"]
  }'
```

**cURL Example (Specific Fields):**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID_HERE/autofill \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "fields": ["gross_weight_kg", "volume_cbm", "hs_code"]
  }'
```

**cURL Example (Default Fields - Empty Body):**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID_HERE/autofill \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{}'
```

**One-liner:**
```bash
curl -X POST http://localhost:8000/api/documents/DOCUMENT_ID/autofill -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"fields":["gross_weight_kg","volume_cbm"]}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "document_id": "DOCUMENT_ID_HERE",
    "shipment_id": "SHIPMENT_ID_HERE",
    "updated_fields": ["gross_weight_kg", "volume_cbm", "hs_code"],
    "confidence": 0.95,
    "extracted_values": {
      "gross_weight_kg": 15000.5,
      "volume_cbm": 60.5,
      "hs_code": "1234.56.78"
    }
  }
}
```

---

## Complete Workflow Example

```bash
# 1. Login to get token
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# 2. Create a shipment (if needed)
SHIPMENT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/shipments/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "origin_port": "Mumbai",
    "destination_port": "New York",
    "weight": 15000.5,
    "volume": 60.5
  }')

SHIPMENT_ID=$(echo $SHIPMENT_RESPONSE | jq -r '.data.id')
echo "Shipment ID: $SHIPMENT_ID"

# 3. Upload invoice
curl -X POST http://localhost:8000/api/documents/uploadInvoice \
  -H "Authorization: Bearer $TOKEN" \
  -F "shipment_id=$SHIPMENT_ID" \
  -F "file=@invoice.pdf"

# 4. Upload packing list
curl -X POST http://localhost:8000/api/documents/shipments/$SHIPMENT_ID/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@packing_list.pdf" \
  -F "document_type=packing_list"

# 5. Get all documents for shipment
curl -X GET http://localhost:8000/api/documents/shipments/$SHIPMENT_ID/list \
  -H "Authorization: Bearer $TOKEN"

# 6. Autofill shipment from document
DOCUMENT_ID="DOCUMENT_ID_FROM_STEP_3"
curl -X POST http://localhost:8000/api/documents/$DOCUMENT_ID/autofill \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "fields": ["gross_weight_kg", "volume_cbm", "hs_code"]
  }'
```

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error Title",
  "reason": "Detailed error message",
  "module": "documents",
  "safe_for_demo": true
}
```

**Common Status Codes:**
- `400` - Bad Request (missing fields, invalid input)
- `401` - Unauthorized (invalid or missing token)
- `404` - Not Found (shipment or document not found)
- `500` - Internal Server Error
- `501` - Not Implemented

---

## Notes

- **File Types:** Supported file types are PDF, JPEG, and PNG
- **File Size:** Maximum file size is 16MB
- **AI Extraction:** Document extraction happens automatically in the background after upload
- **Confidence Score:** Documents with confidence < 0.8 are flagged for review (`needs_review: true`)
- **Document Types:** Use appropriate document types for better extraction accuracy
- **Authentication:** All endpoints require a valid JWT token obtained from `/api/auth/login`

