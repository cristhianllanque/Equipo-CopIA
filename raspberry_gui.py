import cv2
import json
import base64
import requests
import time
import threading
import logging
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from app.core.copia_system import CopIASystem

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] CopIA Edge GUI: %(message)s")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

def get_peru_time():
    return datetime.now(pytz.timezone("America/Lima")).replace(tzinfo=None)

# Configuración global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CopIAEdgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CopIA Edge Monitor")
        self.root.geometry("1024x600")
        
        # Estado de sesión
        self.conductor_id = None
        self.conductor_nombre = None
        self.sesion_id = None
        self.ruta_id = None
        self.rutas_disponibles = []
        self.selected_camera = 0
        
        # IA y Cámara
        self.system = None
        self.cap = None
        self.is_running = False
        self.latest_payload = None
        self.latest_frame = None
        self.latest_log_data = None
        
        self.show_login_screen()
        
    def show_login_screen(self):
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Contenedor central (Estilo Tarjeta Moderna)
        frame = ctk.CTkFrame(master=self.root, width=450, height=500, corner_radius=20, fg_color="#1e293b")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        lbl_title = ctk.CTkLabel(master=frame, text="Transportes Veloz", font=("Helvetica", 32, "bold"), text_color="#38bdf8")
        lbl_title.place(relx=0.5, y=60, anchor=tk.CENTER)
        
        lbl_sub = ctk.CTkLabel(master=frame, text="CopIA Edge - Terminal Integrada", font=("Helvetica", 16), text_color="#94a3b8")
        lbl_sub.place(relx=0.5, y=100, anchor=tk.CENTER)
        
        self.entry_user = ctk.CTkEntry(master=frame, width=320, height=50, placeholder_text="ID Conductor", corner_radius=10, font=("Helvetica", 18), fg_color="#334155", border_color="#475569")
        self.entry_user.place(relx=0.5, y=190, anchor=tk.CENTER)
        
        self.entry_pass = ctk.CTkEntry(master=frame, width=320, height=50, placeholder_text="Contraseña", show="*", corner_radius=10, font=("Helvetica", 18), fg_color="#334155", border_color="#475569")
        self.entry_pass.place(relx=0.5, y=270, anchor=tk.CENTER)
        
        btn_login = ctk.CTkButton(master=frame, text="INICIAR VIAJE", width=320, height=60, font=("Helvetica", 20, "bold"), 
                                  corner_radius=12, command=self.do_login, fg_color="#0284c7", hover_color="#0369a1")
        btn_login.place(relx=0.5, y=380, anchor=tk.CENTER)

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
            
        frame = ctk.CTkFrame(master=self.root, width=550, height=480, corner_radius=20, fg_color="#1e293b")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        lbl_welcome = ctk.CTkLabel(master=frame, text=f"Hola, {self.conductor_nombre}", font=("Helvetica", 28, "bold"), text_color="white")
        lbl_welcome.place(relx=0.5, y=50, anchor=tk.CENTER)
        
        lbl_sub = ctk.CTkLabel(master=frame, text="Selecciona tu destino actual para continuar", font=("Helvetica", 16), text_color="#94a3b8")
        lbl_sub.place(relx=0.5, y=95, anchor=tk.CENTER)
        
        rutas_nombres = [f"{r['origen']} -> {r['destino']}" for r in self.rutas_disponibles]
        
        self.combo_rutas = ctk.CTkComboBox(master=frame, values=rutas_nombres, width=380, height=50, font=("Helvetica", 18), 
                                           dropdown_font=("Helvetica", 16), corner_radius=10, fg_color="#334155", button_color="#0284c7", border_color="#475569")
        self.combo_rutas.place(relx=0.5, y=170, anchor=tk.CENTER)
        
        if rutas_nombres:
            self.combo_rutas.set(rutas_nombres[0])
            
        lbl_cam = ctk.CTkLabel(master=frame, text="Cámara de Monitoreo:", font=("Helvetica", 16), text_color="#94a3b8")
        lbl_cam.place(relx=0.5, y=240, anchor=tk.CENTER)
        
        camaras_disponibles = ["Cámara 0 (Integrada)", "Cámara 1 (Externa USB)", "Cámara 2", "Cámara 3"]
        self.combo_cam = ctk.CTkComboBox(master=frame, values=camaras_disponibles, width=380, height=50, font=("Helvetica", 16), 
                                         dropdown_font=("Helvetica", 14), corner_radius=10, fg_color="#334155", button_color="#10b981", border_color="#475569")
        self.combo_cam.place(relx=0.5, y=285, anchor=tk.CENTER)
        self.combo_cam.set("Cámara 0 (Integrada)")
            
        btn_start = ctk.CTkButton(master=frame, text="CONFIRMAR E INICIAR VIAJE", width=380, height=60, font=("Helvetica", 18, "bold"), 
                                  corner_radius=12, command=self.start_trip_api, fg_color="#10b981", hover_color="#059669")
        btn_start.place(relx=0.5, y=390, anchor=tk.CENTER)

    def start_trip_api(self):
        # Encontrar índice de la ruta seleccionada
        ruta_str = self.combo_rutas.get()
        if not ruta_str:
            return
            
        # Extraer índice de cámara seleccionada
        cam_str = getattr(self, "combo_cam", None)
        if cam_str:
            try:
                self.selected_camera = int(cam_str.get().split(" ")[1])
            except Exception:
                self.selected_camera = 0
            
        idx = next((i for i, r in enumerate(self.rutas_disponibles) if f"{r['origen']} -> {r['destino']}" == ruta_str), -1)
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
            
        # Header Moderno
        header = ctk.CTkFrame(master=self.root, height=70, corner_radius=0, fg_color="#1e293b")
        header.pack(fill=tk.X, side=tk.TOP)
        
        lbl_driver = ctk.CTkLabel(master=header, text=f"Vehículo Activo • Conductor: {self.conductor_nombre}", font=("Helvetica", 16, "bold"), text_color="white")
        lbl_driver.pack(side=tk.LEFT, padx=20, pady=20)
        
        btn_stop = ctk.CTkButton(master=header, text="FINALIZAR VIAJE", width=150, height=40, font=("Helvetica", 14, "bold"), 
                                 corner_radius=8, command=self.stop_trip, fg_color="#e11d48", hover_color="#be123c")
        btn_stop.pack(side=tk.RIGHT, padx=20, pady=15)

        # Body - Dos columnas
        body = ctk.CTkFrame(master=self.root, fg_color="#0f172a", corner_radius=0)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Izquierda: Monitor de Video
        left_panel = ctk.CTkFrame(master=body, corner_radius=15, fg_color="#1e293b", border_width=2, border_color="#334155")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.lbl_video = tk.Label(left_panel, bg="black")
        self.lbl_video.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Derecha: Panel de Telemetría
        right_panel = ctk.CTkFrame(master=body, width=320, corner_radius=15, fg_color="#1e293b")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        lbl_status_title = ctk.CTkLabel(master=right_panel, text="Estado CopIA AI", font=("Helvetica", 14), text_color="#94a3b8")
        lbl_status_title.pack(pady=(20, 5))
        
        self.lbl_status_main = ctk.CTkLabel(master=right_panel, text="INICIANDO...", font=("Helvetica", 32, "bold"), text_color="white")
        self.lbl_status_main.pack(pady=(0, 30))
        
        # Grid de Métricas
        metrics_frame = ctk.CTkFrame(master=right_panel, fg_color="transparent")
        metrics_frame.pack(fill=tk.X, padx=20)
        
        # EAR (Ojos)
        self.lbl_ear = ctk.CTkLabel(master=metrics_frame, text="EAR (Ojos): 0.000", font=("Consolas", 16), text_color="white")
        self.lbl_ear.pack(anchor="w", pady=5)
        # MAR (Boca)
        self.lbl_mar = ctk.CTkLabel(master=metrics_frame, text="MAR (Boca): 0.000", font=("Consolas", 16), text_color="white")
        self.lbl_mar.pack(anchor="w", pady=5)
        # PITCH (Cabeza)
        self.lbl_pitch = ctk.CTkLabel(master=metrics_frame, text="Inclinación: 0.0°", font=("Consolas", 16), text_color="white")
        self.lbl_pitch.pack(anchor="w", pady=5)
        # RIESGO
        self.lbl_risk = ctk.CTkLabel(master=metrics_frame, text="Riesgo: 0%", font=("Helvetica", 18, "bold"), text_color="#38bdf8")
        self.lbl_risk.pack(anchor="w", pady=(15, 0))
        
        # Botón de Pánico
        panic_btn = ctk.CTkButton(master=right_panel, text="🚨 S.O.S", width=250, height=80, font=("Helvetica", 32, "bold"),
                                  corner_radius=40, fg_color="#dc2626", hover_color="#991b1b", command=self.send_panic)
        panic_btn.pack(side=tk.BOTTOM, pady=(0, 40))
        
        lbl_panic_desc = ctk.CTkLabel(master=right_panel, text="Emergencia (Asalto/Robo)", font=("Helvetica", 12), text_color="#94a3b8")
        lbl_panic_desc.pack(side=tk.BOTTOM, pady=(0, 10))
        
        # Iniciar hilos
        self.is_running = True
        self.start_copia()
        
    def send_panic(self):
        try:
            response = requests.post(f"{SERVER_URL}/api/trip/panic", json={
                "conductor_id": self.conductor_id
            }, timeout=3.0)
            if response.status_code == 200:
                messagebox.showinfo("Alerta S.O.S", "Alerta de ROBO/ASALTO enviada a la central.\nRastreo GPS en tiempo real activado.")
            else:
                messagebox.showerror("Error", "No se pudo enviar la alerta de pánico.")
        except:
            messagebox.showerror("Error", "Error de conexión al enviar pánico.")

    def start_copia(self):
        logging.info("Inicializando Motor de IA CopIA...")
        self.system = CopIASystem("config/copia_config.yaml", edge_mode=True)
        camera_index = getattr(self, "selected_camera", 0)
        
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
            try:
                img = Image.fromarray(self.latest_frame)
                # Redimensionar para que encaje
                img = img.resize((660, 480), Image.LANCZOS)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_video.imgtk = imgtk
                self.lbl_video.configure(image=imgtk)
            except Exception as e:
                pass
            
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
                
            self.lbl_status_main.configure(text=text, text_color=color)
            
            self.lbl_ear.configure(text=f"EAR (Ojos): {data.get('ear', 0):.3f}")
            self.lbl_mar.configure(text=f"MAR (Boca): {data.get('mar', 0):.3f}")
            self.lbl_pitch.configure(text=f"Inclinación: {data.get('pitch', 0):.1f}°")
            
            risk_color = "#38bdf8"
            if risk > 50:
                risk_color = "#ef4444"
            self.lbl_risk.configure(text=f"Riesgo Actual: {risk:.0f}%", text_color=risk_color)
            
        self.root.after(30, self.update_ui_loop) # Actualizar a ~30 FPS

    def stop_trip(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        if self.system:
            self.system.shutdown()
        self.show_login_screen()

if __name__ == "__main__":
    root = ctk.CTk()
    app = CopIAEdgeApp(root)
    root.mainloop()
