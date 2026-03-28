"""
Extract images from PDF documents
"""

import fitz  # PyMuPDF
import os
from PIL import Image
import io

def extract_images_from_pdf(pdf_path: str, output_folder: str = "extracted_images"):
    """
    Extract all images from a PDF file
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return []
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Open PDF
    doc = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    extracted_images = []
    
    print(f"📄 Processing PDF: {pdf_name}")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images()
        
        for img_index, img in enumerate(images):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            
            # Save image
            img_filename = f"{pdf_name}_page{page_num+1}_img{img_index+1}.png"
            img_path = os.path.join(output_folder, img_filename)
            
            if pix.n - pix.alpha < 4:
                pix.save(img_path)
            else:
                # Convert CMYK to RGB
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(img_path)
            
            pix = None
            extracted_images.append(img_path)
            print(f"  ✅ Extracted: {img_filename}")
    
    doc.close()
    print(f"✅ Extracted {len(extracted_images)} images from {pdf_name}\n")
    return extracted_images

def extract_all_pdf_images(data_folder: str = "data", output_folder: str = "images"):
    """
    Extract images from all PDFs in data folder
    """
    if not os.path.exists(data_folder):
        print(f"❌ Data folder not found: {data_folder}")
        return
    
    # Create main images folder
    os.makedirs(output_folder, exist_ok=True)
    
    all_images = []
    
    for file in os.listdir(data_folder):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(data_folder, file)
            images = extract_images_from_pdf(pdf_path, output_folder)
            all_images.extend(images)
    
    print(f"\n📸 Total images extracted: {len(all_images)}")
    return all_images

if __name__ == "__main__":
    # Extract all images from PDFs in data folder
    print("🔍 Starting image extraction from PDFs...\n")
    extract_all_pdf_images()
