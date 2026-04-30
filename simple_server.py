from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str

# In-memory storage for demo
sessions = {}

def extract_health_values(text: str) -> dict:
    """Extract glucose, BMI, and age from text using regex"""
    values = {}
    
    # Extract glucose - updated to handle equals sign
    glucose_patterns = [
        r'glucose\s*=\s*(\d+(?:\.\d+)?)',
        r'glucose\s*(?:is\s*)?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*(?:mg/dl)?\s*glucose',
        r'glucose\s*(?:level\s*)?(\d+(?:\.\d+)?)'
    ]
    
    # Extract BMI - updated to handle equals sign
    bmi_patterns = [
        r'bmi\s*=\s*(\d+(?:\.\d+)?)',
        r'bmi\s*(?:is\s*)?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)\s*bmi',
        r'body\s*mass\s*index\s*(?:is\s*)?(\d+(?:\.\d+)?)'
    ]
    
    # Extract age - updated to handle equals sign
    age_patterns = [
        r'age\s*=\s*(\d+)',
        r'age\s*(?:is\s*)?(\d+)',
        r'(\d+)\s*(?:years?\s*)?old',
        r'i\s*am\s*(\d+)\s*(?:years?\s*)?old'
    ]
    
    for pattern in glucose_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['glucose'] = float(match.group(1))
            break
    
    for pattern in bmi_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['bmi'] = float(match.group(1))
            break
    
    for pattern in age_patterns:
        match = re.search(pattern, text.lower())
        if match:
            values['age'] = int(match.group(1))
            break
    
    return values

def ask_llm(user_message: str) -> str:
    """Get response from OpenAI API or fallback to mock responses"""
    try:
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful diabetes health assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to mock responses if API fails
        print(f"OpenAI API Error: {e}")
        if any(keyword in user_message.lower() for keyword in ["glucose", "bmi", "age"]):
            return "I've noted your health information. Please provide all three values (glucose, BMI, and age) to get a diabetes risk assessment."
        elif "risk" in user_message.lower():
            return "Based on your health metrics, I recommend consulting with a healthcare provider for personalized advice about diabetes management and prevention."
        else:
            return "I'm your diabetes health assistant. Please share your glucose level, BMI, and age for a risk assessment."

def predict_diabetes(glucose: float, bmi: float, age: int) -> str:
    """More accurate diabetes risk prediction based on medical guidelines"""
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "public", "index.html")
    return FileResponse(html_path)

@app.get("/api")
async def api_root():
    return {"message": "Simple server is working"}

@app.post("/chat")
@app.post("/api/chat")
async def chat(message: ChatMessage, session_id: str = "default"):
    """Handle chat messages and extract health data"""
    if session_id not in sessions:
        sessions[session_id] = {}
    
    # Extract health values from message
    extracted_values = extract_health_values(message.message)
    
    # If we found new values, clear the session and use only the new values
    if extracted_values:
        sessions[session_id] = extracted_values
    else:
        # Keep existing session data if no new values found
        pass
    
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
async def predict(health_data: dict):
    """Predict diabetes risk using actual health data"""
    glucose = health_data.get("glucose", 0)
    bmi = health_data.get("bmi", 0)
    age = health_data.get("age", 0)
    
    # Use the actual prediction function
    risk_level = predict_diabetes(glucose, bmi, age)
    
    # Generate explanation based on actual risk level
    if risk_level == "High Risk":
        explanation = f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a high risk of diabetes. I strongly recommend consulting with a healthcare provider immediately for proper diagnosis and management. Your elevated glucose level requires medical attention."
    elif risk_level == "Medium Risk":
        explanation = f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a moderate risk of diabetes. I recommend discussing these results with a healthcare provider and making lifestyle changes like improved diet and regular exercise to lower your risk."
    else:
        explanation = f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you appear to have a lower risk of diabetes. However, regular monitoring and healthy lifestyle choices are always recommended."
    
    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "input_data": {"glucose": glucose, "bmi": bmi, "age": age}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)
