# 📋 Technical Specification Document

## 🎯 Project Overview

**Diabetes AI Assistant** - A modern web application providing personalized diabetes risk assessment using AI and machine learning.

### Business Requirements
- Provide accessible diabetes risk assessment
- Offer personalized health recommendations
- Maintain conversation context and natural flow
- Ensure data privacy and security
- Support mobile and desktop users

### Technical Requirements
- Real-time chat interface
- AI-powered health advice generation
- Session management for conversation context
- Responsive design for all devices
- Graceful fallback for service failures

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Chat UI       │  │   API Client    │  │   Session     │ │
│  │   (HTML/CSS/JS) │  │   (Fetch API)   │  │   Manager     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FastAPI       │  │   Session       │  │   Health      │ │
│  │   Application   │  │   Manager       │  │   Extractor   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Risk          │  │   AI Response   │  │   SSL Fix     │ │
│  │   Calculator    │  │   Generator     │  │   Handler     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ API Calls
┌─────────────────────────────────────────────────────────────┐
│                  External Services                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   OpenAI API    │  │   Vercel        │  │   SSL         │ │
│  │   (GPT-4o-mini) │  │   Platform      │  │   Certificates│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
User Input → Frontend Validation → API Request → Backend Processing → External Services
     ↓              ↓                 ↓                ↓                    ↓
Natural Language   Format Check      HTTP POST        Session Mgmt         OpenAI API
Processing         & Sanitization    to /api/chat     + Health Data         GPT-4o-mini
     ↓              ↓                 ↓                ↓                    ↓
Extracted Values   Loading State     JSON Response   Risk Calculation     AI Response
     ↓              ↓                 ↓                ↓                    ↓
Session Update     UI Animation      Status Code     Medical Guidelines   Personalized
     ↓              ↓                 ↓                ↓                    ↓
Chat Display      Error Handling    Response Format Risk Score          Health Advice
```

## 📊 Database Schema

### Session Management (In-Memory)

```python
# Session Structure
sessions = {
    "session_1234567890": {
        "glucose": 120.0,
        "bmi": 25.5,
        "age": 45,
        "last_updated": "2024-01-01T12:00:00Z"
    }
}

# Session Lifecycle
1. Create: session_<timestamp> on first interaction
2. Update: Add health data when extracted
3. Clear: Reset on non-health messages
4. Expire: Natural expiration (not implemented)
```

### API Request/Response Models

```python
# Pydantic Models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class HealthData(BaseModel):
    glucose: float
    bmi: float
    age: int

class RiskAssessment(BaseModel):
    risk_level: str
    explanation: str
    input_data: dict
```

## 🔧 API Specification

### Endpoints

#### 1. Health Check
```
GET /api
Response: {"message": "Simple server is working"}
```

#### 2. Chat Endpoint
```
POST /api/chat
Content-Type: application/json

Request Body:
{
    "message": "glucose=120, bmi=25, age=45",
    "session_id": "session_1234567890"
}

Response:
{
    "response": "I'll analyze your health data...",
    "extracted_data": {"glucose": 120.0, "bmi": 25.0, "age": 45},
    "session_data": {"glucose": 120.0, "bmi": 25.0, "age": 45},
    "ready_for_prediction": true
}
```

#### 3. Prediction Endpoint
```
POST /api/predict
Content-Type: application/json

Request Body:
{
    "glucose": 120.0,
    "bmi": 25.0,
    "age": 45
}

Response:
{
    "risk_level": "Low Risk",
    "explanation": "Based on your health metrics...",
    "input_data": {"glucose": 120.0, "bmi": 25.0, "age": 45}
}
```

#### 4. Static File Serving
```
GET /
Response: index.html (Frontend Application)
```

### Error Handling

| Error Code | Description | Response Format |
|-------------|-------------|-----------------|
| 400 | Invalid Input | `{"detail": "error message"}` |
| 422 | Validation Error | `{"detail": "validation details"}` |
| 500 | Server Error | `{"detail": "internal server error"}` |

## 🧠 AI Integration Details

### OpenAI Configuration

```python
# Model Parameters
model = "gpt-4o-mini"
temperature = 0.8  # Creativity/variety
top_p = 0.9        # Nucleus sampling
max_tokens = 150   # Response length
presence_penalty = 0.6  # Encourage new topics
frequency_penalty = 0.6 # Reduce repetition
```

### System Prompts

#### Chat System Prompt
```
You are a helpful diabetes health assistant. Be conversational, varied, and engaging. 
Avoid repetitive phrases. Mix up your responses with different greetings and approaches 
based on the age of the user. IMPORTANT: Maintain conversation context. If the user 
agrees to share health information, acknowledge their agreement and gently guide them 
to provide specific numbers (glucose, BMI, age). Don't keep asking the same question 
repeatedly. Continue the conversation naturally based on what they say.
```

#### Advice System Prompt
```
You are a knowledgeable diabetes health advisor providing personalized advice based on 
specific health metrics. Be varied and creative in your recommendations while maintaining 
medical accuracy. Avoid repetitive phrasing. Consider the age of the user in your 
recommendations.
```

### Fallback Strategy

```python
# Response Categories
greeting_responses = ["Hey there! I'm your diabetes health assistant...", ...]
agreement_responses = ["Great! Let's get started. What's your current glucose level?", ...]
general_responses = ["I'm your diabetes health assistant. How can I help you today?", ...]

