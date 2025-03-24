import base64
import io
import os
from typing import Union, Optional

try:
    import fitz
except ImportError:
    raise ImportError(
        "PyMuPDF package is not installed. "
        "Please install it using: pip install PyMuPDF"
    )
from PIL import Image


def pdf_page_to_base64(pdf_path: str, page_number: int = 1) -> str:
    """Convert a PDF page to a base64-encoded string.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to convert (1-indexed)
        
    Returns:
        Base64-encoded string of the PDF page as PNG
    """
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1)  # input is one-indexed
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def image_to_base64(image_path: str) -> str:
    """Convert an image file to a base64-encoded string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64-encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_document_as_base64(document_path: str, page_number: Optional[int] = 1) -> str:
    """Convert a document (PDF or image) to a base64-encoded string.
    
    Args:
        document_path: Path to the document
        page_number: Page number for PDFs (ignored for images)
        
    Returns:
        Base64-encoded string of the document
    """
    _, ext = os.path.splitext(document_path.lower())
    
    if ext == '.pdf':
        return pdf_page_to_base64(document_path, page_number)
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return image_to_base64(document_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
