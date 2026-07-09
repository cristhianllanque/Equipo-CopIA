import customtkinter as ctk
from PIL import Image
import subprocess
import threading
import requests
import time
import sys
import os
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

class ServerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CopIA - Centro de Control Central")
        self.geometry("680x620")
        self.resizable(False, False)
        
        self.processes = []
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.build_ui()

    def build_ui(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=15, fill="x")
        
        try:
            logo_img = Image.open(os.path.join(PROJECT_DIR, "Frontend", "public", "logoCopAI.png"))
            self.logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(70, 70))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo, text="")
            self.logo_label.pack(side="left", padx=(40, 20))
        except Exception:
            pass

        self.title_label = ctk.CTkLabel(self.header_frame, text="Centro de Control CopIA", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(side="left")

        # Status Frame
        self.status_frame = ctk.CTkFrame(self, corner_radius=15)
        self.status_frame.pack(pady=10, padx=40, fill="both", expand=True)
        
        # MySQL Step
        ctk.CTkLabel(self.status_frame, text="Paso 1: Base de Datos", font=ctk.CTkFont(size=16, weight="bold")).place(x=30, y=30, anchor="w")
        self.btn_xampp = ctk.CTkButton(self.status_frame, text="Abrir XAMPP", width=110, command=self.open_xampp)
        self.btn_xampp.place(x=250, y=30, anchor="w")
        self.btn_confirm_mysql = ctk.CTkButton(self.status_frame, text="Confirmar MySQL Iniciado", width=180, fg_color="#b91c1c", hover_color="#991b1b", command=self.confirm_mysql)
        self.btn_confirm_mysql.place(x=380, y=30, anchor="w")

        # Servers
        self.lbl_backend = self.create_status_row("Paso 2: Servidor Backend", "Esperando MySQL...", y_pos=80)
        self.lbl_frontend = self.create_status_row("Paso 3: Panel Frontend", "Esperando MySQL...", y_pos=130)
        self.lbl_ngrok = self.create_status_row("Paso 4: Túnel Ngrok", "Esperando MySQL...", y_pos=180)

        # Ngrok URL Frame
        self.url_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=10)
        self.url_frame.pack(pady=10, padx=40, fill="x")
        
        self.lbl_url_title = ctk.CTkLabel(self.url_frame, text="Enlace Mágico para la Raspberry Pi:", font=ctk.CTkFont(size=14))
        self.lbl_url_title.pack(pady=(15, 5))
        
        self.lbl_url = ctk.CTkLabel(self.url_frame, text="Esperando servidores...", font=ctk.CTkFont(size=20, weight="bold"), text_color="#64748b")
        self.lbl_url.pack(pady=(0, 5))
        
        self.btn_copy = ctk.CTkButton(self.url_frame, text="Copiar Enlace", width=100, height=25, fg_color="#475569", hover_color="#64748b", command=self.copy_url, state="disabled")
        self.btn_copy.pack(pady=(0, 15))

        # Open Web Button
        self.btn_open_web = ctk.CTkButton(self, text="Abrir Sistema Web", font=ctk.CTkFont(size=18, weight="bold"), height=50, fg_color="#475569", state="disabled", command=lambda: webbrowser.open("http://localhost:5173"))
        self.btn_open_web.pack(pady=(10, 20), padx=40, fill="x")

    def create_status_row(self, title, initial_status, y_pos):
        ctk.CTkLabel(self.status_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).place(x=30, y=y_pos, anchor="w")
        status_lbl = ctk.CTkLabel(self.status_frame, text=initial_status, font=ctk.CTkFont(size=14), text_color="yellow")
        status_lbl.place(x=250, y=y_pos, anchor="w")
        return status_lbl

    def open_xampp(self):
        xampp_path = r"C:\xampp\xampp-control.exe"
        if os.path.exists(xampp_path):
            subprocess.Popen([xampp_path])
        else:
            self.btn_xampp.configure(text="No encontrado", fg_color="red")

    def confirm_mysql(self):
        self.btn_confirm_mysql.configure(text="MySQL Confirmado", fg_color="#22c55e", state="disabled")
        self.btn_xampp.configure(state="disabled")
        self.lbl_backend.configure(text="Iniciando...", text_color="yellow")
        self.lbl_frontend.configure(text="Iniciando...", text_color="yellow")
        self.lbl_ngrok.configure(text="Iniciando...", text_color="yellow")
        self.lbl_url.configure(text="Buscando enlace...", text_color="#3b82f6")
        
        threading.Thread(target=self.start_and_monitor_servers, daemon=True).start()

    def run_hidden(self, cmd, cwd=None):
        CREATE_NO_WINDOW = 0x08000000
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd, creationflags=CREATE_NO_WINDOW)
        self.processes.append(proc)
        return proc

    def start_and_monitor_servers(self):
        # Iniciar todo en background
        self.run_hidden("ngrok http 8000", cwd=PROJECT_DIR)
        self.run_hidden("python api_main.py", cwd=PROJECT_DIR)
        frontend_dir = os.path.join(PROJECT_DIR, "Frontend")
        self.run_hidden("npm run dev", cwd=frontend_dir)
        
        # Pings de verificacion real
        backend_ok = False
        frontend_ok = False
        ngrok_ok = False
        
        for _ in range(30): # Timeout de ~60 segundos
            time.sleep(2)
            
            if not backend_ok:
                try:
                    resp = requests.get("http://localhost:8000/docs", timeout=1)
                    if resp.status_code == 200:
                        backend_ok = True
                        self.lbl_backend.configure(text="En línea (OK)", text_color="#22c55e")
                except: pass
                
            if not frontend_ok:
                try:
                    resp = requests.get("http://localhost:5173", timeout=1)
                    if resp.status_code == 200:
                        frontend_ok = True
                        self.lbl_frontend.configure(text="En línea (OK)", text_color="#22c55e")
                except: pass
                
            if not ngrok_ok:
                try:
                    resp = requests.get("http://localhost:4040/api/tunnels", timeout=1)
                    if resp.status_code == 200:
                        tunnels = resp.json().get("tunnels", [])
                        for t in tunnels:
                            if t.get("proto") == "https":
                                ngrok_ok = True
                                self.lbl_ngrok.configure(text="En línea (OK)", text_color="#22c55e")
                                self.lbl_url.configure(text=t.get("public_url"), text_color="#22c55e")
                                self.btn_copy.configure(state="normal", fg_color="#0ea5e9")
                except: pass
                
            if backend_ok and frontend_ok and ngrok_ok:
                # Todo listo
                self.btn_open_web.configure(state="normal", fg_color="#0284c7")
                return
                
        # Si llega aquí, hubo error
        if not backend_ok: self.lbl_backend.configure(text="Error al conectar", text_color="red")
        if not frontend_ok: self.lbl_frontend.configure(text="Error al conectar", text_color="red")
        if not ngrok_ok: self.lbl_ngrok.configure(text="Error al conectar", text_color="red")
        self.lbl_url.configure(text="Error general de arranque", text_color="red")

    def copy_url(self):
        url = self.lbl_url.cget("text")
        if url.startswith("http"):
            self.clipboard_clear()
            self.clipboard_append(url)
            self.btn_copy.configure(text="¡Copiado!", fg_color="#22c55e")
            self.after(2000, lambda: self.btn_copy.configure(text="Copiar Enlace", fg_color="#0ea5e9"))

    def on_closing(self):
        for p in self.processes:
            try:
                subprocess.Popen(f"taskkill /F /T /PID {p.pid}", shell=True, creationflags=0x08000000)
            except: pass
        self.destroy()

if __name__ == "__main__":
    app = ServerDashboard()
    app.mainloop()
