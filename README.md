# 🧠 Diabetes AI Assistant

A modern web application that provides personalized diabetes risk assessment using AI and machine learning.

## 🚀 Features

- **Smart Health Data Extraction**: Extracts glucose, BMI, and age from natural language
- **Accurate Risk Assessment**: Medically-based diabetes risk prediction (Low/Medium/High)
- **AI-Powered Advice**: Personalized health recommendations using OpenAI
- **Modern UI**: Responsive web interface with real-time chat
- **Secure**: Environment variable management for API keys

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
