# Gemini AI Prompt: Generate Test Invoice

Use this prompt with Gemini AI (Gemini Pro or Gemini 1.5 Pro) to generate a realistic test invoice document that satisfies all requirements for the document upload endpoint.

## Prompt for Gemini AI

```
Create a realistic commercial invoice document as a PDF or image that includes all the following fields clearly visible and extractable:

**Required Invoice Fields:**

1. **Invoice Number**: A unique invoice number (e.g., "INV-2024-001" or "INV-2025-1234")

2. **Date**: Invoice date in format DD/MM/YYYY or DD-MM-YYYY (e.g., "28/12/2024" or "2024-12-28")

3. **Company Name / Seller Information**:
   - Seller Company Name (e.g., "ABC Trading Co. Ltd" or "XYZ Exporters Inc")
   - Seller Address
   - Seller Contact Information
   - GSTIN/Tax ID (if applicable)

4. **Buyer Information**:
   - Buyer Company Name (e.g., "DEF Imports LLC" or "Global Trading Solutions")
   - Buyer Address
   - Buyer Contact Information

5. **Purchase Order (PO) Number**: A PO reference number (e.g., "PO-2024-5678" or "PUR-12345")

6. **Items/Line Items**: A table with at least 3-5 items containing:
   - Item Description (e.g., "Electronic Components", "Textile Goods", "Machinery Parts")
   - Quantity (numbers like 100, 50, 25)
   - Unit Price (currency amount per unit)
   - Total Price (quantity × unit price)
   - HSN Code / HS Code (e.g., "1234.56.78" or "9876.54.32")

7. **Financial Details**:
   - Subtotal Amount (before tax)
   - Tax Amount (e.g., GST, VAT, Sales Tax - should be a percentage like 10%, 18%, etc.)
   - Total Amount (subtotal + tax)
   - Currency (clearly stated as "USD", "EUR", "INR", etc.)

8. **Payment Terms**: 
   - Payment terms (e.g., "Net 30", "Net 45", "Due on Receipt", "50% Advance, 50% on Delivery")
   - Due Date (e.g., "Due Date: 28/01/2025" or "Payment Due: 30 days from invoice date")

9. **Summary/Notes Section**:
   - A brief summary or description of the transaction
   - Any additional notes or terms and conditions
   - Shipping terms (e.g., "FOB Mumbai", "CIF New York", "EXW")

10. **Additional Details**:
    - Invoice should look professional and realistic
    - Use clear, readable fonts
    - Include proper formatting with headers, tables, and footers
    - Make sure all numbers are clearly visible
    - Include a signature line or "Authorized Signatory" section

**Format Requirements:**
- Create as a PDF document OR high-resolution image (PNG/JPG)
- Ensure all text is OCR-readable
- Use standard invoice layout (header with company logo area, body with items table, footer with totals)
- Make it look like a real commercial invoice from a trading/export company

**Example Structure:**
```
┌─────────────────────────────────────────┐
│  [Company Logo Area]                    │
│  SELLER COMPANY NAME                    │
│  Address, City, Country                 │
│  GSTIN: XX1234567890                    │
│  Phone: +1-234-567-8900                 │
├─────────────────────────────────────────┤
│  INVOICE                                │
│  Invoice No: INV-2024-001               │
│  Date: 28/12/2024                       │
│  PO Number: PO-2024-5678                │
├─────────────────────────────────────────┤
│  BILL TO:                               │
│  Buyer Company Name                     │
│  Buyer Address                          │
│  City, Country                          │
├─────────────────────────────────────────┤
│  ITEMS DESCRIPTION | QTY | PRICE | TOTAL│
│  ───────────────────────────────────────│
│  Item 1 Description | 100 | $10 | $1000│
│  HSN: 1234.56.78                        │
│  ───────────────────────────────────────│
│  Item 2 Description | 50  | $25 | $1250│
│  HSN: 9876.54.32                        │
│  ───────────────────────────────────────│
│  Subtotal:                    $2,250.00│
│  Tax (10%):                    $225.00 │
│  Total Amount:               $2,475.00 │
│  Currency: USD                          │
├─────────────────────────────────────────┤
│  Payment Terms: Net 30                  │
│  Due Date: 28/01/2025                  │
│  Shipping Terms: FOB Mumbai             │
├─────────────────────────────────────────┤
│  Notes:                                 │
│  This invoice is for export of goods   │
│  as per purchase order PO-2024-5678    │
│  ───────────────────────────────────────│
│  Authorized Signatory                   │
│  [Signature Line]                       │
└─────────────────────────────────────────┘
```

Generate this invoice document now.
```

