# 🧠 Diabetes AI Assistant

A modern web application that provides personalized diabetes risk assessment using AI and machine learning.

## 🚀 Features

- **Smart Health Data Extraction**: Extracts glucose, BMI, and age from natural language
- **Accurate Risk Assessment**: Medically-based diabetes risk prediction (Low/Medium/High)
- **AI-Powered Advice**: Personalized health recommendations using OpenAI
- **Modern UI**: Responsive web interface with real-time chat
- **Secure**: Environment variable management for API keys
- **Dynamic Conversations**: Context-aware chat with varied responses
- **Session Management**: Proper data handling and session clearing

## 📚 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Code Documentation](#code-documentation)
3. [System Flow Charts](#system-flow-charts)
4. [Technology Stack](#technology-stack)
5. [Interview Questions](#interview-questions)
6. [Setup & Deployment](#setup--deployment)
7. [Usage Guide](#usage-guide)

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Browser)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • Python API    │    │ • OpenAI API    │
│ • Chat UI       │    │ • Session Mgmt  │    │ • Health Logic  │
│ • Responsive    │    │ • Risk Calc     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Design Patterns

1. **Session-Based Architecture**: Maintains conversation state across requests
2. **Fallback Strategy**: Graceful degradation when external services fail
3. **Context-Aware AI**: Maintains conversation flow and context
4. **Secure Configuration**: Environment-based secret management

## 📖 Code Documentation

### Backend Structure (`simple_server.py`)

```python
# Core Components
├── FastAPI App          # Web framework
├── OpenAI Client        # AI integration
├── Session Manager      # User session handling
├── Health Data Extractor # NLP for health metrics
├── Risk Calculator      # Medical risk assessment
└── Response Generator   # Dynamic AI responses
```

#### Key Functions

**`extract_health_values(text)`**
- **Purpose**: Extract glucose, BMI, age from natural language
- **Input**: User message string
- **Output**: Dictionary with extracted values
- **Patterns**: Uses regex for flexible data extraction

**`predict_diabetes(glucose, bmi, age)`**
- **Purpose**: Calculate diabetes risk based on medical guidelines
- **Logic**: Scoring system with glucose as primary factor
- **Output**: "Low Risk", "Medium Risk", or "High Risk"

**`ask_llm(user_message)`**
- **Purpose**: Generate AI responses with context awareness
- **Features**: Temperature/top-p parameters for variety
- **Fallback**: Dynamic responses when API fails

**`generate_dynamic_advice(glucose, bmi, age, risk_level)`**
- **Purpose**: Create personalized health recommendations
- **AI Integration**: Uses OpenAI for context-specific advice
- **Personalization**: Based on user's specific health metrics

### Frontend Structure (`public/index.html`)

```javascript
// Core Components
├── Chat Interface       // Real-time messaging
├── API Client          // Backend communication
├── Session Manager     // Frontend session handling
├── UI Controller       // User interface logic
└── Response Renderer   // Message display
```

#### Key Functions

**`sendMessage()`**
- Handles user input and API communication
- Manages loading states and error handling
- Updates chat interface with responses

**`addMessage(content, type)`**
- Renders messages in chat interface
- Handles different message types (user/assistant/result)
- Manages scroll behavior

## 🔄 System Flow Charts

### 1. User Interaction Flow

```
User Input → Frontend Validation → API Request → Backend Processing
    ↓              ↓                 ↓                ↓
  Message        Format          HTTP POST        Session Mgmt
  Display        Check           to /api/chat     + Health Extract
    ↓              ↓                 ↓                ↓
  Response    Loading State    Process Message   AI Response
  Render        Animation        + Risk Calc       Generation
```

### 2. Health Assessment Flow

```
User Message → Health Data Extraction → Validation → Risk Calculation
      ↓                ↓                    ↓            ↓
  Natural NLP      Regex Patterns      Positive      Medical
  Processing        for Numbers        Values        Guidelines
      ↓                ↓                    ↓            ↓
  Extracted        Structured          Valid         Risk Score
  Values            Data               Input         Calculation
      ↓                ↓                    ↓            ↓
  Session Update    API Response        Prediction    AI Advice
```

### 3. AI Response Flow

```
User Message → Context Analysis → OpenAI API → Response Processing
      ↓              ↓                 ↓              ↓
  Message Type    Conversation      GPT-4o-mini    Success/Failure
  Detection       Context           with Temp/     ↓
      ↓              ↓                 Top-p         Dynamic Response
  Response        System Prompt     Generation    Generation
  Selection        + History          ↓              ↓
      ↓              ↓                 ↓              ↓
  Context-Aware    Personalized      AI Response   Fallback to
  Response         Conversation      or Error      Local Logic
```

## 🛠️ Technology Stack

### Backend Technologies

| Technology | Version | Purpose | Key Features |
|-------------|---------|---------|--------------|
| **FastAPI** | 0.104+ | Web Framework | Auto-docs, Type Hints, High Performance |
| **Uvicorn** | 0.24+ | ASGI Server | Production-ready, Async Support |
| **OpenAI** | 1.0+ | AI Integration | GPT-4o-mini, Chat Completions |
| **Pydantic** | 2.0+ | Data Validation | Type Safety, Auto-validation |
| **python-dotenv** | 1.0+ | Config Management | Environment Variables |
| **httpx** | 0.25+ | HTTP Client | Async HTTP, SSL Control |

### Frontend Technologies

| Technology | Purpose | Key Features |
|-------------|---------|--------------|
| **HTML5** | Structure | Semantic Markup, Forms |
| **CSS3** | Styling | Responsive Design, Animations |
| **Vanilla JS** | Interactivity | Fetch API, DOM Manipulation |
| **CSS Grid/Flexbox** | Layout | Mobile-responsive Design |

### Deployment & Infrastructure

| Technology | Purpose | Configuration |
|-------------|---------|---------------|
| **Vercel** | Platform | Serverless Functions, Static Hosting |
| **Python Runtime** | Environment | Version 3.9+, Dependencies |
| **Environment Variables** | Security | API Key Management |

## 🎯 Interview Questions

### Technical Questions

#### Backend & API Design

**Q1: How does the session management work in this application?**
**A**: The app uses in-memory session storage with unique session IDs. Each user gets a `session_<timestamp>` ID that persists health data across multiple requests. Sessions are cleared when non-health messages are received to prevent data reuse.

**Q2: Explain the fallback strategy for AI failures.**
**A**: The app implements a multi-layer fallback:
1. Primary: OpenAI API with temperature/top-p parameters
2. Secondary: Dynamic local responses with randomization
3. Tertiary: Static responses for critical failures

**Q3: How do you handle SSL certificate issues on macOS?**
**A**: The app uses `ssl._create_unverified_https_context()` and `httpx.Client(verify=False)` to bypass SSL verification, with proper error handling and logging.

#### Frontend & UX

**Q4: How do you maintain conversation context in the frontend?**
**A**: The frontend uses session ID tracking and maintains chat history. It detects user agreement patterns ("sure", "okay") and provides context-aware responses.

**Q5: Explain the responsive design approach.**
**A**: Uses CSS Grid/Flexbox with mobile-first design. Media queries stack input/button vertically on mobile, ensuring full-width usability.

#### System Architecture

**Q6: Why did you choose FastAPI over Flask/Django?**
**A**: FastAPI provides automatic API documentation, type hints, async support, and better performance for AI/ML applications compared to Flask or Django.

**Q7: How do you ensure data validation and security?**
**A**: Uses Pydantic models for request validation, environment variables for secrets, and input sanitization for health data extraction.

### Behavioral Questions

**Q8: How would you scale this application for millions of users?**
**A**: Implement Redis for session storage, database for persistence, load balancing, and caching for AI responses.

**Q9: How do you handle API rate limiting and costs?**
**A**: Implement request throttling, response caching, and fallback to local processing when quotas are exceeded.

**Q10: What testing strategies would you implement?**
**A**: Unit tests for health extraction, integration tests for API endpoints, E2E tests for user flows, and load testing for performance.

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Key

## 🛠️ Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd diabetes-agent
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Run Locally

```bash
python simple_server.py
```

The app will be available at: http://127.0.0.1:8004

## 🌐 Deployment

### Vercel Deployment

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel --prod
```

3. **Set Environment Variable**:
```bash
vercel env add OPENAI_API_KEY
```

## 📱 Usage

1. Open the app in your browser
2. Type your health information in natural language:
   - "glucose=120.0, bmi=25.5, age=45"
   - "my glucose is 130 and bmi is 22"
   - "age 36 glucose 90 bmi 20"
3. Get instant diabetes risk assessment and personalized advice

## 🔧 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript
- **AI**: OpenAI GPT-4o-mini
- **ML**: Scikit-learn for risk prediction
- **Deployment**: Vercel

## 🛡️ Security

- API keys stored in environment variables
- No hardcoded secrets in source code
- `.env` files excluded from git
- Secure API endpoint design

## 📊 Risk Assessment Logic

Based on medical guidelines:
- **Glucose ≥126 mg/dL**: Diabetes range (High Risk)
- **Glucose 100-125 mg/dL**: Prediabetes range (Medium Risk)
- **Glucose <100 mg/dL**: Normal range (Low Risk)
- Combined with BMI and age factors for comprehensive assessment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Medical Disclaimer

This application is for educational purposes only and should not be used as a substitute for professional medical advice. Always consult with qualified healthcare providers for medical decisions.
