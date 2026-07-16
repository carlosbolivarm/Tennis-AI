const BASE_URL = "https://tennis-ai-68dc.onrender.com";

export async function getPlayers() {
  const response = await fetch(`${BASE_URL}/players`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to load players.");
  }

  return data.players;
}

export async function predictMatch(matchData) {
  const response = await fetch(`${BASE_URL}/predict_by_players`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(matchData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Prediction failed.");
  }

  return data;
}