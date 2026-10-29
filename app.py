import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="Motor de Búsqueda - Firma Digital")

# CORREGIDO Y AUDITADO: allow_credentials en False para evitar conflictos con allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del Endpoint oficial de Gemini con el modelo gemini-1.5-flash
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = (
    "Sos un asistente técnico ultra conciso optimizado exclusivamente para Firma Digital, Certificados y Tokens USB "
    "(ePass2003, mToken criptoID, SafeNet, Athena) en Argentina. "
    "REGLAS OBLIGATORIAS DE RESPUESTA:\n"
    "1. Estructura: Sé directo. Usa subtítulos y diagramas de flujo lineales con emojis (ej: 🔌 -> 📥 -> ⚙️).\n"
    "2. Jerarquía de Enlaces: Priorizá e invitá siempre a descargar desde los canales oficiales del Estado Nacional "
    "(Argentina.gob.ar u ONTI). Ofrecé repositorios privados (como Encode S.A.) únicamente como alternativa secundaria.\n"
    "3. Formato: Formateá todos los enlaces en Markdown puro [Texto](URL) para que sean hipervínculos azules.\n"
    "4. No respondas nada fuera de este nicho cerrado."
)

class QueryRequest(BaseModel):
    prompt: str

async def call_gemini_with_retry(user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Falta configurar la API Key en el servidor de Render.")
        
    attempts = 3
    delay = 2.0
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nConsulta del usuario: {user_prompt}"}]}]
    }
    
    # Timeout ampliado a 45 segundos para tolerar la latencia inicial cuando Render despierta
    async with httpx.AsyncClient() as client:
        for attempt in range(attempts):
            try:
                response = await client.post(GEMINI_URL, json=payload, timeout=45.0)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                
                if response.status_code in (429, 503):
                    if attempt < attempts - 1:
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                
                raise HTTPException(status_code=response.status_code, detail="Error en la respuesta de la API de Gemini.")
                
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt < attempts - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                raise HTTPException(status_code=503, detail="Error de conexión permanente con la IA.")
                
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado.")

@app.post("/api/buscar")
async def buscar(request: QueryRequest):
    resultado = await call_gemini_with_retry(request.prompt)
    return {"respuesta": resultado}
