import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';
import ResponseCard from '../components/ResponseCard';

const HealthPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiGet('/health');
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>Health Check</h1>
      <p>Verify that the Kosty API server is running and healthy.</p>
      <p><strong>Endpoint:</strong> <code>GET /health</code></p>
      
      <ResponseCard
        title="API Response"
        data={data}
        loading={loading}
        error={error}
      />
    </div>
  );
};

export default HealthPage;
