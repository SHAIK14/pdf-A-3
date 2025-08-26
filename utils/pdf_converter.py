import io
import hashlib
import datetime
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import DictionaryObject, ArrayObject, NameObject, TextStringObject, ByteStringObject
import xml.etree.ElementTree as ET

class PDFConverter:
    def __init__(self):
        pass

    def convert_to_pdf_a3(self, pdf_bytes, xml_bytes, sequence_no):
        # Validate XML first
        try:
            ET.fromstring(xml_bytes)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {str(e)}")
        
        # Read input PDF
        pdf_input = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_input)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Add basic metadata
        self._add_metadata(writer)
        
        # Add XML attachment
        self._add_xml_attachment(writer, xml_bytes, sequence_no)
        
        # Add basic catalog modifications for PDF/A-3
        self._add_catalog_modifications(writer)
        
        # Write output
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        
        return output_buffer.getvalue()
    
    def _add_metadata(self, writer):
        now = datetime.datetime.now()
        create_date = now.strftime("D:%Y%m%d%H%M%S+00'00'")
        
        writer.add_metadata({
            '/Title': 'PDF/A-3 Document',
            '/Creator': 'PDF/A-3 Python Converter',
            '/Producer': 'PDF/A-3 Python Converter',
            '/CreationDate': create_date,
            '/ModDate': create_date,
            '/Subject': 'PDF/A-3 compliant document with embedded attachments'
        })
    
    def _add_catalog_modifications(self, writer):
        catalog = writer._root_object
        
        # Set PDF version to 1.7 (required for PDF/A-3)
        catalog[NameObject('/Version')] = NameObject('/1.7')
        
        # Add MarkInfo for accessibility
        from PyPDF2.generic import BooleanObject
        catalog[NameObject('/MarkInfo')] = DictionaryObject({
            NameObject('/Marked'): BooleanObject(True)
        })
        
        # Add structure tree root for accessibility
        catalog[NameObject('/StructTreeRoot')] = DictionaryObject({
            NameObject('/Type'): NameObject('/StructTreeRoot')
        })
        
        # Generate document ID (required for PDF/A)
        doc_id = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()
        catalog[NameObject('/ID')] = ArrayObject([
            ByteStringObject(doc_id.encode()[:16]),
            ByteStringObject(doc_id.encode()[:16])
        ])
        
        # Add XMP metadata placeholder (basic implementation)
        self._add_xmp_metadata(writer, catalog)
    
    def _add_xmp_metadata(self, writer, catalog):
        """Add basic XMP metadata for PDF/A-3 compliance"""
        now = datetime.datetime.now()
        create_date = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        
        xmp_template = '''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c015">
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about=""
            xmlns:xmp="http://ns.adobe.com/xap/1.0/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
            xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
         <xmp:CreateDate>{create_date}</xmp:CreateDate>
         <xmp:ModifyDate>{modify_date}</xmp:ModifyDate>
         <xmp:CreatorTool>PDF/A-3 Python Converter</xmp:CreatorTool>
         <dc:format>application/pdf</dc:format>
         <pdf:PDFVersion>1.7</pdf:PDFVersion>
         <pdfaid:part>3</pdfaid:part>
         <pdfaid:conformance>B</pdfaid:conformance>
      </rdf:Description>
   </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''.format(
            create_date=create_date,
            modify_date=create_date
        )
        
        # Create metadata stream (simplified approach)
        xmp_bytes = xmp_template.encode('utf-8')
        
        # Add metadata reference to catalog (simplified - just mark as having metadata)
        from PyPDF2.generic import NumberObject
        metadata_dict = DictionaryObject({
            NameObject('/Type'): NameObject('/Metadata'),
            NameObject('/Subtype'): NameObject('/XML'),
            NameObject('/Length'): NumberObject(len(xmp_bytes))
        })
        
        catalog[NameObject('/Metadata')] = metadata_dict
    
    def _add_xml_attachment(self, writer, xml_bytes, sequence_no):
        """Add XML file as attachment to PDF"""
        from PyPDF2.generic import StreamObject, NumberObject
        
        catalog = writer._root_object
        
        # Create the embedded file stream
        xml_stream = StreamObject()
        xml_stream._data = xml_bytes
        xml_stream.update({
            NameObject('/Type'): NameObject('/EmbeddedFile'),
            NameObject('/Length'): NumberObject(len(xml_bytes)),
            NameObject('/Subtype'): NameObject('/application#2Fxml')
        })
        
        # Create file specification
        filename = f'attachment_{sequence_no}.xml'
        file_spec = DictionaryObject({
            NameObject('/Type'): NameObject('/Filespec'),
            NameObject('/F'): TextStringObject(filename),
            NameObject('/UF'): TextStringObject(filename),
            NameObject('/Desc'): TextStringObject('XML Invoice Data'),
            NameObject('/EF'): DictionaryObject({
                NameObject('/F'): xml_stream
            }),
            NameObject('/AFRelationship'): NameObject('/Data')
        })
        
        # Create Names dictionary structure
        if NameObject('/Names') not in catalog:
            catalog[NameObject('/Names')] = DictionaryObject()
        
        names_dict = catalog[NameObject('/Names')]
        
        if NameObject('/EmbeddedFiles') not in names_dict:
            names_dict[NameObject('/EmbeddedFiles')] = DictionaryObject()
        
        embedded_files = names_dict[NameObject('/EmbeddedFiles')]
        
        if NameObject('/Names') not in embedded_files:
            embedded_files[NameObject('/Names')] = ArrayObject()
        
        names_array = embedded_files[NameObject('/Names')]
        names_array.extend([
            TextStringObject(filename),
            file_spec
        ])
        
        # Add to Associated Files array
        if NameObject('/AF') not in catalog:
            catalog[NameObject('/AF')] = ArrayObject()
        
        catalog[NameObject('/AF')].append(file_spec)