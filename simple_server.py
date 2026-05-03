from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv
import ssl
import sys
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

print("=== DEBUG: API Key loaded: Yes ===")
print(f"=== DEBUG: API Key starts with: {api_key[:10]}... ===")

# Fix SSL certificate verification issue on macOS
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Initialize OpenAI client with SSL verification disabled
import httpx
client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False)) if api_key else None

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
    if not client:
        # No API key available - use smart fallback
        msg_lower = user_message.lower()
        if any(greeting in msg_lower for greeting in ["hi", "hello", "hey", "good morning", "good evening"]):
            return "Hello! I'm your diabetes health assistant. Please share your glucose level, BMI, and age for a risk assessment."
        elif any(health_term in msg_lower for health_term in ["glucose", "bmi", "age", "blood sugar", "diabetes", "risk"]):
            return "I can help with diabetes risk assessment. Please provide your glucose level, BMI, and age so I can give you a personalized evaluation."
        else:
            return "I'm your diabetes health assistant. Please share your glucose level, BMI, and age for a risk assessment."
    
    try:
        print(f"DEBUG: Attempting OpenAI API call...")
        print(f"DEBUG: Client exists: {client is not None}")
        print(f"DEBUG: API key starts with: {api_key[:10] if api_key else 'None'}...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful diabetes health assistant. Be conversational, varied, and engaging. Avoid repetitive phrases. Mix up your responses with different greetings and approaches based on the age of the user. IMPORTANT: Maintain conversation context. If the user agrees to share health information, acknowledge their agreement and gently guide them to provide specific numbers (glucose, BMI, age). Don't keep asking the same question repeatedly. Continue the conversation naturally based on what they say."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            top_p=0.9,
            max_tokens=150,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        print(f"DEBUG: OpenAI API call successful")
        return response.choices[0].message.content
    except Exception as e:
        # Dynamic fallback responses when API fails
        print(f"DEBUG: OpenAI API Error Type: {type(e).__name__}")
        print(f"DEBUG: OpenAI API Error: {e}")
        print(f"DEBUG: API Key valid: {api_key and api_key.startswith('sk-')}")
        print(f"DEBUG: API Key length: {len(api_key) if api_key else 0}")
        msg_lower = user_message.lower()
        
        import random
        greeting_responses = [
            "Hey there! I'm your diabetes health assistant. Ready to check your health numbers?",
            "Hi! I'm here to help with diabetes risk assessment. What are your glucose, BMI, and age?",
            "Hello! Let's assess your diabetes health together. Can you share your health metrics?",
            "Hey! I'm your diabetes health assistant. What are your current health numbers?",
            "Hi there! Ready to evaluate your diabetes risk? I'll need your glucose, BMI, and age."
        ]
        
        # Context-aware responses for when user agrees or is ready
        agreement_responses = [
            "Great! Let's get started. What's your current glucose level?",
            "Perfect! Let me know your glucose, BMI, and age when you're ready.",
            "Excellent! Let's start with your glucose level - what is it?",
            "Great! I'll need your health numbers. What's your glucose level first?",
            "Perfect! Let's begin the assessment. What's your current glucose reading?"
        ]
        
        # Context-aware responses for general conversation
        general_responses = [
            "I'm your diabetes health assistant. How can I help you today?",
            "Hello! I'm here to help with diabetes health monitoring. What would you like to know?",
            "Hi! I can provide diabetes risk assessment and health guidance. What's on your mind?",
            "Hey! I'm your diabetes health assistant. Feel free to ask me anything about diabetes health.",
            "Hello! I'm here to help with diabetes evaluation and health advice. How can I assist you?"
        ]
        
        if any(greeting in msg_lower for greeting in ["hi", "hello", "hey", "good morning", "good evening"]):
            return random.choice(greeting_responses)
        elif any(agreement in msg_lower for agreement in ["sure", "okay", "ok", "yes", "yeah", "alright", "sounds good", "ready", "let's do it", "of course"]):
            return random.choice(agreement_responses)
        elif any(health_term in msg_lower for health_term in ["glucose", "bmi", "age", "blood sugar", "diabetes", "risk"]):
            return random.choice(general_responses)
        else:
            return random.choice(general_responses)

def generate_dynamic_advice(glucose: float, bmi: float, age: int, risk_level: str) -> str:
    """Generate personalized advice using AI based on specific health metrics"""
    if not client:
        # Fallback to static advice if no AI client
        if risk_level == "High Risk":
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a high risk of diabetes. I strongly recommend consulting with a healthcare provider immediately for proper diagnosis and management. Your elevated glucose level requires medical attention."
        elif risk_level == "Medium Risk":
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a moderate risk of diabetes. I recommend discussing these results with a healthcare provider and making lifestyle changes like improved diet and regular exercise to lower your risk."
        else:
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you appear to have a lower risk of diabetes. However, regular monitoring and healthy lifestyle choices are always recommended."
    
    try:
        prompt = f"""
        Based on these specific health metrics:
        - Glucose: {glucose} mg/dL
        - BMI: {bmi} kg/m²  
        - Age: {age} years
        - Risk Level: {risk_level}
        
        Provide personalized, actionable advice for diabetes management. Consider:
        1. The specific glucose level and what it means
        2. The BMI category and its implications
        3. Age-related risk factors
        4. Concrete lifestyle recommendations
        5. When to seek medical attention
        
        Keep it concise (2-3 sentences) but specific to their numbers.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a knowledgeable diabetes health advisor providing personalized advice based on specific health metrics. Be varied and creative in your recommendations while maintaining medical accuracy. Avoid repetitive phrasing. Consider the age of the user in your recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            top_p=0.95,
            max_tokens=200,
            presence_penalty=0.7,
            frequency_penalty=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI advice generation error: {e}")
        # Fallback to static advice
        if risk_level == "High Risk":
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a high risk of diabetes. I strongly recommend consulting with a healthcare provider immediately for proper diagnosis and management."
        elif risk_level == "Medium Risk":
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a moderate risk of diabetes. I recommend discussing these results with a healthcare provider and making lifestyle changes."
        else:
            return f"Based on your health metrics (glucose: {glucose}, BMI: {bmi}, age: {age}), you have a lower risk of diabetes. Continue maintaining healthy lifestyle choices."

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
    
    # If no health data extracted, clear session to prevent old data from triggering prediction
    if not extracted_values:
        print(f"DEBUG: No health data found in '{message.message}', clearing session {session_id}")
        sessions[session_id] = {}
    else:
        print(f"DEBUG: Found health data in '{message.message}': {extracted_values}")
        sessions[session_id].update(extracted_values)
    
    # Get AI response
    response = ask_llm(message.message)
    
    # Only mark as ready for prediction if we have actual numeric values for all 3 metrics
    has_glucose = sessions[session_id].get('glucose') is not None and sessions[session_id].get('glucose') > 0
    has_bmi = sessions[session_id].get('bmi') is not None and sessions[session_id].get('bmi') > 0
    has_age = sessions[session_id].get('age') is not None and sessions[session_id].get('age') > 0
    
    ready_for_prediction = has_glucose and has_bmi and has_age
    print(f"DEBUG: Session data: {sessions[session_id]}")
    print(f"DEBUG: Ready for prediction: {ready_for_prediction}")
    
    return {
        "response": response,
        "extracted_data": extracted_values,
        "session_data": sessions[session_id],
        "ready_for_prediction": ready_for_prediction
    }

@app.post("/predict")
@app.post("/api/predict")
async def predict(health_data: dict):
    """Predict diabetes risk using actual health data"""
    glucose = health_data.get("glucose", 0)
    bmi = health_data.get("bmi", 0)
    age = health_data.get("age", 0)
    
    # Validate health data before processing
    if not glucose or not bmi or not age:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Valid glucose, BMI, and age values are required")
    
    if glucose <= 0 or bmi <= 0 or age <= 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Health values must be positive numbers")
    
    # Use the actual prediction function
    risk_level = predict_diabetes(glucose, bmi, age)
    
    # Generate dynamic AI advice based on specific health data
    explanation = generate_dynamic_advice(glucose, bmi, age, risk_level)
    
    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "input_data": {"glucose": glucose, "bmi": bmi, "age": age}
    }

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        print("=== Testing OpenAI Connection ===")
        print(f"DEBUG: Testing basic network connectivity...")
        
        # Test basic connectivity first
        import requests
        try:
            response = requests.get("https://api.openai.com/", timeout=5, verify=False)
            print(f"DEBUG: OpenAI base URL reachable: {response.status_code}")
        except Exception as net_e:
            print(f"❌ Network Error: {net_e}")
            return False
        
        print(f"DEBUG: API Key loaded: {api_key[:10] if api_key else 'None'}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10,
            timeout=10
        )
        print(f"✅ OpenAI Connection Successful: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Connection Failed: {type(e).__name__}: {e}")
        print(f"DEBUG: This might be a network/firewall issue")
        return False

if __name__ == "__main__":
    import uvicorn
    # Test OpenAI connection before starting server
    test_openai_connection()
    uvicorn.run(app, host="127.0.0.1", port=8004)
