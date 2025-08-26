from flask import Flask, request, jsonify
import base64
import logging
from utils.pdf_converter import PDFConverter

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            'message': 'PDF/A-3 conversion successful'
        })
        
    except Exception as e:
        logger.error(f'Conversion error: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'Conversion failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)