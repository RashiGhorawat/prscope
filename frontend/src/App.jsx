import { useEffect, useState } from "react";
import "./index.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [summary, setSummary] = useState(null);
  const [prs, setPrs] = useState([]);
  const [selectedPr, setSelectedPr] = useState(null);
  const [loading, setLoading] = useState(true);

  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);

      const [summaryResponse, prsResponse] = await Promise.all([
        fetch(`${API_URL}/dashboard/risk-summary`),
        fetch(`${API_URL}/dashboard/prs`)
      ]);

      const summaryData = await summaryResponse.json();
      const prsData = await prsResponse.json();

      setSummary(summaryData);
      setPrs(prsData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function viewAnalysis(id) {
    try {
      const response = await fetch(`${API_URL}/dashboard/pr/${id}`);
      const data = await response.json();
      setSelectedPr(data);
    } catch (error) {
      console.error(error);
    }
  }

  async function analyzeNewPr(event) {
    event.preventDefault();

    if (!owner || !repo || !prNumber) {
      setMessage("Please fill in all fields.");
      return;
    }

    try {
      setAnalyzing(true);
      setMessage("");

      const response = await fetch(
        `${API_URL}/analyze/${owner}/${repo}/${prNumber}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed");
      }

      setMessage("PR analyzed successfully.");

      await loadDashboard();

      if (data.database?.pull_request_id) {
        await viewAnalysis(data.database.pull_request_id);
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAnalyzing(false);
    }
  }

  function getRiskClass(risk) {
    if (!risk) return "";
    return risk.toLowerCase();
  }

  if (loading && !summary) {
    return (
      <div className="app">
        <h1>PRScope</h1>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (selectedPr) {
    const risk = selectedPr.risk_analysis || {};
    const testRecommendations = risk.test_recommendations || [];
    const probabilities = risk.ml_class_probabilities || {};
    const riskReasons = risk.risk_reasons || [];
    const affectedFiles = risk.affected_files || [];

    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>PRScope</h1>
            <p>AI-Powered Pull Request Risk Analyzer</p>
          </div>
        </header>

        <button
          className="back-button"
          onClick={() => setSelectedPr(null)}
        >
          ← Back to Dashboard
        </button>

        <section className="detail-header">
          <h2>
            PR #{selectedPr.pr_number} — {selectedPr.repository}
          </h2>

          <p>{selectedPr.title}</p>

          <a
            className="github-button"
            href={selectedPr.github_url}
            target="_blank"
            rel="noreferrer"
          >
            View on GitHub
          </a>
        </section>

        <section className="details-grid">
          <div className="detail-card">
            <h3>Combined Risk</h3>
            <div
              className={`risk-value ${getRiskClass(
                risk.combined_risk_level
              )}`}
            >
              {risk.combined_risk_level}
            </div>
          </div>

          <div className="detail-card">
            <h3>ML Prediction</h3>
            <div
              className={`risk-value ${getRiskClass(
                risk.ml_predicted_risk
              )}`}
            >
              {risk.ml_predicted_risk}
            </div>
            <p>
              Confidence:{" "}
              {(risk.ml_confidence * 100).toFixed(0)}%
            </p>
          </div>

          <div className="detail-card">
            <h3>Dependency Impact</h3>
            <div
              className={`risk-value ${getRiskClass(
                risk.dependency_impact
              )}`}
            >
              {risk.dependency_impact}
            </div>
          </div>

          <div className="detail-card">
            <h3>Base Risk</h3>
            <div
              className={`risk-value ${getRiskClass(
                risk.base_risk_level
              )}`}
            >
              {risk.base_risk_level}
            </div>
          </div>
        </section>

        <section className="analysis-grid">
          <div className="detail-card">
            <h3>Change Metrics</h3>

            <p>
              <strong>Files Changed:</strong>{" "}
              {selectedPr.total_files_changed}
            </p>

            <p>
              <strong>Additions:</strong>{" "}
              +{selectedPr.total_additions}
            </p>

            <p>
              <strong>Deletions:</strong>{" "}
              -{selectedPr.total_deletions}
            </p>

            <p>
              <strong>Total Changes:</strong>{" "}
              {selectedPr.total_changes}
            </p>

            <p>
              <strong>High Risk Files:</strong>{" "}
              {risk.high_risk_file_count}
            </p>

            <p>
              <strong>Affected Files:</strong>{" "}
              {risk.affected_file_count}
            </p>
          </div>

          <div className="detail-card">
            <h3>ML Class Probabilities</h3>

            {Object.entries(probabilities).map(
              ([className, probability]) => (
                <div className="probability-row" key={className}>
                  <span>{className}</span>

                  <div className="probability-bar">
                    <div
                      className="probability-fill"
                      style={{
                        width: `${probability * 100}%`
                      }}
                    />
                  </div>

                  <span>
                    {(probability * 100).toFixed(1)}%
                  </span>
                </div>
              )
            )}
          </div>
        </section>

        <section className="detail-card full-width">
          <h3>Risk Reasons</h3>

          {riskReasons.length > 0 ? (
            <ul className="reason-list">
              {riskReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p>No risk reasons available.</p>
          )}
        </section>

        <section className="detail-card full-width">
          <h3>Recommended Tests</h3>

          {testRecommendations.length > 0 ? (
            <div className="test-recommendations">
              {testRecommendations.map((recommendation, index) => (
                <div
                  className="test-recommendation"
                  key={index}
                >
                  <h4>{recommendation.file}</h4>

                  <p>{recommendation.reason}</p>

                  <ul>
                    {recommendation.recommended_tests?.map(
                      (test, testIndex) => (
                        <li key={testIndex}>{test}</li>
                      )
                    )}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <p>No test recommendations available.</p>
          )}
        </section>

        <section className="detail-card full-width">
          <h3>Affected Files</h3>

          {affectedFiles.length > 0 ? (
            <ul className="file-list">
              {affectedFiles.map((file, index) => (
                <li className="file-item" key={index}>
                  {file}
                </li>
              ))}
            </ul>
          ) : (
            <p>No dependent project files were detected.</p>
          )}
        </section>

        <section className="detail-card full-width">
          <h3>Changed Files</h3>

          <div className="file-list">
            {selectedPr.files.map((file, index) => (
              <div className="file-item" key={index}>
                <div>
                  <strong>{file.filename}</strong>

                  <p>
                    +{file.additions} / -{file.deletions}{" "}
                    ({file.changes} changes)
                  </p>
                </div>

                <span
                  className={`file-risk ${getRiskClass(
                    file.risk_level
                  )}`}
                >
                  {file.risk_level}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>PRScope</h1>
          <p>AI-Powered Pull Request Risk Analyzer</p>
        </div>
      </header>

      <section className="stats-grid">
        <div className="stat-card">
          <h3>Repositories</h3>
          <div className="stat-value">
            {summary?.total_repositories || 0}
          </div>
        </div>

        <div className="stat-card">
          <h3>Pull Requests</h3>
          <div className="stat-value">
            {summary?.total_pull_requests || 0}
          </div>
        </div>

        <div className="stat-card">
          <h3>Low Risk</h3>
          <div className="stat-value">
            {summary?.combined_risk_distribution?.Low || 0}
          </div>
        </div>

        <div className="stat-card">
          <h3>Medium Risk</h3>
          <div className="stat-value">
            {summary?.combined_risk_distribution?.Medium || 0}
          </div>
        </div>

        <div className="stat-card">
          <h3>High Risk</h3>
          <div className="stat-value">
            {summary?.combined_risk_distribution?.High || 0}
          </div>
        </div>
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Risk Distribution</h2>

          <div className="distribution">
            <p>
              Low:{" "}
              {summary?.combined_risk_distribution?.Low || 0}
            </p>

            <p>
              Medium:{" "}
              {summary?.combined_risk_distribution?.Medium || 0}
            </p>

            <p>
              High:{" "}
              {summary?.combined_risk_distribution?.High || 0}
            </p>
          </div>
        </div>

        <div className="dashboard-card">
          <h2>ML Risk Distribution</h2>

          <div className="distribution">
            <p>
              Low:{" "}
              {summary?.ml_risk_distribution?.Low || 0}
            </p>

            <p>
              Medium:{" "}
              {summary?.ml_risk_distribution?.Medium || 0}
            </p>

            <p>
              High:{" "}
              {summary?.ml_risk_distribution?.High || 0}
            </p>
          </div>
        </div>
      </section>

      <section className="analyze-panel">
        <h2>Analyze New Pull Request</h2>

        <form
          className="analyze-form"
          onSubmit={analyzeNewPr}
        >
          <div className="form-group">
            <label>Owner</label>
            <input
              type="text"
              placeholder="python"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Repository</label>
            <input
              type="text"
              placeholder="cpython"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>PR Number</label>
            <input
              type="number"
              placeholder="1"
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
            />
          </div>

          <button
            className="analyze-button"
            type="submit"
            disabled={analyzing}
          >
            {analyzing ? "Analyzing..." : "Analyze PR"}
          </button>
        </form>

        {message && (
          <p className="success">{message}</p>
        )}
      </section>

      <section className="dashboard-card">
        <h2>Recent Pull Requests</h2>

        {prs.length === 0 ? (
          <p>No pull requests analyzed yet.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Repository</th>
                  <th>PR</th>
                  <th>Title</th>
                  <th>Files</th>
                  <th>Changes</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {prs.map((pr) => (
                  <tr key={pr.id}>
                    <td>{pr.repository}</td>
                    <td>#{pr.pr_number}</td>
                    <td>{pr.title}</td>
                    <td>{pr.total_files_changed}</td>
                    <td>{pr.total_changes}</td>
                    <td>
                      <button
                        className="view-button"
                        onClick={() =>
                          viewAnalysis(pr.id)
                        }
                      >
                        View Analysis
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;