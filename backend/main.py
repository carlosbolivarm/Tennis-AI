from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model and model columns
model = joblib.load("random_forest_model.pkl")
model_columns = joblib.load("model_columns.pkl")


class MatchInput(BaseModel):
    player1_hand: str
    player2_hand: str
    round: str
    surface: str
    best_of: int
    final_tb: str
    year: int

    p1_previous_matches: int
    p2_previous_matches: int
    experience_diff: int

    p1_previous_win_rate: float
    p2_previous_win_rate: float
    win_rate_diff: float

    p1_surface_matches: int
    p2_surface_matches: int
    surface_experience_diff: int

    p1_surface_win_rate: float
    p2_surface_win_rate: float
    surface_win_rate_diff: float


@app.get("/")
def home():
    return {"message": "ATP Tennis Match Predictor API is running"}


@app.post("/predict")
def predict_match(data: MatchInput):
    input_df = pd.DataFrame([{
        "Pl 1 hand": data.player1_hand,
        "Pl 2 hand": data.player2_hand,
        "Round": data.round,
        "Surface": data.surface,
        "Best of": data.best_of,
        "Final TB?": data.final_tb,
        "Year": data.year,

        "p1_previous_matches": data.p1_previous_matches,
        "p2_previous_matches": data.p2_previous_matches,
        "experience_diff": data.experience_diff,

        "p1_previous_win_rate": data.p1_previous_win_rate,
        "p2_previous_win_rate": data.p2_previous_win_rate,
        "win_rate_diff": data.win_rate_diff,

        "p1_surface_matches": data.p1_surface_matches,
        "p2_surface_matches": data.p2_surface_matches,
        "surface_experience_diff": data.surface_experience_diff,

        "p1_surface_win_rate": data.p1_surface_win_rate,
        "p2_surface_win_rate": data.p2_surface_win_rate,
        "surface_win_rate_diff": data.surface_win_rate_diff,
    }])

    input_encoded = pd.get_dummies(input_df)

    # Match the exact training columns
    input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

    prediction = model.predict(input_encoded)[0]
    probabilities = model.predict_proba(input_encoded)[0]

    if prediction == 1:
        predicted_winner = "Player 1"
        confidence = probabilities[1]
    else:
        predicted_winner = "Player 2"
        confidence = probabilities[0]

    return {
        "prediction": int(prediction),
        "predicted_winner": predicted_winner,
        "confidence": round(float(confidence), 4)
    }