# PDF/A-3 Converter Server

A Python Flask server that converts regular PDFs to PDF/A-3 format with embedded XML attachments, designed for electronic invoice compliance.

## Features

- Convert PDF to PDF/A-3 format with proper compliance
- Embed XML files as attachments in PDF/A-3 documents  
- Base64 input/output support for easy API integration
- Multiple endpoints for conversion and file download
- Dynamic processing with configurable data inputs
- Web-based test interface for easy testing

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python app.py
   ```
   
   Server will start on `http://localhost:8080`

3. **Open test interface:**
   Navigate to `http://localhost:8080/test.html` in your browser

## API Endpoints

### 1. `/convert-pdf-a3` (POST)
Convert PDF to PDF/A-3 with XML attachment and return base64 response.

**Request:**
```json
{
  "sequence_no": "INV001",
  "pdf_base64": "JVBERi0xLjQK...",
  "xml_base64": "PD94bWwgdmVyc2lvbj0i..."
}
```

**Response:**
```json
{
  "success": true,
  "sequence_no": "INV001", 
  "pdf_a3_base64": "JVBERi0xLjcK...",
  "message": "PDF/A-3 conversion successful",
  "original_pdf_size": 12345,
  "xml_size": 5678,
  "pdf_a3_size": 15432,
  "attachment_filename": "invoice_INV001.xml"
}
```

### 2. `/test-sample` (POST)
Test conversion using data from `sampledata.json` file.

### 3. `/convert-and-download` (POST)
Convert PDF to PDF/A-3 and download the file directly.

### 4. `/download-pdf` (POST)
Download any PDF from base64 data.

### 5. `/health` (GET)
Health check endpoint.

## Sample Data Format

The `sampledata.json` file contains sample PDF and XML data for testing:
```json
{
  "sequence_no": "test1",
  "pdf_base64": "JVBERi0xLjQK...",
  "xml_base64": "PD94bWwgdmVyc2lvbj0i..."
}
```

## Testing

1. **Using the Web Interface:**
   - Open `http://localhost:8080/test.html`
   - Click "Test Sample Data" to test with included sample data
   - Or manually input your own PDF and XML base64 data

2. **Using curl:**
   ```bash
   # Test with sample data
   curl -X POST http://localhost:8080/test-sample
   
   # Manual conversion
   curl -X POST http://localhost:8080/convert-pdf-a3 \
     -H "Content-Type: application/json" \
     -d @sampledata.json
   ```

## PDF/A-3 Compliance Features

✅ **PDF Version 1.7** structure  
✅ **XMP Metadata** with PDF/A-3 identification  
✅ **Embedded File Streams** with proper parameters  
✅ **Associated Files (AF)** array for attachments  
✅ **Names Tree** structure for file specifications  
✅ **Accessibility Markers** (MarkInfo)  
✅ **Document Structure Tree**  
✅ **Checksum Validation**