# Selection Logic
if greeting_detected:
    return random.choice(greeting_responses)
elif agreement_detected:
    return random.choice(agreement_responses)
else:
    return random.choice(general_responses)
```

## 🔒 Security Specifications

### Authentication & Authorization
- **No user authentication** (public health tool)
- **Session-based** state management
- **API key protection** via environment variables

### Data Protection
- **No PII storage** - sessions are temporary
- **Environment variables** for sensitive data
- **HTTPS enforcement** in production
- **Input sanitization** for health data

### SSL Certificate Handling
```python
# macOS SSL Fix
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# OpenAI Client with SSL bypass
client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))
```

## 📱 Frontend Specifications

### UI Components

```javascript
// Core Components
├── Chat Container
│   ├── Message List
│   ├── Loading Indicator
│   └── Result Cards
├── Input Section
│   ├── Text Input
│   └── Send Button
└── Status Indicator
    ├── Session Data Display
    └── Progress Messages
```

### Responsive Design

```css
/* Breakpoints */
- Mobile: ≤768px (stacked layout)
- Desktop: >768px (horizontal layout)

/* Mobile Optimizations */
.input-container {
    flex-direction: column;
    width: 100%;
}

.input-field, .send-button {
    width: 100%;
    margin-bottom: 10px;
}
```

### State Management

```javascript
// Frontend State
let sessionId = 'session_' + Date.now();
let sessionData = {};
let isLoading = false;

// Message Types
- 'user': User messages
- 'assistant': AI responses
- 'result': Risk assessment results
```

## 🚀 Performance Specifications

### Response Time Targets
- **API Response**: <2 seconds
- **AI Response**: <5 seconds (with fallback)
- **UI Updates**: <100ms
- **Page Load**: <2 seconds

### Scalability Considerations
- **Session Storage**: In-memory (current) → Redis (future)
- **AI Caching**: Not implemented (future)
- **Load Balancing**: Vercel automatic (production)
- **Database**: Not required (current) → PostgreSQL (future)

### Monitoring & Logging
```python
# Debug Logging
print(f"DEBUG: API Key loaded: {bool(api_key)}")
print(f"DEBUG: Session data: {sessions[session_id]}")
print(f"DEBUG: Ready for prediction: {ready_for_prediction}")

# Error Logging
print(f"OpenAI API Error: {e}")
print(f"AI advice generation error: {e}")
```

## 🧪 Testing Specifications

### Test Categories

#### Unit Tests
```python
# Test Cases
- test_health_data_extraction()
- test_risk_calculation()
- test_session_management()
- test_ai_response_generation()
```

#### Integration Tests
```python
# API Endpoint Tests
- test_chat_endpoint()
- test_predict_endpoint()
- test_session_persistence()
- test_error_handling()
```

#### End-to-End Tests
```javascript
// User Flow Tests
- Complete health assessment flow
- Conversation context maintenance
- Mobile responsiveness
- Error recovery scenarios
```

### Test Data
```python
# Test Scenarios
test_cases = [
    {"input": "glucose=120, bmi=25, age=45", "expected": "Low Risk"},
    {"input": "glucose=130, bmi=30, age=55", "expected": "Medium Risk"},
    {"input": "glucose=140, bmi=35, age=65", "expected": "High Risk"},
]
```

## 📋 Deployment Specifications

### Environment Configuration

```bash
# Development
python simple_server.py
# Local server on http://127.0.0.1:8004

# Production (Vercel)
vercel --prod
# Serverless deployment with environment variables
```

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-proj-...

# Optional (future)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
```

### Build Process

```json
// vercel.json Configuration
{
  "version": 2,
  "builds": [
    {
      "src": "simple_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/simple_server.py"
    },
    {
      "src": "/(.*)",
      "dest": "/public/$1"
    }
  ]
}
```

## 🔮 Future Enhancements

### Planned Features
1. **User Authentication** - Account system for history tracking
2. **Database Storage** - PostgreSQL for persistent data
3. **Caching Layer** - Redis for session and AI response caching
4. **Advanced Analytics** - Health trends and insights
5. **Mobile App** - React Native application
6. **Integration APIs** - Health device connections
7. **Multi-language Support** - Internationalization
8. **Advanced AI Models** - Fine-tuned medical models

### Technical Debt
1. **Test Coverage** - Increase from 0% to 80%+
2. **Error Handling** - More comprehensive error scenarios
3. **Logging** - Structured logging with levels
4. **Documentation** - API documentation with Swagger
5. **Security** - Input validation and rate limiting
6. **Performance** - Response time optimization
7. **Accessibility** - WCAG 2.1 compliance
8. **Monitoring** - Application performance monitoring

---

*This technical specification provides a comprehensive overview of the Diabetes AI Assistant system architecture, implementation details, and future development plans.*
