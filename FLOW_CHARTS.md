# 🔄 System Flow Charts

## 📋 Table of Contents

1. [User Interaction Flow](#user-interaction-flow)
2. [Health Assessment Process](#health-assessment-process)
3. [AI Response Generation](#ai-response-generation)
4. [Session Management](#session-management)
5. [Error Handling & Recovery](#error-handling--recovery)
6. [Data Processing Pipeline](#data-processing-pipeline)

---

## 🔄 User Interaction Flow

### Main User Journey

```mermaid
graph TD
    A[User Opens App] --> B[Load Chat Interface]
    B --> C[Display Welcome Message]
    C --> D[User Types Message]
    D --> E{Message Type?}
    
    E -->|Greeting| F[AI Greeting Response]
    E -->|Health Data| G[Extract Health Values]
    E -->|Agreement| H[Context-Aware Response]
    E -->|Other| I[General Response]
    
    F --> J[Update Chat UI]
    G --> K{Complete Data?}
    H --> J
    I --> J
    
    K -->|No| L[Request Missing Data]
    K -->|Yes| M[Generate Risk Assessment]
    
    L --> N[Continue Conversation]
    M --> O[Display Risk Results]
    
    N --> D
    O --> P[Show Personalized Advice]
    P --> D
    J --> D
```

### Detailed Message Processing

```mermaid
graph LR
    A[User Input] --> B[Frontend Validation]
    B --> C[Format Check]
    C --> D[API Request]
    D --> E[Backend Processing]
    E --> F[Response Generation]
    F --> G[UI Update]
    
    subgraph "Frontend"
        B --> B1[Empty Check]
        B1 --> B2[Character Limit]
        B2 --> C
    end
    
    subgraph "Backend"
        E --> E1[Session Management]
        E1 --> E2[Health Extraction]
        E2 --> E3[AI Processing]
        E3 --> F
    end
    
    subgraph "Response"
        F --> F1[AI Response]
        F1 --> F2[Risk Assessment]
        F2 --> F3[Error Handling]
        F3 --> G
    end
```

---

## 🏥 Health Assessment Process

### Risk Calculation Flow

```mermaid
graph TD
    A[Health Data Received] --> B[Validate Input]
    B --> C{All Values Present?}
    
    C -->|No| D[Request Missing Values]
    C -->|Yes| E[Check Positive Values]
    
    E -->|Invalid| F[Error: Positive Numbers Required]
    E -->|Valid| G[Calculate Risk Score]
    
    G --> H[Glucose Assessment]
    H --> I[BMI Assessment]
    I --> J[Age Assessment]
    
    J --> K[Sum Risk Points]
    K --> L{Total Score}
    
    L -->|0-2| M[Low Risk]
    L -->|3-4| N[Medium Risk]
    L -->|5+| O[High Risk]
    
    M --> P[Generate Low Risk Advice]
    N --> Q[Generate Medium Risk Advice]
    O --> R[Generate High Risk Advice]
    
    P --> S[Return Assessment]
    Q --> S
    R --> S
    
    D --> T[Continue Conversation]
    F --> T
    S --> U[Display Results]
```

### Medical Guidelines Implementation

```mermaid
graph LR
    A[Glucose Level] --> B{Glucose Range}
    
    B -->|<90| C[Normal: 0 points]
    B -->|90-99| D[Elevated: 1 point]
    B -->|100-125| E[Prediabetes: 2 points]
    B -->|≥126| F[Diabetes: 3 points]
    
    G[BMI Value] --> H{BMI Category}
    
    H -->|<25| I[Normal: 0 points]
    H -->|25-29.9| J[Overweight: 1 point]
    H -->|≥30| K[Obese: 2 points]
    
    L[Age Value] --> M{Age Range}
    
    M -->|<45| N[Young: 0 points]
    M -->|45-64| O[Middle: 1 point]
    M -->|≥65| P[Senior: 2 points]
    
    C --> Q[Calculate Total]
    D --> Q
    E --> Q
    F --> Q
    
    I --> Q
    J --> Q
    K --> Q
    
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R[Determine Risk Level]
```

---

## 🤖 AI Response Generation

### Dynamic Response Flow

```mermaid
graph TD
    A[User Message] --> B[Context Analysis]
    B --> C{Message Type}
    
    C -->|Greeting| D[Greeting Response Set]
    C -->|Agreement| E[Agreement Response Set]
    C -->|Health Query| F[Health Response Set]
    C -->|Other| G[General Response Set]
    
    D --> H[Select Random Response]
    E --> H
    F --> H
    G --> H
    
    H --> I{OpenAI Available?}
    
    I -->|Yes| J[Call OpenAI API]
    I -->|No| K[Use Fallback Response]
    
    J --> L{API Success?}
    
    L -->|Yes| M[AI Generated Response]
    L -->|No| K
    
    K --> N[Dynamic Local Response]
    M --> O[Format Response]
    N --> O
    
    O --> P[Return to User]
```

### OpenAI Integration Flow

```mermaid
graph LR
    A[Prepare Request] --> B[System Prompt + User Message]
    B --> C[Set Parameters]
    
    C --> D[temperature=0.8]
    C --> E[top_p=0.9]
    C --> F[max_tokens=150]
    C --> G[presence_penalty=0.6]
    C --> H[frequency_penalty=0.6]
    
    D --> I[Send to OpenAI]
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J{Response Status}
    
    J -->|Success| K[Extract Response Text]
    J -->|Error| L[Log Error]
    
    K --> M[Return AI Response]
    L --> N[Use Fallback]
    
    N --> O[Dynamic Local Response]
    M --> P[Format for Display]
    O --> P
```

---

## 📝 Session Management

### Session Lifecycle

```mermaid
graph TD
    A[User Starts Chat] --> B[Generate Session ID]
    B --> C[Create Empty Session]
    C --> D[Store in Memory]
    
    D --> E[User Sends Message]
    E --> F{Health Data?}
    
    F -->|Yes| G[Extract Health Values]
    F -->|No| H[Clear Session Data]
    
    G --> I[Update Session]
    I --> J[Check Completeness]
    
    J -->|Complete| K[Ready for Prediction]
    J -->|Incomplete| L[Request More Data]
    
    H --> M[Reset Session]
    M --> N[Continue Conversation]
    
    K --> O[Generate Assessment]
    L --> P[Wait for More Data]
    O --> Q[Display Results]
    P --> E
    Q --> R[Continue Chat]
    
    N --> E
    R --> E
```

### Session Data Structure

```mermaid
graph TB
    A[Session Object] --> B[Session ID]
    A --> C[Health Data]
    A --> D[Metadata]
    
    B --> B1["session_" + timestamp]
    
    C --> C1[glucose: float]
    C --> C2[bmi: float]
    C --> C3[age: integer]
    
    D --> D1[created_at: datetime]
    D --> D2[last_updated: datetime]
    D --> D3[messages_count: integer]
    
    subgraph "Session States"
        E[Empty] --> F[Partial Data]
        F --> G[Complete Data]
        G --> H[Assessment Generated]
        H --> I[Session Cleared]
        I --> E
    end
```

---

## ⚠️ Error Handling & Recovery

### Comprehensive Error Flow

```mermaid
graph TD
    A[Request Received] --> B[Input Validation]
    B --> C{Valid Input?}
    
    C -->|No| D[Return 400 Error]
    C -->|Yes| E[Process Request]
    
    E --> F{Health Data Valid?}
    
    F -->|No| G[Return 422 Error]
    F -->|Yes| H[Call OpenAI API]
    
    H --> I{API Available?}
    
    I -->|No| J[Use Fallback Logic]
    I -->|Yes| K{API Success?}
    
    K -->|No| L[Log Error + Fallback]
    K -->|Yes| M[Process AI Response]
    
    J --> N[Generate Response]
    L --> N
    M --> N
    
    N --> O[Return Success]
    
    D --> P[Log Error]
    G --> P
    P --> Q[Send Error Response]
```

### SSL Certificate Error Handling

```mermaid
graph LR
    A[API Call Attempt] --> B{SSL Error?}
    
    B -->|No| C[Normal Processing]
    B -->|Yes| D[Apply SSL Fix]
    
    D --> E[ssl._create_unverified_https_context]
    E --> F[httpx.Client(verify=False)]
    F --> G[Retry API Call]
    
    G --> H{Success?}
    
    H -->|Yes| I[Continue Processing]
    H -->|No| J[Use Fallback]
    
    C --> K[Return Response]
    I --> K
    J --> L[Dynamic Local Response]
    L --> K
```

---

## 🔄 Data Processing Pipeline

### Health Data Extraction Pipeline

```mermaid
graph TD
    A[User Message] --> B[Text Preprocessing]
    B --> C[Lowercase Conversion]
    C --> D[Tokenization]
    
    D --> E[Pattern Matching]
    E --> F[Glucose Patterns]
    E --> G[BMI Patterns]
    E --> H[Age Patterns]
    
    F --> I[Extract Glucose]
    G --> J[Extract BMI]
    H --> K[Extract Age]
    
    I --> L[Validate Glucose]
    J --> M[Validate BMI]
    K --> N[Validate Age]
    
    L --> O{Valid?}
    M --> P{Valid?}
    N --> Q{Valid?}
    
    O -->|Yes| R[Store Glucose]
    O -->|No| S[Ignore Glucose]
    
    P -->|Yes| T[Store BMI]
    P -->|No| U[Ignore BMI]
    
    Q -->|Yes| V[Store Age]
    Q -->|No| W[Ignore Age]
    
    R --> X[Compile Results]
    T --> X
    V --> X
    S --> X
    U --> X
    W --> X
    
    X --> Y[Return Health Data]
```

### Response Generation Pipeline

```mermaid
graph LR
    A[Response Request] --> B[Context Analysis]
    B --> C[Message Classification]
    
    C --> D[Response Strategy]
    D --> E{AI Available?}
    
    E -->|Yes| F[OpenAI Processing]
    E -->|No| G[Fallback Processing]
    
    F --> H[Prompt Engineering]
    H --> I[Parameter Tuning]
    I --> J[API Call]
    
    G --> K[Pattern Matching]
    K --> L[Response Selection]
    L --> M[Randomization]
    
    J --> N{Success?}
    N -->|Yes| O[AI Response]
    N -->|No| G
    
    M --> P[Dynamic Response]
    O --> Q[Response Formatting]
    P --> Q
    
    Q --> R[Final Response]
```

---

## 📊 System Metrics & Monitoring

### Performance Monitoring Flow

```mermaid
graph TD
    A[User Request] --> B[Start Timer]
    B --> C[Process Request]
    C --> D[End Timer]
    
    D --> E[Calculate Response Time]
    E --> F{Response Time < 2s?}
    
    F -->|Yes| G[Log Success]
    F -->|No| H[Log Performance Issue]
    
    G --> I[Update Metrics]
    H --> I
    
    I --> J[Monitor Dashboard]
    J --> K{Alert Threshold?}
    
    K -->|Yes| L[Send Alert]
    K -->|No| M[Continue Monitoring]
    
    L --> N[Investigate Issue]
    M --> O[Next Request]
    N --> O
```

### Error Rate Monitoring

```mermaid
graph LR
    A[Request Processing] --> B{Error Occurred?}
    
    B -->|No| C[Increment Success Count]
    B -->|Yes| D[Log Error Details]
    
    D --> E[Increment Error Count]
    E --> F[Calculate Error Rate]
    
    C --> F
    F --> G{Error Rate > 5%?}
    
    G -->|Yes| H[Trigger Alert]
    G -->|No| I[Normal Operation]
    
    H --> J[Investigate Root Cause]
    I --> K[Continue Monitoring]
    J --> K
```

---

## 🔧 Configuration & Deployment Flow

### Environment Setup Flow

```mermaid
graph TD
    A[Start Application] --> B[Load Environment]
    B --> C[Check API Key]
    
    C --> D{API Key Present?}
    
    D -->|No| E[Raise Error & Exit]
    D -->|Yes| F[Initialize OpenAI Client]
    
    F --> G[Setup SSL Context]
    G --> H[Create FastAPI App]
    H --> I[Configure CORS]
    
    I --> J[Setup Routes]
    J --> K[Start Server]
    
    K --> L[Ready for Requests]
    
    E --> M[Display Error Message]
    M --> N[Exit Application]
```

### Vercel Deployment Flow

```mermaid
graph LR
    A[git push] --> B[Vercel Build Trigger]
    B --> C[Install Dependencies]
    C --> D[Build Python Runtime]
    
    D --> E[Deploy Functions]
    E --> F[Upload Static Files]
    F --> G[Configure Routes]
    
    G --> H[Set Environment Variables]
    H --> I[Start Production Server]
    
    I --> J[Health Check]
    J --> K{Deployment Successful?}
    
    K -->|Yes| L[Live URL Available]
    K -->|No| M[Rollback to Previous]
    
    L --> N[Monitor Performance]
    M --> O[Debug Issues]
    N --> P[Scale as Needed]
    O --> P
```

---

*These flow charts provide comprehensive visual documentation of all system processes, from user interactions to technical implementations.*
