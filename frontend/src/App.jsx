import { useState } from "react";
import MatchForm from "./components/MatchForm";
import PredictionResult from "./components/PredictionResult";
import "./App.css";

function App() {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  return (
    <main className="app">
      <section className="predictor-card">
        <header className="page-header">
          <span className="page-label">Machine Learning Project</span>

          <h1>ATP Tennis Match Predictor</h1>

          <p>
            Enter two players and the match conditions to predict the most
            likely winner.
          </p>
        </header>

        <MatchForm
          setPrediction={setPrediction}
          setIsLoading={setIsLoading}
          setError={setError}
        />

        {isLoading && (
          <div className="status-message">
            Analyzing the match...
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {prediction && !isLoading && (
          <PredictionResult prediction={prediction} />
        )}
      </section>
    </main>
  );
}

export default App;