from typing import Dict, Any
import PyPDF2
from io import BytesIO
import re

class PdfParsing:
    def parse(self, file_bytes: bytes) -> Dict[str, Any]:

        print("REACHED TILL PDF PARSING SERVICE")
        try:
            # Basic file info
            result = {
                "file_size": len(file_bytes),
                "page_count": 0,
                "text": "",
                "metadata": {}
            }
            
            # Parse PDF content
            with BytesIO(file_bytes) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                
                result["page_count"] = len(reader.pages)
                result["metadata"] = reader.metadata or {}
                
                # Extract text from first 3 pages (adjust as needed)
                text = []
                for page in reader.pages[:3]:
                    text.append(page.extract_text())
                result["text"] = "\n".join(text)
                
                # Simple email extraction example
                emails = re.findall(r'[\w\.-]+@[\w\.-]+', result["text"])
                if emails:
                    result["emails"] = list(set(emails))
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "file_size": len(file_bytes)
            }