import os
import sys
import time
import subprocess
import threading
import customtkinter as ctk

# Configuración global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def check_for_updates():
    try:
        # Obtener los últimos cambios de GitHub sin combinarlos
        subprocess.run(["git", "fetch"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Comprobar si estamos detrás
        status = subprocess.check_output(["git", "status", "-uno"]).decode("utf-8")
        if "Your branch is behind" in status or "Tu rama está detrás" in status:
            return True
        return False
    except Exception:
        return False

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CopIA Edge - Actualizador")
        self.root.geometry("450x260")
        
        # Centrar ventana en la pantalla
        window_width = 450
        window_height = 260
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        
        self.frame = ctk.CTkFrame(master=self.root, corner_radius=15, fg_color="#1e293b")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.lbl_title = ctk.CTkLabel(master=self.frame, text="Actualización Disponible", font=("Helvetica", 20, "bold"), text_color="white")
        self.lbl_title.pack(pady=(20, 10))
        
        self.lbl_info = ctk.CTkLabel(master=self.frame, text="Hay mejoras en la nube listas para instalarse.", font=("Helvetica", 14), text_color="#94a3b8")
        self.lbl_info.pack(pady=(0, 20))
        
        self.btn_update = ctk.CTkButton(master=self.frame, text="Actualizar Ahora", font=("Helvetica", 16, "bold"), height=45, fg_color="#10b981", hover_color="#059669", command=self.start_update)
        self.btn_update.pack(pady=10)
        
        self.progressbar = ctk.CTkProgressBar(master=self.frame, width=300)
        self.progressbar.set(0)
        
        self.btn_skip = ctk.CTkButton(master=self.frame, text="Omitir por ahora", font=("Helvetica", 14), fg_color="transparent", text_color="#94a3b8", hover_color="#334155", command=self.skip)
        self.btn_skip.pack(pady=5)

    def skip(self):
        self.root.destroy()
        sys.exit(0)

    def start_update(self):
        self.btn_update.destroy()
        self.btn_skip.destroy()
        
        self.lbl_info.configure(text="Descargando e instalando actualización...")
        self.progressbar.pack(pady=20)
        self.progressbar.start()
        
        threading.Thread(target=self.run_git_pull, daemon=True).start()
        
    def run_git_pull(self):
        try:
            # Simulamos tiempo para mostrar la animación de la barra
            time.sleep(1.5)
            subprocess.run(["git", "pull", "origin", "main"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
            self.root.after(0, self.finish_update)
        except Exception:
            self.root.after(0, self.fail_update)

    def finish_update(self):
        self.progressbar.stop()
        self.progressbar.set(1)
        self.lbl_info.configure(text="¡Actualización completada!", text_color="#10b981")
        # Cerrar el actualizador para dar paso a la app principal
        self.root.after(2000, self.root.destroy)

    def fail_update(self):
        self.progressbar.stop()
        self.lbl_info.configure(text="Error al actualizar. Comprueba tu conexión.", text_color="#ef4444")
        self.root.after(3000, self.root.destroy)

if __name__ == "__main__":
    if not check_for_updates():
        # Si no hay actualizaciones, terminar silenciosamente de inmediato
        sys.exit(0)
        
    root = ctk.CTk()
    app = UpdaterApp(root)
    root.mainloop()
