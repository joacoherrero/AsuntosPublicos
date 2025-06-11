import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from example import main as process_news
import threading

class NewsAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Noticias")
        self.root.geometry("800x600")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
        # Crear el contenedor principal
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        self.title = ttk.Label(
            self.main_frame, 
            text="Sistema de Análisis de Noticias", 
            style="Title.TLabel"
        )
        self.title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Frame para estadísticas
        self.stats_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Estadísticas", 
            padding="10"
        )
        self.stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.last_run_label = ttk.Label(
            self.stats_frame, 
            text="Última ejecución: Nunca"
        )
        self.last_run_label.grid(row=0, column=0, sticky=tk.W)
        
        self.reports_count_label = ttk.Label(
            self.stats_frame, 
            text="Reportes generados hoy: 0"
        )
        self.reports_count_label.grid(row=1, column=0, sticky=tk.W)
        
        # Frame para acciones
        self.actions_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Acciones", 
            padding="10"
        )
        self.actions_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Botones de acción
        self.process_button = ttk.Button(
            self.actions_frame, 
            text="Procesar Noticias",
            command=self.process_news
        )
        self.process_button.grid(row=0, column=0, padx=5)
        
        self.view_reports_button = ttk.Button(
            self.actions_frame, 
            text="Ver Reportes",
            command=self.view_reports
        )
        self.view_reports_button.grid(row=0, column=1, padx=5)
        
        self.config_button = ttk.Button(
            self.actions_frame, 
            text="Configuración",
            command=self.show_config
        )
        self.config_button.grid(row=0, column=2, padx=5)
        
        # Frame para log
        self.log_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Log de Actividad", 
            padding="10"
        )
        self.log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Área de texto para log
        self.log_text = tk.Text(
            self.log_frame, 
            height=10, 
            width=70, 
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el log
        self.log_scroll = ttk.Scrollbar(
            self.log_frame, 
            orient=tk.VERTICAL, 
            command=self.log_text.yview
        )
        self.log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = self.log_scroll.set
        
        # Barra de estado
        self.status_label = ttk.Label(
            self.main_frame, 
            text="Listo", 
            relief=tk.SUNKEN
        )
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configurar expansión de grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
    def log(self, message):
        """Agrega un mensaje al área de log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def process_news(self):
        """Inicia el procesamiento de noticias en un hilo separado"""
        self.process_button.state(['disabled'])
        self.status_label['text'] = "Procesando noticias..."
        self.log("Iniciando procesamiento de noticias...")
        
        def process():
            try:
                process_news()
                self.root.after(0, self.process_completed)
            except Exception as e:
                self.root.after(0, lambda: self.process_error(str(e)))
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def process_completed(self):
        """Callback cuando el procesamiento termina exitosamente"""
        self.process_button.state(['!disabled'])
        self.status_label['text'] = "Procesamiento completado"
        self.log("Procesamiento de noticias completado exitosamente")
        self.update_stats()
        messagebox.showinfo("Éxito", "Procesamiento de noticias completado")
    
    def process_error(self, error_message):
        """Callback cuando hay un error en el procesamiento"""
        self.process_button.state(['!disabled'])
        self.status_label['text'] = "Error en el procesamiento"
        self.log(f"Error: {error_message}")
        messagebox.showerror("Error", f"Error en el procesamiento: {error_message}")
    
    def view_reports(self):
        """Abre el directorio de reportes"""
        reports_dir = "Reportes"
        if os.path.exists(reports_dir):
            os.startfile(reports_dir)
        else:
            messagebox.showwarning("Aviso", "No hay reportes generados todavía")
    
    def show_config(self):
        """Muestra la ventana de configuración"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuración")
        config_window.geometry("600x400")
        
        # Aquí agregaremos las opciones de configuración
        ttk.Label(
            config_window, 
            text="Configuración del Sistema",
            style="Title.TLabel"
        ).pack(pady=20)
        
        # Por ahora solo mostraremos un mensaje
        ttk.Label(
            config_window,
            text="Funcionalidad en desarrollo"
        ).pack(pady=20)
    
    def update_stats(self):
        """Actualiza las estadísticas mostradas"""
        self.last_run_label['text'] = f"Última ejecución: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        # Contar reportes de hoy
        today = datetime.now().strftime("%Y%m%d")
        reports_dir = os.path.join("Reportes", today)
        if os.path.exists(reports_dir):
            reports_count = len([f for f in os.listdir(reports_dir) if f.endswith('.docx')])
            self.reports_count_label['text'] = f"Reportes generados hoy: {reports_count}"

def main():
    root = tk.Tk()
    app = NewsAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 