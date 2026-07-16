import { useEffect, useState } from "react";
import { getPlayers, predictMatch } from "../services/predictionApi";

function MatchForm({ setPrediction, setIsLoading, setError }) {
  const [formData, setFormData] = useState({
    player1: "",
    player2: "",
    surface: "Hard",
    round: "F",
    best_of: 3,
    final_tb: "A",
    match_date: new Date().toISOString().split("T")[0],
});

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]:
        e.target.name === "best_of"
          ? Number(e.target.value)
          : e.target.value,
    });
  };

    const [players, setPlayers] = useState([]);

    useEffect(() => {
    async function loadPlayers() {
        try {
        const playerList = await getPlayers();
        setPlayers(playerList);
        } catch (error) {
        setError("Unable to load the available players.");
        }
    }

    loadPlayers();
    }, [setError]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setPrediction(null);
    setError("");

    const player1Exists = players.includes(formData.player1);
    const player2Exists = players.includes(formData.player2);

    if (!player1Exists) {
        setError(`"${formData.player1}" is not an available ATP player.`);
        return;
    }

    if (!player2Exists) {
        setError(`"${formData.player2}" is not an available ATP player.`);
        return;
    }

    if (formData.player1 === formData.player2) {
        setError("Please select two different players.");
        return;
    }

    setIsLoading(true);

    try {
        const result = await predictMatch(formData);
        setPrediction(result);
    } catch (err) {
        setError(err.message || "Unable to predict this match.");
    } finally {
        setIsLoading(false);
    }
    };

  return (
    <form className="match-form" onSubmit={handleSubmit}>

        <label>
            Player 1
            <input
                type="text"
                name="player1"
                list="player1-options"
                placeholder="Search for a player"
                value={formData.player1}
                onChange={handleChange}
                autoComplete="off"
                required
            />

            <datalist id="player1-options">
                {players.map((player) => (
                <option key={player} value={player} />
                ))}
            </datalist>
        </label>

        <label>
            Player 2
            <input
                type="text"
                name="player2"
                list="player2-options"
                placeholder="Search for a player"
                value={formData.player2}
                onChange={handleChange}
                autoComplete="off"
                required
            />

            <datalist id="player2-options">
                {players.map((player) => (
                <option key={player} value={player} />
                ))}
            </datalist>
        </label>

      <label>
        Surface
        <select
          name="surface"
          value={formData.surface}
          onChange={handleChange}
        >
          <option>Hard</option>
          <option>Clay</option>
          <option>Grass</option>
        </select>
      </label>

      <label>
        Round
        <select
          name="round"
          value={formData.round}
          onChange={handleChange}
        >
          <option value="R128">Round of 128</option>
          <option value="R64">Round of 64</option>
          <option value="R32">Round of 32</option>
          <option value="R16">Round of 16</option>
          <option value="QF">Quarterfinal</option>
          <option value="SF">Semifinal</option>
          <option value="F">Final</option>
        </select>
      </label>

      <label>
        Best Of
        <select
          name="best_of"
          value={formData.best_of}
          onChange={handleChange}
        >
          <option value={3}>3 Sets</option>
          <option value={5}>5 Sets</option>
        </select>
      </label>

      <button type="submit">
        Predict Winner
      </button>

    </form>
  );
}

export default MatchForm;