import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
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
    "Mantené una conversación fluida, recordá el contexto de lo que el usuario te viene consultando, "
    "usá diagramas de flujo lineales con emojis (ej: 🔌 -> 📥 -> ⚙️) cuando sea útil, y priorizá siempre "
    "enlaces oficiales en Markdown [Texto](URL) a Argentina.gob.ar u ONTI."
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    prompt: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Falta la API Key en el servidor.")
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        # Formatear el historial previo para que el chat recuerde la charla
        formatted_history = []
        for msg in request.history:
            role = "user" if msg.role == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg.content]})
            
        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(request.prompt)
        
        return {"respuesta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de Google AI: {str(e)}")
