import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "Sos un asistente técnico ultra conciso optimizado exclusivamente para Firma Digital, Certificados y Tokens USB "
    "(ePass2003, mToken criptoID, SafeNet, Athena) en Argentina. "
    "REGLAS OBLIGATORIAS DE RESPUESTA:\n"
    "1. Estructura: Sé directo. Usa subtítulos y diagramas de flujo lineales con emojis (ej: 🔌 -> 📥 -> ⚙️).\n"
    "2. Jerarquía de Enlaces: Priorizá e invitá siempre a descargar desde los canales oficiales del Estado Nacional "
    "(Argentina.gob.ar u ONTI).\n"
    "3. Formato: Formateá todos los enlaces en Markdown puro [Texto](URL).\n"
    "4. No respondas nada fuera de este nicho cerrado."
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/api/buscar")
async def buscar(request: QueryRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Falta la API Key en el servidor de Render.")
    
    try:
        # Usamos exactamente el modelo requerido por tu cuenta de Google
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        response = model.generate_content(request.prompt)
        return {"respuesta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de Google AI: {str(e)}")
