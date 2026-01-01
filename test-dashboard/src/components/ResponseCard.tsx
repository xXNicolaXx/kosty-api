import React from 'react';
import './ResponseCard.css';

interface ResponseCardProps {
  title: string;
  data: any;
  loading: boolean;
  error: string | null;
}

const ResponseCard: React.FC<ResponseCardProps> = ({ title, data, loading, error }) => {
  return (
    <div className="response-card">
      <h3>{title}</h3>
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}
      {!loading && !error && data && (
        <pre className="json-display">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
};

export default ResponseCard;
