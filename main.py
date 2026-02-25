from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

app = FastAPI()

# Cho phép Frontend truy cập vào Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key="YOUR_GEMINI_API_KEY")

@app.post("/ask")
async def ask_gemini(data: dict):
    user_message = data.get("message")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(user_message)
    return {"reply": response.text}