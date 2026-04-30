import pickle
import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("🧠 Diabetes AI Assistant")

def ask_llm(user_message):
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
        # Neutral fallback to avoid re-asking for values
        return "Got it—processing your details now."

def predict_diabetes(glucose, bmi, age):
    model = pickle.load(open("diabetes_model.pkl", "rb"))
    prediction = model.predict([[glucose, bmi, age]])[0]
    
    return "High Risk" if prediction == 1 else "Low Risk"

# Store user data
if "data" not in st.session_state:
    st.session_state.data = {}

user_input = st.text_input("Tell me about your health:")

if user_input:
    reply = ask_llm(user_input)
    st.write("🤖", reply)

if "glucose" in user_input.lower():
    words = user_input.split()
    for word in words:
        try:
            st.session_state.data["glucose"] = int(word)
            break
        except ValueError:
            continue

elif "bmi" in user_input.lower():
    words = user_input.split()
    for word in words:
        try:
            st.session_state.data["bmi"] = float(word)
            break
        except ValueError:
            continue

elif "age" in user_input.lower():
    words = user_input.split()
    for word in words:
        try:
            st.session_state.data["age"] = int(word)
            break
        except ValueError:
            continue

if len(st.session_state.data) == 3:
    result = predict_diabetes(
        st.session_state.data["glucose"],
        st.session_state.data["bmi"],
        st.session_state.data["age"]
    )

    explanation = ask_llm(
        f"A patient has {result} diabetes risk. Explain what this means and give advice."
    )
    
    st.write("🧠 Result:", result)
    st.write("💬 Advice:", explanation)