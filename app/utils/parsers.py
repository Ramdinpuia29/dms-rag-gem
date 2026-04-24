import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from llama_index.core import Document
from unstructured.partition.auto import partition

def parse_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF, falling back to OCR if no text found."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        if not page_text.strip():
            # Scanned PDF or image-based page
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
        text += page_text + "\n"
    doc.close()
    return text

def parse_image(file_path: str) -> str:
    """Extract text from images using pytesseract."""
    return pytesseract.image_to_string(Image.open(file_path))

def parse_with_unstructured(file_path: str) -> str:
    """Extract text using unstructured for various formats (.docx, .txt, .md, .csv, .xlsx)."""
    elements = partition(filename=file_path)
    return "\n\n".join([str(el) for el in elements])

def parse_file(file_path: str) -> list[Document]:
    """Parse file and return a list of LlamaIndex Document objects."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        text = parse_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        text = parse_image(file_path)
    else:
        # Handles .docx, .txt, .md, .csv, .xlsx etc.
        text = parse_with_unstructured(file_path)
    
    return [Document(text=text, metadata={"file_name": os.path.basename(file_path)})]
