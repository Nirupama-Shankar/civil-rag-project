import fitz  # PyMuPDF
import os

PDF_FOLDER = "data"
IMAGE_OUTPUT_FOLDER = "images"

os.makedirs(IMAGE_OUTPUT_FOLDER, exist_ok=True)

for pdf_file in os.listdir(PDF_FOLDER):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        doc = fitz.open(pdf_path)

        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_name = f"{pdf_file.replace('.pdf','')}_page{page_index+1}_{img_index}.{image_ext}"
                image_path = os.path.join(IMAGE_OUTPUT_FOLDER, image_name)

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                print(f"Saved: {image_name}")

print("✅ Image extraction complete.")
