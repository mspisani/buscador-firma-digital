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
        raise HTTPException(status_code=500, detail="Falta la API Key en el servidor.")
    
    try:
        # Usamos el modelo oficial de Gemini para una respuesta rápida y fluida
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        response = model.generate_content(request.prompt)
        return {"respuesta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en IA: {str(e)}") IA: {str(e)}")
