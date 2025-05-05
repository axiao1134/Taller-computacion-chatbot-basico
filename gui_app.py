import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from threading import Thread
import fitz
import os
import shutil
from modules import pdf_loader, qa_engine

class ElegantPDFChat:
    def __init__(self, root):
        self.root = root
        self.root.title("Taller de computación")
        self.setup_constants()
        self.setup_styles()
        self.init_ui()
        self.load_initial_documents()
        
    def setup_constants(self):
        self.COLORS = {
            'primary': '#1A2B3C',
            'secondary': '#2C3E50',
            'accent': '#3498DB',
            'text': '#ECF0F1',
            'highlight': '#7F8C8D',
            'success': '#2ECC71'
        }
        
        self.FONTS = {
            'title': ('Segoe UI', 12, 'bold'),
            'body': ('Segoe UI', 10),
            'input': ('Segoe UI', 11)
        }
        
        self.PDF_DIR = "data/uploads"
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar estilos base
        self.style.configure('.', 
                           background=self.COLORS['primary'],
                           foreground=self.COLORS['text'],
                           font=self.FONTS['body'])
        
        # Botones
        self.style.configure('TButton', 
                           padding=8,
                           borderwidth=0,
                           focuscolor=self.COLORS['primary'])
        self.style.map('TButton',
                     background=[
                         ('active', self.COLORS['accent']),
                         ('!disabled', self.COLORS['secondary'])
                     ])
        
        # Treeview
        self.style.configure('Treeview', 
                            background=self.COLORS['secondary'],
                            fieldbackground=self.COLORS['secondary'],
                            rowheight=28)
        self.style.map('Treeview', 
                     background=[('selected', self.COLORS['accent'])])
        
    def init_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Chat
        self.setup_chat_panel(main_frame)
        
        # Panel derecho - Documentos
        self.setup_doc_panel(main_frame)
        
    def setup_chat_panel(self, parent):
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Cabecera del chat
        header = ttk.Frame(chat_frame)
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header, text="📚 Taller de computación", 
                 font=self.FONTS['title']).pack(side=tk.LEFT)
        
        self.stats_label = ttk.Label(header, style='TLabel')
        self.stats_label.pack(side=tk.RIGHT)
        
        # Historial de chat
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state='disabled',
            bg=self.COLORS['secondary'],
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            font=self.FONTS['body'],
            padx=15,
            pady=15,
            relief='flat'
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        
        # Configurar estilos de mensajes
        self.chat_history.tag_config('user', foreground='#BDC3C7')
        self.chat_history.tag_config('assistant', foreground=self.COLORS['accent'])
        self.chat_history.tag_config('system', foreground=self.COLORS['success'])
        self.chat_history.tag_config('thinking', foreground=self.COLORS['highlight'])
        
        # Controles de entrada
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.user_input = ttk.Entry(
            input_frame,
            font=self.FONTS['input']
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.setup_input_placeholder()
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Enviar ➤",
            command=self.process_query
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="🔄 Actualizar",
            command=self.manual_refresh
        ).pack(side=tk.LEFT, padx=2)
        
    def setup_doc_panel(self, parent):
        doc_frame = ttk.Frame(parent, width=280)
        doc_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cabecera de documentos
        doc_header = ttk.Frame(doc_frame)
        doc_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(doc_header, 
                 text="📁 Documentos Cargados",
                 font=self.FONTS['title']).pack(side=tk.LEFT)
        
        # Lista de documentos
        self.doc_list = ttk.Treeview(
            doc_frame,
            columns=('pages', 'words'),
            show='headings',
            selectmode='none',
            style='Treeview'
        )
        self.doc_list.heading('#0', text='Nombre')
        self.doc_list.heading('pages', text='Págs')
        self.doc_list.heading('words', text='Palabras')
        self.doc_list.column('#0', width=160)
        self.doc_list.column('pages', width=60, anchor='center')
        self.doc_list.column('words', width=80, anchor='center')
        self.doc_list.pack(fill=tk.BOTH, expand=True)
        
    def setup_input_placeholder(self):
        self.user_input.insert(0, "Escribe tu consulta aquí...")
        self.user_input.bind('<FocusIn>', self.clear_input_placeholder)
        self.user_input.bind('<FocusOut>', self.set_input_placeholder)
        self.user_input.configure(foreground=self.COLORS['highlight'])
        
    def clear_input_placeholder(self, event):
        if self.user_input.get() == "Escribe tu consulta aquí...":
            self.user_input.delete(0, tk.END)
            self.user_input.configure(foreground='black')
            
    def set_input_placeholder(self, event):
        if not self.user_input.get():
            self.user_input.insert(0, "Escribe tu consulta aquí...")
            self.user_input.configure(foreground=self.COLORS['highlight'])
            
    def load_initial_documents(self):
        if os.path.exists(self.PDF_DIR):
            Thread(target=self.load_documents).start()
            
    def manual_refresh(self):
        """Actualizar manualmente los documentos"""
        Thread(target=self.load_documents).start()
        self.add_system_message("Sistema: Actualizando documentos...")
            
    def load_documents(self):
        """Cargar documentos desde el directorio"""
        try:
            self.pdf_data = pdf_loader.load_all_pdfs()
            documents = []
            total_pages = 0
            total_words = 0
            
            for filename, data in self.pdf_data.items():
                doc_path = os.path.join(self.PDF_DIR, filename)
                with fitz.open(doc_path) as doc:
                    pages = len(doc)
                words = len(data.split())
                documents.append((filename, pages, words))
                total_pages += pages
                total_words += words
                
            self.root.after(0, self.update_interface, documents, total_pages, total_words)
            
        except Exception as e:
            self.root.after(0, self.add_system_message, f"Error: {str(e)}")
            
    def update_interface(self, documents, total_pages, total_words):
        """Actualizar todos los elementos de la UI"""
        self.update_document_list(documents)
        self.update_stats(len(documents), total_pages, total_words)
        self.add_system_message(f"Sistema: Cargados {len(documents)} documentos")
            
    def update_document_list(self, documents):
        """Actualizar la lista de documentos"""
        self.doc_list.delete(*self.doc_list.get_children())
        for doc in documents:
            self.doc_list.insert('', 'end', 
                               text=doc[0], 
                               values=(doc[1], doc[2]))
            
    def update_stats(self, total_docs, total_pages, total_words):
        """Actualizar las estadísticas"""
        self.stats_label.config(
            text=f"📊 Docs: {total_docs} | Págs: {total_pages} | Palabras: {total_words}"
        )
        
    def add_system_message(self, message):
        """Añadir mensaje del sistema"""
        self.append_message('system', message)
        
    def process_query(self):
        """Procesar la consulta del usuario"""
        query = self.user_input.get().strip()
        if query and query != "Escribe tu consulta aquí...":
            self.user_input.delete(0, tk.END)
            self.append_message('user', f"Tú: {query}")
            self.show_thinking_indicator()
            Thread(target=self.get_assistant_response, args=(query,)).start()
            
    def get_assistant_response(self, query):
        """Obtener respuesta del asistente"""
        response = qa_engine.answer_question(query, self.pdf_data)
        self.root.after(0, self.hide_thinking_indicator)
        self.root.after(0, self.append_message, 'assistant', f"Asistente: {response}")
            
    def append_message(self, sender, message):
        """Añadir mensaje al historial"""
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"\n{message}\n", sender)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
            
    def show_thinking_indicator(self):
        """Mostrar indicador de procesamiento"""
        self.chat_history.config(state='normal')
        start_pos = self.chat_history.index(tk.END)
        self.chat_history.insert(tk.END, "\nSistema: Procesando consulta...\n", 'thinking')
        end_pos = self.chat_history.index(tk.END)
        self.thinking_range = (start_pos, end_pos)
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
        
    def hide_thinking_indicator(self):
        """Ocultar indicador de procesamiento"""
        if hasattr(self, 'thinking_range'):
            try:
                self.chat_history.config(state='normal')
                self.chat_history.delete(self.thinking_range[0], self.thinking_range[1])
                self.chat_history.config(state='disabled')
            except Exception as e:
                print(f"Error limpiando indicador: {e}")
            finally:
                del self.thinking_range

def main():
    root = tk.Tk()
    root.geometry("1280x800")
    root.configure(bg='#1A2B3C')
    
    # Centrar ventana
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 800) // 2
    root.geometry(f"+{x}+{y}")
    
    # Verificar y crear directorio PDFs
    if not os.path.exists("data/uploads"):
        os.makedirs("data/uploads")
    
    ElegantPDFChat(root)
    root.mainloop()

if __name__ == "__main__":
    main()