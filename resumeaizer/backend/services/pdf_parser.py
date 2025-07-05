from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer
from typing import Dict, List, Any
import io
import json

class PdfParser:
    def __init__(self):
        self.layout_params = LAParams(
            line_overlap=0.5,
            char_margin=2.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=True
        )

    def parse_with_layout(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extracts text with precise layout information"""
        result = {
            "metadata": {},
            "pages": [],
            "element_map": {}  # For tracking modifications
        }

        with io.BytesIO(file_bytes) as pdf_file:
            # First get basic info with PyPDF2
            try:
                import PyPDF2
                pdf = PyPDF2.PdfReader(pdf_file)
                result["metadata"] = {
                    "author": pdf.metadata.author or "",
                    "creator": pdf.metadata.creator or "",
                    "producer": pdf.metadata.producer or "",
                    "title": pdf.metadata.title or ""
                }
                pdf_file.seek(0)
            except:
                pass

            # Process layout with pdfminer
            for page_num, page_layout in enumerate(extract_pages(pdf_file, laparams=self.layout_params)):
                page_data = {
                    "number": page_num + 1,
                    "width": page_layout.width,
                    "height": page_layout.height,
                    "elements": []
                }

                for elem_idx, element in enumerate(page_layout):
                    if isinstance(element, LTTextContainer):
                        element_id = f"page_{page_num+1}_element_{elem_idx}"
                        element_data = self._extract_element_data(element, element_id)
                        
                        page_data["elements"].append(element_data)
                        result["element_map"][element_id] = element_data

                result["pages"].append(page_data)

        return result

    def _extract_element_data(self, element, element_id: str) -> Dict[str, Any]:
        """Extracts detailed information about a text element"""
        font_info = self._get_font_data(element)
        
        return {
            "id": element_id,
            "text": element.get_text().strip(),
            "x": element.x0,
            "y": element.y0,
            "width": element.width,
            "height": element.height,
            "font": font_info
        }

    def _get_font_data(self, element) -> Dict[str, Any]:
        """Extracts font characteristics from the first character"""
        # Default font info if analysis fails
        font_info = {
            "name": "Helvetica",
            "size": 11,
            "bold": False,
            "italic": False
        }

        try:
            # Get the first character's font info
            first_char = next(c for c in element if isinstance(c, pdfminer.layout.LTChar))
            font_info.update({
                "name": first_char.fontname,
                "size": first_char.size,
                "bold": "bold" in first_char.fontname.lower(),
                "italic": "italic" in first_char.fontname.lower()
            })
        except:
            pass

        return font_info