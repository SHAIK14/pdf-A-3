import io
import hashlib
import datetime
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import (
    DictionaryObject, ArrayObject, NameObject, TextStringObject, 
    ByteStringObject, StreamObject, NumberObject, BooleanObject
)
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
        
        # Add comprehensive metadata for PDF/A-3
        self._add_metadata(writer)
        
        # Add catalog modifications for PDF/A-3 compliance
        self._add_catalog_modifications(writer)
        
        # Add XML attachment with proper PDF/A-3 structure
        self._add_xml_attachment(writer, xml_bytes, sequence_no)
        
        # Write output
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        
        return output_buffer.getvalue()
    
    def _add_metadata(self, writer):
        """Add comprehensive metadata for PDF/A-3"""
        now = datetime.datetime.now()
        create_date = now.strftime("D:%Y%m%d%H%M%S+00'00'")
        
        writer.add_metadata({
            '/Title': 'PDF/A-3 Document with XML Attachment',
            '/Creator': 'PDF/A-3 Python Converter v1.0',
            '/Producer': 'PDF/A-3 Python Converter v1.0',
            '/CreationDate': create_date,
            '/ModDate': create_date,
            '/Subject': 'PDF/A-3 compliant document with embedded electronic invoice',
            '/Keywords': 'PDF/A-3, Electronic Invoice, XML Attachment'
        })
    
    def _add_catalog_modifications(self, writer):
        """Add catalog modifications for PDF/A-3 compliance"""
        catalog = writer._root_object
        
        # Set PDF version to 1.7 (required for PDF/A-3)
        catalog[NameObject('/Version')] = NameObject('/1.7')
        
        # Add MarkInfo for accessibility (required for PDF/A)
        catalog[NameObject('/MarkInfo')] = DictionaryObject({
            NameObject('/Marked'): BooleanObject(True)
        })
        
        # Add structure tree root for accessibility
        catalog[NameObject('/StructTreeRoot')] = DictionaryObject({
            NameObject('/Type'): NameObject('/StructTreeRoot'),
            NameObject('/K'): ArrayObject(),
            NameObject('/ParentTree'): DictionaryObject({
                NameObject('/Nums'): ArrayObject()
            })
        })
        
        # Generate document ID (required for PDF/A)
        doc_id = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()
        catalog[NameObject('/ID')] = ArrayObject([
            ByteStringObject(doc_id.encode()[:16]),
            ByteStringObject(doc_id.encode()[:16])
        ])
        
        # Add XMP metadata for PDF/A-3 compliance
        self._add_xmp_metadata(writer, catalog)
    
    def _add_xmp_metadata(self, writer, catalog):
        """Add proper XMP metadata for PDF/A-3 compliance"""
        now = datetime.datetime.now()
        create_date = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        document_id = hashlib.sha256(str(now).encode()).hexdigest()[:32]
        
        xmp_template = '''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Python XMP Toolkit">
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about=""
            xmlns:xmp="http://ns.adobe.com/xap/1.0/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
            xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/"
            xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/">
         <xmp:CreateDate>{create_date}</xmp:CreateDate>
         <xmp:ModifyDate>{modify_date}</xmp:ModifyDate>
         <xmp:CreatorTool>PDF/A-3 Python Converter v1.0</xmp:CreatorTool>
         <xmp:MetadataDate>{create_date}</xmp:MetadataDate>
         <xmpMM:DocumentID>uuid:{document_id}</xmpMM:DocumentID>
         <dc:format>application/pdf</dc:format>
         <dc:title>
            <rdf:Alt>
               <rdf:li xml:lang="x-default">PDF/A-3 Document with XML Attachment</rdf:li>
            </rdf:Alt>
         </dc:title>
         <dc:creator>
            <rdf:Seq>
               <rdf:li>PDF/A-3 Python Converter</rdf:li>
            </rdf:Seq>
         </dc:creator>
         <pdf:PDFVersion>1.7</pdf:PDFVersion>
         <pdf:Producer>PDF/A-3 Python Converter</pdf:Producer>
         <pdfaid:part>3</pdfaid:part>
         <pdfaid:conformance>B</pdfaid:conformance>
      </rdf:Description>
   </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''.format(
            create_date=create_date,
            modify_date=create_date,
            document_id=document_id
        )
        
        # Create metadata stream
        xmp_bytes = xmp_template.encode('utf-8')
        
        # Create metadata stream object
        metadata_stream = DictionaryObject()
        metadata_stream.update({
            NameObject('/Type'): NameObject('/Metadata'),
            NameObject('/Subtype'): NameObject('/XML'),
            NameObject('/Length'): NumberObject(len(xmp_bytes))
        })
        
        # Add the stream data
        metadata_stream._data = xmp_bytes
        
        # Add metadata reference to catalog
        catalog[NameObject('/Metadata')] = metadata_stream
    
    def _add_xml_attachment(self, writer, xml_bytes, sequence_no):
        """Add XML file as attachment to PDF for PDF/A-3 compliance"""
        catalog = writer._root_object
        
        # Create embedded file stream with proper parameters
        xml_stream = DictionaryObject()
        xml_stream._data = xml_bytes
        xml_stream.update({
            NameObject('/Type'): NameObject('/EmbeddedFile'),
            NameObject('/Length'): NumberObject(len(xml_bytes)),
            NameObject('/Subtype'): NameObject('/application#2Fxml'),
            NameObject('/Params'): DictionaryObject({
                NameObject('/Size'): NumberObject(len(xml_bytes)),
                NameObject('/CreationDate'): TextStringObject(
                    datetime.datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'")
                ),
                NameObject('/ModDate'): TextStringObject(
                    datetime.datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'")
                ),
                NameObject('/CheckSum'): TextStringObject(
                    hashlib.md5(xml_bytes).hexdigest().upper()
                )
            })
        })
        
        # Create file specification with proper PDF/A-3 attributes
        filename = f'invoice_{sequence_no}.xml'
        file_spec = DictionaryObject({
            NameObject('/Type'): NameObject('/Filespec'),
            NameObject('/F'): TextStringObject(filename),
            NameObject('/UF'): TextStringObject(filename),
            NameObject('/Desc'): TextStringObject('Electronic Invoice XML Data'),
            NameObject('/EF'): DictionaryObject({
                NameObject('/F'): xml_stream,
                NameObject('/UF'): xml_stream
            }),
            NameObject('/AFRelationship'): NameObject('/Data')
        })
        
        # Initialize Names dictionary if not present
        if NameObject('/Names') not in catalog:
            catalog[NameObject('/Names')] = DictionaryObject()
        
        names_dict = catalog[NameObject('/Names')]
        
        # Initialize EmbeddedFiles name tree
        if NameObject('/EmbeddedFiles') not in names_dict:
            names_dict[NameObject('/EmbeddedFiles')] = DictionaryObject({
                NameObject('/Names'): ArrayObject()
            })
        
        embedded_files = names_dict[NameObject('/EmbeddedFiles')]
        
        # Ensure Names array exists
        if NameObject('/Names') not in embedded_files:
            embedded_files[NameObject('/Names')] = ArrayObject()
        
        # Add to Names array (key-value pairs)
        names_array = embedded_files[NameObject('/Names')]
        names_array.extend([
            TextStringObject(filename),
            file_spec
        ])
        
        # Add to Associated Files array for PDF/A-3
        if NameObject('/AF') not in catalog:
            catalog[NameObject('/AF')] = ArrayObject()
        
        catalog[NameObject('/AF')].append(file_spec)
        
        return file_spec