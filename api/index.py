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

def ask_llm(user_message: str) -> str:
    """Get response from OpenAI or return mock response"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful diabetes health assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # Mock responses for testing when API is down
        if any(keyword in user_message.lower() for keyword in ["glucose", "bmi", "age"]):
            return "I've noted your health information. Please provide all three values (glucose, BMI, and age) to get a diabetes risk assessment."
        elif "risk" in user_message.lower():
            return "Based on your health metrics, I recommend consulting with a healthcare provider for personalized advice about diabetes management and prevention."
        else:
            return "I'm currently in offline mode, but I can still help track your health data. Please share your glucose level, BMI, and age for a risk assessment."

def predict_diabetes(glucose: float, bmi: float, age: int) -> str:
    """Predict diabetes risk using the trained model"""
    try:
        # Try to load the pickle file
        with open("diabetes_model.pkl", "rb") as f:
            model = pickle.load(f)
        
        prediction = model.predict([[glucose, bmi, age]])[0]
        return "High Risk" if prediction == 1 else "Low Risk"
    except FileNotFoundError:
        # Fallback simple prediction if model file doesn't exist
        if glucose > 126 or bmi > 30 or age > 45:
            return "High Risk"
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
    
    return {
        "response": response,
        "extracted_data": extracted_values,
        "session_data": sessions[session_id],
        "ready_for_prediction": len(sessions[session_id]) == 3
    }

@app.post("/predict")
@app.post("/api/predict")
async def predict(health_data: HealthData):
    """Predict diabetes risk from health data"""
    try:
        result = predict_diabetes(health_data.glucose, health_data.bmi, health_data.age)
        
        # Get explanation from AI
        explanation = ask_llm(
            f"A patient has {result} diabetes risk with glucose: {health_data.glucose}, BMI: {health_data.bmi}, age: {health_data.age}. Explain what this means and give advice."
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
