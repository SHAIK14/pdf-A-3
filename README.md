# PDF/A-3 Conversion Server

A lightweight Python Flask server that converts regular PDFs to PDF/A-3 compliant documents with embedded XML attachments.

## Features

- ✅ Converts PDF to PDF/A-3B compliant format
- ✅ Embeds XML files as attachments  
- ✅ Adds proper XMP metadata for compliance
- ✅ RESTful API with JSON responses
- ✅ Base64 encoding/decoding support
- ✅ Docker support for easy deployment

## API Usage

### Convert PDF to PDF/A-3

**Endpoint:** `POST /convert-pdf-a3`

**Request Body:**
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
  "message": "PDF/A-3 conversion successful"
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

## Deployment

### Local Development
```bash
pip install -r requirements.txt
python app.py
```

### Docker
```bash
docker build -t pdf-a3-server .
docker run -p 8080:8080 pdf-a3-server
```

### Cloud Platforms
- Deploy on Render.com, Railway.app, or Heroku
- Uses PORT environment variable for cloud deployment
- Dockerfile included for containerized deployment

## PDF/A-3 Compliance

✅ **PDF Version 1.7**  
✅ **XMP Metadata** with PDF/A-3B conformance  
✅ **Accessibility** markup and structure  
✅ **XML Attachments** with proper relationships  
✅ **Document Structure** for screen readers  
✅ **Error Handling** for invalid inputs