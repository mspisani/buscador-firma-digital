import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

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
        raise HTTPException(status_code=500, detail="Error crítico: La variable GEMINI_API_KEY no está configurada en Render.")
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nConsulta del usuario: {request.prompt}"}]}]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GEMINI_URL, json=payload, timeout=40.0)
            
            # Si Gemini rechaza la clave o hay un error de cuota, devolvemos el detalle exacto
            if response.status_code != 200:
                error_detalle = response.json().get("error", {}).get("message", "Error desconocido de la API de Gemini")
                raise HTTPException(status_code=500, detail=f"Google API Error: {error_detalle}")
                
            data = response.json()
            return {"respuesta": data["candidates"][0]["content"]["parts"][0]["text"]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Excepción interna en servidor: {str(e)}")
