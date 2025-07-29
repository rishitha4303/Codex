import React, { useState } from 'react';
import axios from 'axios';
import GraphViewer from '../components/GraphViewer';
import './GraphPage.css';

const GraphPage = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [graphUrl, setGraphUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateGraph = async () => {
    setLoading(true);
    setGraphUrl('');
    setError('');

    try {
      const response = await axios.post('http://localhost:5001/generate-graph', {
        repo_url: repoUrl,
      });

      if (response.data.graph_url) {
        setGraphUrl(`http://localhost:5000${response.data.graph_url}`);
      }
    } catch (err) {
      setError('Failed to generate graph. Make sure the repo is public.');
    }

    setLoading(false);
  };

  return (
    <div className="graph-page">
      <h2>📊 GitHub Repo Dependency Graph</h2>
      <input
        type="text"
        placeholder="Enter GitHub Repository URL"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
      />
      <button onClick={handleGenerateGraph} disabled={loading || !repoUrl}>
        {loading ? 'Generating...' : 'Generate Graph'}
      </button>

      {error && <p className="error">{error}</p>}

      <GraphViewer graphUrl={graphUrl} />
    </div>
  );
};

export default GraphPage;
