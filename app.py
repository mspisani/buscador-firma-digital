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
    "Sos un asistente técnico conversacional, amigable, claro y ultra conciso especializado exclusivamente en Firma Digital, "
    "Certificados y Tokens USB (ePass2003, mToken criptoID, SafeNet, Athena) en Argentina. "
    "Respondé de forma fluida, natural y conversacional, usá diagramas de flujo lineales con emojis (ej: 🔌 -> 📥 -> ⚙️) "
    "y priorizá enlaces oficiales en Markdown [Texto](URL) a Argentina.gob.ar u ONTI."
)

class ChatRequest(BaseModel):
    history: list = []
    prompt: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Falta configurar la API Key en el servidor de Render.")
    
    try:
        # Detectamos automáticamente qué modelo soporta generación de contenido con tu clave actual
        modelo_activo = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelo_activo = m.name
                break
        
        if not modelo_activo:
            modelo_activo = "gemini-pro" # Fallback por seguridad

        model = genai.GenerativeModel(
            model_name=modelo_activo,
            system_instruction=SYSTEM_PROMPT
        )
        
        response = model.generate_content(request.prompt)
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Gemini devolvió una respuesta vacía.")
            
        return {"respuesta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno de IA: {str(e)}")
        return {"respuesta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno de IA: {str(e)}")
