from flask import Flask, request, jsonify, send_file
import base64
import logging
import json
import io
import os
from utils.pdf_converter import PDFConverter

app = Flask(__name__, static_folder='.', static_url_path='')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for development
try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    print("Warning: flask-cors not installed. Install with: pip install flask-cors")

@app.route('/convert-pdf-a3', methods=['POST'])
def convert_pdf_a3():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        required_fields = ['sequence_no', 'pdf_base64', 'xml_base64']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        sequence_no = data['sequence_no']
        pdf_base64 = data['pdf_base64']
        xml_base64 = data['xml_base64']
        
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            xml_bytes = base64.b64decode(xml_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Invalid base64 encoding: {str(e)}'
            }), 400
        
        converter = PDFConverter()
        pdf_a3_bytes = converter.convert_to_pdf_a3(pdf_bytes, xml_bytes, sequence_no)
        
        pdf_a3_base64 = base64.b64encode(pdf_a3_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'sequence_no': sequence_no,
            'pdf_a3_base64': pdf_a3_base64,
            'message': 'PDF/A-3 conversion successful',
            'original_pdf_size': len(pdf_bytes),
            'xml_size': len(xml_bytes),
            'pdf_a3_size': len(pdf_a3_bytes),
            'attachment_filename': f'invoice_{sequence_no}.xml'
        })
        
    except Exception as e:
        logger.error(f'Conversion error: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Conversion failed: {str(e)}'
        }), 500

@app.route('/test-sample', methods=['POST'])
def test_sample():
    """Test endpoint using sample data from sampledata.json"""
    try:
        # Load sample data
        with open('sampledata.json', 'r') as f:
            data = json.load(f)
        
        sequence_no = data['sequence_no']
        pdf_base64 = data['pdf_base64']
        xml_base64 = data['xml_base64']
        
        # Decode base64 data
        pdf_bytes = base64.b64decode(pdf_base64)
        xml_bytes = base64.b64decode(xml_base64)
        
        # Convert to PDF/A-3
        converter = PDFConverter()
        pdf_a3_bytes = converter.convert_to_pdf_a3(pdf_bytes, xml_bytes, sequence_no)
        
        # Encode result to base64
        pdf_a3_base64 = base64.b64encode(pdf_a3_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'sequence_no': sequence_no,
            'pdf_a3_base64': pdf_a3_base64,
            'message': 'PDF/A-3 conversion successful using sample data',
            'original_pdf_size': len(pdf_bytes),
            'xml_size': len(xml_bytes),
            'pdf_a3_size': len(pdf_a3_bytes)
        })
        
    except Exception as e:
        logger.error(f'Sample test error: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Sample test failed: {str(e)}'
        }), 500

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Decode base64 PDF and provide download"""
    try:
        data = request.get_json()
        
        if not data or 'pdf_base64' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing pdf_base64 field'
            }), 400
        
        pdf_base64 = data['pdf_base64']
        filename = data.get('filename', 'document.pdf')
        
        # Ensure filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Decode base64 PDF
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Invalid base64 encoding: {str(e)}'
            }), 400
        
        # Create BytesIO object for download
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f'PDF download error: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'PDF download failed: {str(e)}'
        }), 500

@app.route('/convert-and-download', methods=['POST'])
def convert_and_download():
    """Convert to PDF/A-3 and provide download"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        required_fields = ['sequence_no', 'pdf_base64', 'xml_base64']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        sequence_no = data['sequence_no']
        pdf_base64 = data['pdf_base64']
        xml_base64 = data['xml_base64']
        filename = data.get('filename', f'invoice_{sequence_no}_pdfa3.pdf')
        
        # Ensure filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            xml_bytes = base64.b64decode(xml_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Invalid base64 encoding: {str(e)}'
            }), 400
        
        # Convert to PDF/A-3
        converter = PDFConverter()
        pdf_a3_bytes = converter.convert_to_pdf_a3(pdf_bytes, xml_bytes, sequence_no)
        
        # Create BytesIO object for download
        pdf_buffer = io.BytesIO(pdf_a3_bytes)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f'Convert and download error: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Convert and download failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'PDF/A-3 Converter'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting PDF/A-3 Converter server on http://localhost:{port}")
    print(f"Test interface available at: http://localhost:{port}/test.html")
    app.run(host='0.0.0.0', port=port, debug=False)