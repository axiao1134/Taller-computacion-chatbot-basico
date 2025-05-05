from modules.llm_handler import ask_llm

def generate_context_from_pdfs(pdf_texts):
    """Une el contenido de todos los PDFs cargados."""
    context = "\n\n".join(pdf_texts.values())
    return context

def answer_question(question, pdf_texts):
    """Construye el prompt y obtiene la respuesta del LLM."""
    if not pdf_texts:
        return "No se han cargado PDFs."

    context = generate_context_from_pdfs(pdf_texts)
    
    prompt = (
        f"Contexto:\n{context}\n\n"
        f"Pregunta: {question}"
    )

    response = ask_llm(prompt)
    return response
