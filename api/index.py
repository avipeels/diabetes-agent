from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import pickle
import os
from openai import OpenAI
import re

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
client = OpenAI(api_key=api_key)

# Pydantic models
class HealthData(BaseModel):
    glucose: float
    bmi: float
    age: int

class ChatMessage(BaseModel):
    message: str

class HealthSession(BaseModel):
    data: dict

# In-memory storage for demo (in production, use a database)
sessions = {}

def extract_health_values(text: str) -> dict:
    """Extract glucose, BMI, and age from text using regex"""
    values = {}
    
    # Extract glucose (numbers in context of glucose)
    glucose_patterns = [
        r'glucose\s*=\s*(\d+(?:\.\d+)?)',
        r'glucose\s*(?:is\s*)?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*(?:mg/dl)?\s*glucose',
        r'glucose\s*(?:level\s*)?(\d+(?:\.\d+)?)'
    ]
    
    # Extract BMI
    bmi_patterns = [
        r'bmi\s*=\s*(\d+(?:\.\d+)?)',
        r'bmi\s*(?:is\s*)?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*bmi',
        r'body\s*mass\s*index\s*(?:is\s*)?(\d+(?:\.\d+)?)'
    ]
    
    # Extract age
    age_patterns = [
        r'age\s*=\s*(\d+)',
        r'age\s*(?:is\s*)?(\d+)',
        r'(\d+)\s*(?:years?\s*)?old',
        r'i\s*am\s*(\d+)\s*(?:years?\s*)?old'
    ]
    
    # Try to extract glucose
    for pattern in glucose_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['glucose'] = float(match.group(1))
            break
    
    # Try to extract BMI
    for pattern in bmi_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['bmi'] = float(match.group(1))
            break
    
    # Try to extract age
    for pattern in age_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['age'] = int(match.group(1))
            break
    
    return values

def ask_llm(user_message):
    """Get response from OpenAI or return mock response"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful diabetes health assistant. Always respond professionally and helpfully. If the user sends greetings or general questions, respond appropriately. If they share health information, acknowledge it and guide them to provide glucose, BMI, and age for a risk assessment."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        # Smart fallback based on message content
        msg_lower = user_message.lower()
        if any(greeting in msg_lower for greeting in ["hi", "hello", "hey", "good morning", "good evening"]):
            return "Hello! I'm your diabetes health assistant. Please share your glucose level, BMI, and age for a risk assessment."
        elif any(health_term in msg_lower for health_term in ["glucose", "bmi", "age", "blood sugar", "diabetes", "risk"]):
            return "I can help with diabetes risk assessment. Please provide your glucose level, BMI, and age so I can give you a personalized evaluation."
        else:
            return "I'm your diabetes health assistant. Please share your glucose level, BMI, and age for a risk assessment."

def predict_diabetes(glucose: float, bmi: float, age: int) -> str:
    """Predict diabetes risk using deterministic medical thresholds"""
    risk_score = 0

    # Glucose risk (most important factor)
    if glucose >= 126:
        risk_score += 3  # Diabetes range
    elif glucose >= 100:
        risk_score += 2  # Prediabetes range
    elif glucose >= 90:
        risk_score += 1  # Elevated normal

    # BMI risk
    if bmi >= 30:
        risk_score += 2  # Obese
    elif bmi >= 25:
        risk_score += 1  # Overweight

    # Age risk
    if age >= 65:
        risk_score += 2  # Higher age risk
    elif age >= 45:
        risk_score += 1  # Moderate age risk

    # Determine risk level
    if risk_score >= 5:
        return "High Risk"
    elif risk_score >= 3:
        return "Medium Risk"
    else:
        return "Low Risk"

@app.get("/")
async def root():
    # This route should not be called since Vercel serves static files directly
    # But keeping it as a fallback
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head><title>Diabetes AI Assistant</title></head>
        <body>
            <h1>Diabetes AI Assistant</h1>
            <p>Please visit the main page at <a href="/index.html">/index.html</a></p>
        </body>
        </html>
        """,
        status_code=200
    )

@app.get("/api")
async def api_root():
    return {"message": "Diabetes AI Assistant API"}

@app.post("/chat")
@app.post("/api/chat")
async def chat(message: ChatMessage, session_id: str = "default"):
    """Handle chat messages and extract health data"""
    if session_id not in sessions:
        sessions[session_id] = {}
    
    # Extract health values from message
    extracted_values = extract_health_values(message.message)
    sessions[session_id].update(extracted_values)
    
    # Get AI response
    response = ask_llm(message.message)
    
    # Only mark as ready for prediction if we have actual numeric values for all 3 metrics
    has_glucose = sessions[session_id].get('glucose') is not None and sessions[session_id].get('glucose') > 0
    has_bmi = sessions[session_id].get('bmi') is not None and sessions[session_id].get('bmi') > 0
    has_age = sessions[session_id].get('age') is not None and sessions[session_id].get('age') > 0
    
    return {
        "response": response,
        "extracted_data": extracted_values,
        "session_data": sessions[session_id],
        "ready_for_prediction": has_glucose and has_bmi and has_age
    }

@app.post("/predict")
@app.post("/api/predict")
async def predict(health_data: HealthData):
    """Predict diabetes risk from health data"""
    # Validate health data before processing
    if not health_data.glucose or not health_data.bmi or not health_data.age:
        raise HTTPException(status_code=400, detail="Valid glucose, BMI, and age values are required")
    
    if health_data.glucose <= 0 or health_data.bmi <= 0 or health_data.age <= 0:
        raise HTTPException(status_code=400, detail="Health values must be positive numbers")
    
    try:
        result = predict_diabetes(health_data.glucose, health_data.bmi, health_data.age)
        # Deterministic explanation (avoid re-asking for values on API errors)
        if result == "High Risk":
            explanation = (
                "Your metrics indicate a high risk of diabetes. "
                "Please consult a healthcare provider promptly for diagnosis and management. "
                "Focus on glucose control, balanced diet, and regular activity."
            )
        elif result == "Medium Risk":
            explanation = (
                "You have a moderate risk of diabetes. "
                "Discuss with a healthcare provider and adopt lifestyle changes: balanced diet, "
                "regular exercise, weight management, and routine monitoring."
            )
        else:
            explanation = (
                "Your metrics suggest a lower risk. "
                "Maintain a healthy lifestyle, keep regular checkups, and monitor glucose as advised."
            )

        return {
            "risk_level": result,
            "explanation": explanation,
            "input_data": {
                "glucose": health_data.glucose,
                "bmi": health_data.bmi,
                "age": health_data.age
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session data"""
    if session_id not in sessions:
        sessions[session_id] = {}
    
    return {
        "session_id": session_id,
        "data": sessions[session_id],
        "ready_for_prediction": len(sessions[session_id]) == 3
    }

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data"""
    if session_id in sessions:
        sessions[session_id] = {}
    
    return {"message": "Session cleared"}
