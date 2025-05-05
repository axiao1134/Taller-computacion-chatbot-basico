from modules import pdf_loader, qa_engine

def main():
    pdf_texts = {}
    while True:
        print("\n==== Chatbot IA con PDFs ====")
        print("1. Cargar archivos PDF")
        print("2. Hacer una pregunta")
        print("3. Salir")
        choice = input("Seleccione una opción: ").strip()

        if choice == "1":
            print("\nCargando archivos PDF...")
            pdf_texts = pdf_loader.load_all_pdfs()
            if pdf_texts:
                print(f"{len(pdf_texts)} archivo(s) cargado(s) exitosamente.")
            else:
                print("No se encontraron archivos PDF o no contienen texto.")

        elif choice == "2":
            if not pdf_texts:
                print("Primero debes cargar archivos PDF.")
                continue
            question = input("\nEscribe tu pregunta: ").strip()
            if question:
                print("\nPensando...")
                answer = qa_engine.answer_question(question, pdf_texts)
                print("\nRespuesta del chatbot:")
                print(answer)
            else:
                print("La pregunta no puede estar vacía.")

        elif choice == "3":
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
