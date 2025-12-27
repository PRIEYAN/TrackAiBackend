# cURL Examples for TradeFlow AI API

## Registration

### Basic Registration (Supplier)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "supplier@example.com",
    "password": "password123",
    "name": "John Supplier",
    "phone": "+1234567890",
    "role": "supplier",
    "company_name": "ABC Trading Co",
    "gstin": "29ABCDE1234F1Z5",
    "country": "IN"
  }'
```

### Basic Registration (Forwarder)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "forwarder@example.com",
    "password": "password123",
    "name": "Jane Forwarder",
    "phone": "+1234567890",
    "role": "forwarder",
    "company_name": "XYZ Logistics",
    "country": "IN"
  }'
```

### Basic Registration (Buyer)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@example.com",
    "password": "password123",
    "name": "Bob Buyer",
    "phone": "+1234567890",
    "role": "buyer",
    "company_name": "DEF Imports",
    "country": "IN"
  }'
```

### Minimal Registration (Required fields only)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "Test User",
    "phone": "986532741",
    "role": "supplier"
  }'
```

## Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

## Get Current User / My Profile (Requires JWT Token)

**Using `/me` endpoint:**
```bash
curl -X GET http://localhost:8000/api/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Using `/my-profile` endpoint:**
```bash
curl -X GET http://localhost:8000/api/my-profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/my-profile -H "Authorization: Bearer YOUR_TOKEN"
```

## Create Shipment (Requires JWT Token - Supplier)

```bash
curl -X POST http://localhost:8000/api/shipments/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "origin_port": "Mumbai",
    "destination_port": "New York",
    "weight": 15000.5,
    "volume": 60.5
  }'
```

### One-liner

```bash
curl -X POST http://localhost:8000/api/shipments/create -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d '{"origin_port":"Mumbai","destination_port":"New York","weight":15000.5,"volume":60.5}'
```

## Get Shipment (Requires JWT Token)

```bash
curl -X GET http://localhost:8000/api/shipments/SHIPMENT_ID_HERE \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## List/Show Shipments (Requires JWT Token)

### Get All Shipments for Current User (Supplier)
This endpoint extracts the user ID from the bearer token and returns all shipments where the user is the supplier.

**Using `/list` endpoint:**
```bash
curl -X GET http://localhost:8000/api/shipments/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Using `/show` endpoint:**
```bash
curl -X GET http://localhost:8000/api/shipments/show \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Using `/show_shipments` endpoint:**
```bash
curl -X GET http://localhost:8000/api/shipments/show_shipments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Filter Shipments by Status
```bash
curl -X GET "http://localhost:8000/api/shipments/show_shipments?status=draft" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/shipments/show_shipments -H "Authorization: Bearer YOUR_TOKEN"
```

### Available Status Values
- `draft` - Shipment is in draft state
- `pending_quote` - Waiting for quotes
- `pending` - Pending action
- `quoted` - Quotes received
- `booked` - Shipment booked
- `in_transit` - Currently in transit
- `arrived` - Arrived at destination
- `delivered` - Delivered
- `cancelled` - Cancelled

**Note:** 
- For **suppliers**: Returns shipments where `supplier_id` matches the user ID from token
- For **buyers**: Returns shipments where `buyer_id` matches the user ID from token
- For **forwarders**: Returns shipments where `forwarder_id` matches the user ID from token

## Example: Register → Login → Get User Info

```bash
# 1. Register
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "phone": "+1234567890",
    "role": "supplier"
  }')

echo "Registration Response: $REGISTER_RESPONSE"

# 2. Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }')

echo "Login Response: $LOGIN_RESPONSE"

# Extract token (requires jq)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. Get user info
curl -X GET http://localhost:8000/api/me \
  -H "Authorization: Bearer $TOKEN"
```

## Forwarder Routes (Requires JWT Token - Forwarder Role)

### Show Available Shipments (Without Forwarder)
Get all shipments that don't have a forwarder assigned yet (available for bidding).

```bash
curl -X GET http://localhost:8000/api/forwarder/show-shipments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/forwarder/show-shipments -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Forwarder Profile
Get the current forwarder's profile information.

```bash
curl -X GET http://localhost:8000/api/forwarder/my-profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**One-liner:**
```bash
curl -X GET http://localhost:8000/api/forwarder/my-profile -H "Authorization: Bearer YOUR_TOKEN"
```