## Alternative Shorter Prompt

If the above is too long, use this concise version:

```
Create a professional commercial invoice PDF or image with:
- Invoice number: INV-2024-001
- Date: 28/12/2024
- Seller: ABC Trading Co. Ltd, Mumbai, India, GSTIN: 29ABCDE1234F1Z5
- Buyer: DEF Imports LLC, New York, USA
- PO Number: PO-2024-5678
- Items table: 3-5 items with description, quantity, unit price, total, HSN code
- Subtotal, Tax (10%), Total Amount in USD
- Payment Terms: Net 30, Due Date: 28/01/2025
- Shipping Terms: FOB Mumbai
- Notes section with transaction summary
Make it look realistic and professional with proper formatting.
```

## Testing Checklist

After generating the invoice, verify it contains:

- [ ] Unique invoice number
- [ ] Invoice date
- [ ] Seller company name and details
- [ ] Buyer company name and details
- [ ] PO number
- [ ] Items table with at least 3 items
- [ ] HSN/HS codes for items
- [ ] Subtotal amount
- [ ] Tax amount and percentage
- [ ] Total amount
- [ ] Currency clearly stated
- [ ] Payment terms
- [ ] Due date
- [ ] Summary/notes section
- [ ] Shipping terms (FOB/CIF/etc.)

## Usage with Gemini API

If using Gemini API programmatically:

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

prompt = """
Create a professional commercial invoice PDF or image with:
- Invoice number: INV-2024-001
- Date: 28/12/2024
- Seller: ABC Trading Co. Ltd, Mumbai, India, GSTIN: 29ABCDE1234F1Z5
- Buyer: DEF Imports LLC, New York, USA
- PO Number: PO-2024-5678
- Items table: 3-5 items with description, quantity, unit price, total, HSN code
- Subtotal, Tax (10%), Total Amount in USD
- Payment Terms: Net 30, Due Date: 28/01/2025
- Shipping Terms: FOB Mumbai
- Notes section with transaction summary
Make it look realistic and professional with proper formatting.
"""

response = model.generate_content(prompt)
# Note: Gemini may generate text description. For actual PDF/image generation,
# you may need to use image generation models or convert the description to PDF.
```

## Manual Invoice Creation

If Gemini doesn't generate PDFs directly, you can:
1. Use the prompt to get a detailed invoice structure
2. Create the invoice manually using:
   - Microsoft Word/Google Docs
   - Canva or other design tools
   - Invoice generators online
   - Or use the example structure above as a template

## Sample Invoice Data for Manual Creation

Use this data to create a test invoice:

**Invoice Details:**
- Invoice Number: INV-2024-001
- Date: 28/12/2024
- PO Number: PO-2024-5678

**Seller:**
- Company: ABC Trading Co. Ltd
- Address: 123 Export Street, Mumbai 400001, India
- GSTIN: 29ABCDE1234F1Z5
- Phone: +91-22-1234-5678

**Buyer:**
- Company: DEF Imports LLC
- Address: 456 Import Avenue, New York, NY 10001, USA
- Phone: +1-212-555-1234

**Items:**
1. Electronic Components - Qty: 100, Unit Price: $10.00, Total: $1,000.00, HSN: 8541.40.90
2. Textile Goods - Qty: 50, Unit Price: $25.00, Total: $1,250.00, HSN: 5208.11.00
3. Machinery Parts - Qty: 25, Unit Price: $40.00, Total: $1,000.00, HSN: 8481.80.90

**Financials:**
- Subtotal: $3,250.00
- Tax (10%): $325.00
- Total: $3,575.00
- Currency: USD

**Terms:**
- Payment Terms: Net 30
- Due Date: 28/01/2025
- Shipping Terms: FOB Mumbai
- Notes: Export invoice for goods shipped as per purchase order PO-2024-5678. All goods are in compliance with export regulations.

