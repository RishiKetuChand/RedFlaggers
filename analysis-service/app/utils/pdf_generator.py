import logging
import os
import tempfile
import uuid
from typing import Dict, Any
from datetime import datetime

import pypandoc
from google.cloud import storage

logger = logging.getLogger(__name__)


class PDFGenerator:
    def __init__(self):
        self.storage_client = storage.Client()

    def generate_pdf_from_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Generate PDF from analysis results and return markdown content"""
        startup_name = analysis_data.get('startup_name', 'Unknown Startup')
        results = analysis_data.get('results', {})
        processing_time = analysis_data.get('processing_time_seconds', 0)
        timestamp = analysis_data.get('timestamp', datetime.utcnow().isoformat())

        # Build markdown content
        md_content = f"""# Analysis Report: {startup_name}

**Generated:** {timestamp}  
**Processing Time:** {processing_time:.2f} seconds  
**Request ID:** {analysis_data.get('request_id', 'N/A')}

---

"""

        # Add each section
        for section_name, section_data in results.items():
            if isinstance(section_data, dict) and section_data.get('status') == 'success':
                md_content += f"{section_data.get('content', 'No content available')}\n\n"
                md_content += "---\n\n"
                md_content += "\\newpage"
            elif isinstance(section_data, dict) and 'error' in section_data:
                md_content += f"**Error:** {section_data['error']}\n\n"
                md_content += "---\n\n"
                md_content += "\\newpage"

        return md_content

    def convert_to_pdf(self, md_content: str, upload_id: str, filename: str = None) -> str:
        """Convert markdown content to PDF and return the file path"""
        if not filename:
            filename = f"{upload_id}_analysis.pdf"
        
        # Create temporary file path
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, filename)

        try:
            # Convert markdown to PDF using pypandoc
            pypandoc.convert_text(
                md_content, 
                "pdf", 
                format="md", 
                outputfile=pdf_path,
                extra_args=["--pdf-engine=xelatex"]
            )
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")

    def upload_to_gcs(self, file_path: str, bucket_name: str, blob_name: str = None) -> str:
        """Upload file to Google Cloud Storage and return public URL"""
        if not blob_name:
            blob_name = f"results/{os.path.basename(file_path)}"
        
        try:
            # Get bucket
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Upload file
            with open(file_path, 'rb') as file_data:
                blob.upload_from_file(file_data, content_type='application/pdf')
            
            # Make blob publicly accessible
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(f"File uploaded successfully to GCS: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {str(e)}")
            raise e
        finally:
            # Clean up local file
            try:
                if os.path.exists(file_path):
                    #TODO remove it later
                    #os.remove(file_path)
                    logger.info(f"Cleaned up local file: {file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup local file: {str(cleanup_error)}")

    def process_analysis_to_pdf_url(self, analysis_data: Dict[str, Any], bucket_name: str, upload_id: str) -> str:
        """Complete workflow: analysis -> markdown -> PDF -> upload -> return URL"""
        try:
            startup_name = analysis_data.get('startup_name', 'unknown')
            request_id = analysis_data.get('request_id', uuid.uuid4().hex[:8])
            
            # Generate markdown content
            md_content = self.generate_pdf_from_analysis(analysis_data)
            
            # Convert to PDF
            filename = f"{startup_name}_{upload_id}_analysis.pdf"
            pdf_path = self.convert_to_pdf(md_content, upload_id, filename)
            
            # Upload to GCS and get public URL
            blob_name = f"analysis_reports/{filename}"
            public_url = self.upload_to_gcs(pdf_path, bucket_name, blob_name)
            
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to process analysis to PDF URL: {str(e)}")
            raise e
