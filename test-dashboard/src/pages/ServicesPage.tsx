import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';
import ResponseCard from '../components/ResponseCard';

const ServicesPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiGet('/api/services');
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
      <h1>Available Services</h1>
      <p>List all AWS services that can be audited by Kosty.</p>
      <p><strong>Endpoint:</strong> <code>GET /api/services</code></p>
      
      <ResponseCard
        title="API Response"
        data={data}
        loading={loading}
        error={error}
      />
    </div>
  );
};

export default ServicesPage;
