# text_extraction.py
import io
import os
import fitz
from pdf2image import convert_from_path
from PIL import Image
from aws_clients import textract

def extract_text_fitz(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        return " ".join(page.get_text() for page in doc).strip()
    except Exception:
        return ""

def extract_text_textract(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    text = []

    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        response = textract.detect_document_text(
            Document={"Bytes": buf.getvalue()}
        )

        lines = [
            b["Text"]
            for b in response["Blocks"]
            if b["BlockType"] == "LINE"
        ]
        text.append(" ".join(lines))

    return " ".join(text)

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image files (JPG, PNG) using AWS Textract"""
    try:
        with open(image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        
        response = textract.detect_document_text(
            Document={"Bytes": img_bytes}
        )
        
        lines = [
            b["Text"]
            for b in response["Blocks"]
            if b["BlockType"] == "LINE"
        ]
        
        return " ".join(lines)
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def extract_text(file_path: str) -> tuple[str, str]:
    """Extract text from PDF or image files"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Handle image files
    if file_ext in ['.jpg', '.jpeg', '.png']:
        text = extract_text_from_image(file_path)
        return text, "TEXTRACT_IMAGE"
    
    # Handle PDF files
    text = extract_text_fitz(file_path)
    if len(text) > 20:
        return text, "FITZ"

    return extract_text_textract(file_path), "TEXTRACT"
