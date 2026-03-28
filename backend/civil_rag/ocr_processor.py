# ocr_processor.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

# Optional: set tesseract path explicitly if not on PATH
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

def _pdf_is_scanned(pdf_path: str, sample_pages: int = 3) -> bool:
    """
    Check first N pages — if all yield < 30 chars of text,
    treat the whole PDF as scanned.
    """
    doc = fitz.open(pdf_path)
    pages_to_check = min(sample_pages, len(doc))
    total_text = ""
    for i in range(pages_to_check):
        total_text += doc[i].get_text()
    doc.close()
    return len(total_text.strip()) < 30


def extract_text_from_scanned_pdf(pdf_path: str, dpi: int = 200) -> str:
    """
    Rasterize each page using PyMuPDF and run pytesseract OCR.
    Returns concatenated text from all pages.
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    zoom = dpi / 72  # PyMuPDF default is 72 DPI
    mat = fitz.Matrix(zoom, zoom)

    for page_num, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        # Tesseract config: treat as single block of text, English
        page_text = pytesseract.image_to_string(
            img,
            lang="eng",
            config="--psm 6"
        )

        if page_text.strip():
            full_text += f"\n[Page {page_num + 1}]\n{page_text}"

    doc.close()
    return full_text.strip()


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> list[str]:
    """
    Extract all embedded raster images from a PDF.
    Saves them as PNG files and returns list of saved paths.
    Used by image_ingest.py for the image vectorstore.
    """
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    saved_paths = []

    for page_num, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # Convert CMYK or other color spaces to RGB
            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_p{page_num+1}_img{img_index}.png"
            out_path = os.path.join(output_dir, filename)
            pix.save(out_path)
            saved_paths.append(out_path)

    doc.close()
    return saved_paths