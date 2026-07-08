import cv2
import json
import base64
import requests
import time
import threading
import logging
import tkinter as tk
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from tkinter import messagebox, font, ttk
from PIL import Image, ImageTk
from app.core.copia_system import CopIASystem

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] CopIA Edge GUI: %(message)s")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

def get_peru_time():
    return datetime.now(pytz.timezone("America/Lima")).replace(tzinfo=None)

class CopIAEdgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CopIA Edge Monitor")
        # Iniciar en pantalla completa o tamaño grande
        self.root.geometry("1024x600")
        self.root.configure(bg="#0f172a") # Slate 900
        
        # Estado de sesión
        self.conductor_id = None
        self.conductor_nombre = None
        self.sesion_id = None
        self.ruta_id = None
        self.rutas_disponibles = []
        
        # IA y Cámara
        self.system = None
        self.cap = None
        self.is_running = False
        self.latest_payload = None
        self.latest_frame = None
        self.latest_log_data = None
        
        # Fuentes
        self.title_font = font.Font(family="Helvetica", size=36, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=18)
        self.btn_font = font.Font(family="Helvetica", size=20, weight="bold")
        
        self.show_login_screen()
        
    def show_login_screen(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Contenedor central
        frame = tk.Frame(self.root, bg="#1e293b", padx=50, pady=50) # Slate 800
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        lbl_title = tk.Label(frame, text="Transportes Veloz", font=self.title_font, bg="#1e293b", fg="#38bdf8")
        lbl_title.pack(pady=(0, 10))
        
        lbl_sub = tk.Label(frame, text="Terminal de Cabina - CopIA", font=self.normal_font, bg="#1e293b", fg="#94a3b8")
        lbl_sub.pack(pady=(0, 40))
        
        tk.Label(frame, text="Usuario:", font=self.normal_font, bg="#1e293b", fg="white").pack(anchor="w")
        self.entry_user = tk.Entry(frame, font=self.normal_font, bg="#334155", fg="white", insertbackground="white", width=25)
        self.entry_user.pack(pady=(5, 20), ipady=10)
        
        tk.Label(frame, text="Contraseña:", font=self.normal_font, bg="#1e293b", fg="white").pack(anchor="w")
        self.entry_pass = tk.Entry(frame, font=self.normal_font, bg="#334155", fg="white", insertbackground="white", width=25, show="*")
        self.entry_pass.pack(pady=(5, 30), ipady=10)
        
        btn_login = tk.Button(frame, text="INICIAR VIAJE", font=self.btn_font, bg="#0284c7", fg="white", 
                              activebackground="#0369a1", activeforeground="white", command=self.do_login, relief=tk.FLAT)
        btn_login.pack(fill=tk.X, ipady=15)

    def do_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        if not username or not password:
            messagebox.showwarning("Error", "Por favor ingresa usuario y contraseña")
            return
            
        try:
            response = requests.post(f"{SERVER_URL}/api/auth/conductor", json={
                "username": username,
                "password": password
            }, timeout=3.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.conductor_id = data["conductor_id"]
                    self.conductor_nombre = data["nombre"]
                    self.fetch_rutas_and_show_screen()
                else:
                    messagebox.showerror("Error", "Credenciales inválidas")
            else:
                messagebox.showerror("Error", "Credenciales inválidas o servidor caído")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "No se pudo conectar con el servidor central")

    def fetch_rutas_and_show_screen(self):
        try:
            response = requests.get(f"{SERVER_URL}/api/rutas", timeout=3.0)
            if response.status_code == 200:
                self.rutas_disponibles = response.json()
                self.show_route_selection_screen()
            else:
                messagebox.showerror("Error", "No se pudieron cargar las rutas.")
        except:
            messagebox.showerror("Error", "Error al conectar con el servidor para rutas.")

    def show_route_selection_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        frame = tk.Frame(self.root, bg="#1e293b", padx=50, pady=50)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text=f"Hola, {self.conductor_nombre}", font=self.title_font, bg="#1e293b", fg="white").pack(pady=(0, 10))
        tk.Label(frame, text="Selecciona tu destino actual", font=self.normal_font, bg="#1e293b", fg="#94a3b8").pack(pady=(0, 40))
        
        # Combobox para rutas
        rutas_nombres = [f"{r['origen']} -> {r['destino']}" for r in self.rutas_disponibles]
        
        self.combo_rutas = ttk.Combobox(frame, values=rutas_nombres, font=self.normal_font, state="readonly", width=30)
        self.combo_rutas.pack(pady=(5, 30))
        if rutas_nombres:
            self.combo_rutas.current(0)
            
        btn_start = tk.Button(frame, text="CONFIRMAR E INICIAR VIAJE", font=self.btn_font, bg="#10b981", fg="white", 
                              activebackground="#059669", activeforeground="white", command=self.start_trip_api, relief=tk.FLAT)
        btn_start.pack(fill=tk.X, ipady=15)

    def start_trip_api(self):
        idx = self.combo_rutas.current()
        if idx < 0:
            messagebox.showwarning("Aviso", "Selecciona una ruta válida")
            return
            
        ruta_seleccionada = self.rutas_disponibles[idx]
        self.ruta_id = ruta_seleccionada["id"]
        
        try:
            response = requests.post(f"{SERVER_URL}/api/trip/start", json={
                "conductor_id": self.conductor_id,
                "ruta_id": self.ruta_id
            }, timeout=3.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.sesion_id = data["sesion_id"]
                    
                    # Reproducir saludo por voz
                    try:
                        from app.copiloto.voice_assistant import VoiceAssistant
                        import random
                        va = VoiceAssistant()
                        destino = ruta_seleccionada.get("destino", "su destino")
                        horas = random.randint(1, 4)
                        minutos = random.randint(10, 50)
                        tiempo_estimado = f"{horas} horas y {minutos} minutos"
                        saludo = f"Hola {self.conductor_nombre}. Iniciando viaje hacia {destino}. El tiempo promedio de llegada es de {tiempo_estimado}. Te acompañaré en la ruta."
                        va.speak(saludo, force=True)
                    except Exception as e:
                        logging.error(f"Error al reproducir saludo: {e}")

                    self.show_dashboard_screen()
                else:
                    messagebox.showerror("Error", "Error al iniciar viaje en el servidor.")
            else:
                messagebox.showerror("Error", "Error en el servidor al crear sesión.")
        except:
            messagebox.showerror("Error", "No se pudo conectar con el servidor.")

    def show_dashboard_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Header
        header = tk.Frame(self.root, bg="#1e293b", height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"Buen viaje, {self.conductor_nombre}", font=self.normal_font, bg="#1e293b", fg="white").pack(side=tk.LEFT, padx=20, pady=20)
        
        btn_stop = tk.Button(header, text="FINALIZAR VIAJE", font=self.btn_font, bg="#e11d48", fg="white", 
                             activebackground="#be123c", activeforeground="white", command=self.stop_trip, relief=tk.FLAT)
        btn_stop.pack(side=tk.RIGHT, padx=20, pady=10, ipady=5, ipadx=10)

        # Body
        body = tk.Frame(self.root, bg="#0f172a")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Izquierda: Video
        left_panel = tk.Frame(body, bg="#1e293b", bd=2, relief=tk.RIDGE)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.lbl_video = tk.Label(left_panel, bg="black")
        self.lbl_video.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Derecha: Estado
        right_panel = tk.Frame(body, bg="#1e293b", width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="Estado CopIA", font=self.normal_font, bg="#1e293b", fg="#94a3b8").pack(pady=(20, 10))
        
        self.lbl_status_main = tk.Label(right_panel, text="INICIANDO...", font=self.title_font, bg="#1e293b", fg="white")
        self.lbl_status_main.pack(pady=20)
        
        self.lbl_metrics = tk.Label(right_panel, text="Cargando métricas...", font=self.normal_font, bg="#1e293b", fg="white", justify=tk.LEFT)
        self.lbl_metrics.pack(pady=20, anchor="w", padx=30)
        
        # Contenedor para botón de pánico
        panic_frame = tk.Frame(right_panel, bg="#1e293b")
        panic_frame.pack(pady=(20, 10), fill=tk.X, padx=20)
        
        self.canvas_panic = tk.Canvas(panic_frame, width=120, height=120, bg="#1e293b", highlightthickness=0)
        self.canvas_panic.pack(pady=5)
        
        self.circle_id = self.canvas_panic.create_oval(10, 10, 110, 110, fill="#dc2626", outline="#991b1b", width=3)
        self.text_id = self.canvas_panic.create_text(60, 60, text="🚨\nS.O.S", fill="white", font=("Helvetica", 16, "bold"), justify=tk.CENTER)
        
        self.canvas_panic.tag_bind(self.circle_id, "<Button-1>", self.on_panic_click)
        self.canvas_panic.tag_bind(self.text_id, "<Button-1>", self.on_panic_click)
        
        lbl_panic_desc = tk.Label(panic_frame, text="presionar en caso de robos", font=("Helvetica", 11, "italic"), bg="#1e293b", fg="#94a3b8")
        lbl_panic_desc.pack()
        
        # Iniciar hilos
        self.is_running = True
        self.start_copia()
        
    def on_panic_click(self, event):
        self.canvas_panic.itemconfig(self.circle_id, fill="#991b1b")
        self.root.after(200, lambda: self.canvas_panic.itemconfig(self.circle_id, fill="#dc2626"))
        self.send_panic()

    def send_panic(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/trip/panic", json={
                "conductor_id": self.conductor_id
            }, timeout=3.0)
            if response.status_code == 200:
                messagebox.showinfo("Alerta de Robo Enviada", "Se ha enviado una alerta de ROBO/ASALTO a la central.\nTu posición GPS actual está siendo rastreada.")
            else:
                messagebox.showerror("Error", "No se pudo enviar la alerta de pánico.")
        except:
            messagebox.showerror("Error", "Error de conexión al enviar pánico.")

    def start_copia(self):
        logging.info("Inicializando Motor de IA CopIA...")
        self.system = CopIASystem("config/copia_config.yaml", edge_mode=True)
        camera_index = self.system.config.get("camera_index", 1)
        
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se encontró cámara conectada.")
            self.stop_trip()
            return
            
        # Hilo de cámara (IA)
        threading.Thread(target=self.camera_worker, daemon=True).start()
        # Hilo de red
        threading.Thread(target=self.telemetry_worker, daemon=True).start()
        
        # Actualizador de UI
        self.update_ui_loop()

    def camera_worker(self):
        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
                
            processed_frame, log_data = self.system.process_frame(frame)
            
            # Guardar frame para la GUI
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            self.latest_frame = rgb_frame
            self.latest_log_data = log_data
            
            if log_data:
                # Comprimir para telemetría
                small_frame = cv2.resize(processed_frame, (640, 480))
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                ret_enc, buffer = cv2.imencode('.jpg', small_frame, encode_param)
                
                if ret_enc:
                    b64_str = base64.b64encode(buffer).decode('utf-8')
                    self.latest_payload = {
                        "conductor_id": self.conductor_id,
                        "log_data": log_data,
                        "snapshot_b64": b64_str,
                        "event_timestamp": get_peru_time().isoformat()
                    }
                    
    def telemetry_worker(self):
        telemetry_queue = []
        while self.is_running:
            if self.latest_payload:
                payload = self.latest_payload
                self.latest_payload = None
                
                # Encolar si hay alerta crítica
                is_critical = payload["log_data"].get("alert_level", 0) > 0 or payload["log_data"].get("event_type") in ["PÁNICO_EMERGENCIA", "ROBO_ASALTO"]
                if is_critical:
                    telemetry_queue.append(payload)
                else:
                    telemetry_queue.insert(0, payload)
                
                if len(telemetry_queue) > 1000:
                    telemetry_queue.pop(0)
                    
            if telemetry_queue:
                payload_to_send = telemetry_queue[0]
                try:
                    with requests.Session() as s:
                        resp = s.post(f"{SERVER_URL}/api/telemetry", json=payload_to_send, timeout=1.5)
                        if resp.status_code == 200:
                            telemetry_queue.pop(0)
                        else:
                            time.sleep(1)
                except Exception:
                    is_critical = payload_to_send["log_data"].get("alert_level", 0) > 0 or payload_to_send["log_data"].get("event_type") in ["PÁNICO_EMERGENCIA", "ROBO_ASALTO"]
                    if not is_critical:
                        telemetry_queue.pop(0)
                    else:
                        time.sleep(1)
            else:
                time.sleep(0.01)

    def update_ui_loop(self):
        if not self.is_running:
            return
            
        if self.latest_frame is not None:
            # Actualizar Video
            img = Image.fromarray(self.latest_frame)
            # Redimensionar para que encaje en el panel izquierdo (ej. 600x400)
            img = img.resize((600, 450), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lbl_video.imgtk = imgtk
            self.lbl_video.configure(image=imgtk)
            
        if self.latest_log_data is not None:
            # Actualizar Estado y Métricas
            data = self.latest_log_data
            risk = data.get("risk_score", 0)
            event = data.get("event_type", "normal").upper()
            
            if risk < 30:
                color = "#10b981" # Emerald
                text = "NORMAL"
            elif risk < 55:
                color = "#f59e0b" # Amber
                text = event
            elif risk < 75:
                color = "#f97316" # Orange
                text = event
            else:
                color = "#ef4444" # Red
                text = event
                
            self.lbl_status_main.config(text=text, fg=color)
            
            metrics_str = f"Riesgo: {risk:.1f}\n\n"
            metrics_str += f"Ojos (EAR): {data.get('ear', 0):.3f}\n"
            metrics_str += f"Boca (MAR): {data.get('mar', 0):.3f}\n"
            metrics_str += f"Inclinación: {data.get('pitch', 0):.1f}"
            self.lbl_metrics.config(text=metrics_str)
            
        self.root.after(30, self.update_ui_loop) # Actualizar a ~30 FPS

    def stop_trip(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.system:
            self.system.shutdown()
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = CopIAEdgeApp(root)
    root.mainloop()
