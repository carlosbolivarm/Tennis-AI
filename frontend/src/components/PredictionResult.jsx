function PredictionResult({ prediction }) {
  const confidencePercentage = Math.round(prediction.confidence * 100);

  return (
    <section className="prediction-result">
      <p className="result-label">Predicted Winner</p>

      <h2>{prediction.predicted_winner}</h2>

      <div className="confidence-section">
        <div className="confidence-header">
          <span>Model Confidence</span>
          <strong>{confidencePercentage}%</strong>
        </div>

        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${confidencePercentage}%` }}
          />
        </div>
      </div>

      <div className="match-summary">
        <p>
          <strong>Match:</strong> {prediction.player1} vs.{" "}
          {prediction.player2}
        </p>

        <p>
          <strong>Surface:</strong> {prediction.surface}
        </p>

        <p>
          <strong>Round:</strong> {prediction.round}
        </p>
      </div>
    </section>
  );
}

export default PredictionResult;