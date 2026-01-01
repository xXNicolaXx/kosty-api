import React, { useEffect, useState } from 'react';
import { apiGet } from '../utils/api';
import ResponseCard from '../components/ResponseCard';

const AccountIdPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiGet('/api/account-id');
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
      <h1>AWS Account ID</h1>
      <p>Get the AWS Account ID of the API server. Users need this to create the trust relationship in their IAM role.</p>
      <p><strong>Endpoint:</strong> <code>GET /api/account-id</code></p>
      
      <ResponseCard
        title="API Response"
        data={data}
        loading={loading}
        error={error}
      />
    </div>
  );
};

export default AccountIdPage;
