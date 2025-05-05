import os
import fitz  # PyMuPDF

PDF_DIR = "data/uploads"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error al procesar {pdf_path}: {e}")
    return text

def load_all_pdfs():
    pdf_texts = {}
    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            path = os.path.join(PDF_DIR, filename)
            print(f"Cargando: {filename}")
            text = extract_text_from_pdf(path)
            if text.strip():
                pdf_texts[filename] = text
            else:
                print(f"Advertencia: {filename} no contiene texto legible.")
    return pdf_texts
