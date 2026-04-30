import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Dummy small dataset (replace later with PIMA if you want)
data = {
    "glucose": [85, 130, 150, 90, 170],
    "bmi": [22, 30, 35, 25, 40],
    "age": [25, 45, 50, 30, 60],
    "diabetes": [0, 1, 1, 0, 1]
}

df = pd.DataFrame(data)

X = df[["glucose", "bmi", "age"]]
y = df["diabetes"]

model = RandomForestClassifier()
model.fit(X, y)

# Save model
with open("diabetes_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved!")