import customtkinter as ctk
from google import genai
import threading
import os

GEMINI_KEY = os.environ.get("GEMINI_KEY")
MODEL_ID = "gemini-1.5-flash-latest"

client = None
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY.strip())

class AsistenteFlotante(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Overlay")
        self.geometry("320x480")
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.95)
        ctk.set_appearance_mode("Dark")
        self.crear_widgets()
    
        if not GEMINI_KEY:
            self.mostrar_error_config()

    def crear_widgets(self):
        self.lbl_status = ctk.CTkLabel(self, text="● SISTEMA LISTO", text_color="#2ecc71", font=("Roboto", 11, "bold"))
        self.lbl_status.pack(pady=(10, 0))

        self.chat_display = ctk.CTkTextbox(self, width=290, height=360, wrap="word")
        self.chat_display.pack(pady=10, padx=10)
        self.chat_display.insert("0.0", "SISTEMA: Conectado a Gemini 1.5 Flash.\n\n")
        self.chat_display.configure(state="disabled")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_message = ctk.CTkEntry(self.input_frame, placeholder_text="Escriba aquí...", width=230)
        self.entry_message.pack(side="left", padx=(5, 5))
        self.entry_message.bind("<Return>", self.iniciar_envio)

        self.btn_send = ctk.CTkButton(self.input_frame, text=">", width=40, command=self.iniciar_envio)
        self.btn_send.pack(side="right", padx=(0, 5))

    def mostrar_error_config(self):
        instrucciones = (
            "⚠️ ERROR DE CONFIGURACIÓN\n\n"
            "No se detectó la GEMINI_KEY.\n\n"
            "1. Consigue tu clave en:\nhttps://aistudio.google.com/app/apikey\n\n"
            "2. Configúrala como variable de entorno o en un archivo .env"
        )
        self.actualizar_chat(instrucciones)
        self.lbl_status.configure(text="● FALTA API KEY", text_color="#e74c3c")

    def iniciar_envio(self, event=None):
        user_input = self.entry_message.get()
        if not user_input: return
        
        if not client:
            self.actualizar_chat("\nSISTEMA: No puedo procesar sin la GEMINI_KEY.\n")
            return

        self.btn_send.configure(state="disabled")
        self.actualizar_chat(f"USUARIO: {user_input}\n")
        self.entry_message.delete(0, "end")
        self.lbl_status.configure(text="○ PROCESANDO...", text_color="#f1c40f")
        
        threading.Thread(target=self.consultar_ia, args=(user_input,), daemon=True).start()

    def consultar_ia(self, prompt):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            self.actualizar_chat(f"IA: {response.text}\n\n")
        except Exception as e:
            self.actualizar_chat(f"ERROR: {str(e)}\n")
        finally:
            self.btn_send.configure(state="normal")
            self.lbl_status.configure(text="● SISTEMA LISTO", text_color="#2ecc71")

    def actualizar_chat(self, texto):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", texto)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

if __name__ == "__main__":
    app = AsistenteFlotante()
    app.mainloop()
