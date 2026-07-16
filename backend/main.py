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

# Load labeled historical data so the API can calculate player features automatically
historical_data = pd.read_csv("../data/processed/labeled_matches_2021.csv")
historical_data["Date"] = pd.to_datetime(historical_data["Date"], errors="coerce")


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


class PlayerMatchInput(BaseModel):
    player1: str
    player2: str
    surface: str
    round: str
    best_of: int
    final_tb: str
    match_date: str


@app.get("/")
def home():
    return {"message": "ATP Tennis Match Predictor API is running"}


@app.get("/players")
def get_players():
    players = sorted(
        set(historical_data["Player 1"].dropna().tolist())
        | set(historical_data["Player 2"].dropna().tolist())
    )

    return {"players": players}


def get_player_hand(player_name):
    p1_rows = historical_data[historical_data["Player 1"] == player_name]
    p2_rows = historical_data[historical_data["Player 2"] == player_name]

    hands = []

    if not p1_rows.empty:
        hands.extend(p1_rows["Pl 1 hand"].dropna().tolist())

    if not p2_rows.empty:
        hands.extend(p2_rows["Pl 2 hand"].dropna().tolist())

    if len(hands) == 0:
        return "R"

    return pd.Series(hands).mode()[0]


def calculate_player_features(player1, player2, surface, match_date):
    match_date = pd.to_datetime(match_date, errors="coerce")

    past_matches = historical_data[historical_data["Date"] < match_date].copy()

    p1_matches_df = past_matches[
        (past_matches["Player 1"] == player1) |
        (past_matches["Player 2"] == player1)
    ]

    p2_matches_df = past_matches[
        (past_matches["Player 1"] == player2) |
        (past_matches["Player 2"] == player2)
    ]

    p1_previous_matches = len(p1_matches_df)
    p2_previous_matches = len(p2_matches_df)

    p1_wins = len(p1_matches_df[p1_matches_df["Winner"] == player1])
    p2_wins = len(p2_matches_df[p2_matches_df["Winner"] == player2])

    p1_previous_win_rate = (
        p1_wins / p1_previous_matches if p1_previous_matches > 0 else 0.5
    )

    p2_previous_win_rate = (
        p2_wins / p2_previous_matches if p2_previous_matches > 0 else 0.5
    )

    p1_surface_df = p1_matches_df[p1_matches_df["Surface"] == surface]
    p2_surface_df = p2_matches_df[p2_matches_df["Surface"] == surface]

    p1_surface_matches = len(p1_surface_df)
    p2_surface_matches = len(p2_surface_df)

    p1_surface_wins = len(p1_surface_df[p1_surface_df["Winner"] == player1])
    p2_surface_wins = len(p2_surface_df[p2_surface_df["Winner"] == player2])

    p1_surface_win_rate = (
        p1_surface_wins / p1_surface_matches if p1_surface_matches > 0 else 0.5
    )

    p2_surface_win_rate = (
        p2_surface_wins / p2_surface_matches if p2_surface_matches > 0 else 0.5
    )

    return {
        "p1_previous_matches": p1_previous_matches,
        "p2_previous_matches": p2_previous_matches,
        "experience_diff": p1_previous_matches - p2_previous_matches,

        "p1_previous_win_rate": p1_previous_win_rate,
        "p2_previous_win_rate": p2_previous_win_rate,
        "win_rate_diff": p1_previous_win_rate - p2_previous_win_rate,

        "p1_surface_matches": p1_surface_matches,
        "p2_surface_matches": p2_surface_matches,
        "surface_experience_diff": p1_surface_matches - p2_surface_matches,

        "p1_surface_win_rate": p1_surface_win_rate,
        "p2_surface_win_rate": p2_surface_win_rate,
        "surface_win_rate_diff": p1_surface_win_rate - p2_surface_win_rate,
    }


def make_prediction(input_df):
    input_encoded = pd.get_dummies(input_df)

    # Match exact training columns
    input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

    prediction = model.predict(input_encoded)[0]
    probabilities = model.predict_proba(input_encoded)[0]

    return prediction, probabilities


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

    prediction, probabilities = make_prediction(input_df)

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


@app.post("/predict_by_players")
def predict_by_players(data: PlayerMatchInput):
    player1_hand = get_player_hand(data.player1)
    player2_hand = get_player_hand(data.player2)

    player_features = calculate_player_features(
        data.player1,
        data.player2,
        data.surface,
        data.match_date
    )

    match_date = pd.to_datetime(data.match_date, errors="coerce")
    year = match_date.year

    input_df = pd.DataFrame([{
        "Pl 1 hand": player1_hand,
        "Pl 2 hand": player2_hand,
        "Round": data.round,
        "Surface": data.surface,
        "Best of": data.best_of,
        "Final TB?": data.final_tb,
        "Year": year,

        **player_features
    }])

    prediction, probabilities = make_prediction(input_df)

    if prediction == 1:
        predicted_winner = data.player1
        confidence = probabilities[1]
    else:
        predicted_winner = data.player2
        confidence = probabilities[0]

    return {
        "player1": data.player1,
        "player2": data.player2,
        "surface": data.surface,
        "round": data.round,
        "predicted_winner": predicted_winner,
        "confidence": round(float(confidence), 4),

        "player1_hand": player1_hand,
        "player2_hand": player2_hand,

        "player1_previous_matches": player_features["p1_previous_matches"],
        "player2_previous_matches": player_features["p2_previous_matches"],
        "experience_diff": player_features["experience_diff"],

        "player1_previous_win_rate": round(player_features["p1_previous_win_rate"], 4),
        "player2_previous_win_rate": round(player_features["p2_previous_win_rate"], 4),
        "win_rate_diff": round(player_features["win_rate_diff"], 4),

        "player1_surface_matches": player_features["p1_surface_matches"],
        "player2_surface_matches": player_features["p2_surface_matches"],
        "surface_experience_diff": player_features["surface_experience_diff"],

        "player1_surface_win_rate": round(player_features["p1_surface_win_rate"], 4),
        "player2_surface_win_rate": round(player_features["p2_surface_win_rate"], 4),
        "surface_win_rate_diff": round(player_features["surface_win_rate_diff"], 4)
    }