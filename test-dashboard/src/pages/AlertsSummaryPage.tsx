import React, { useState } from 'react';
import { apiPost } from '../utils/api';
import ApiForm, { type FormField } from '../components/ApiForm';
import ResponseCard from '../components/ResponseCard';

const AlertsSummaryPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fields: FormField[] = [
    {
      name: 'user_role_arn',
      label: 'User Role ARN',
      type: 'text',
      placeholder: 'arn:aws:iam::123456789012:role/KostyAuditRole'
    },
    {
      name: 'external_id',
      label: 'External ID',
      type: 'text',
      placeholder: 'unique-external-id'
    },
    {
      name: 'regions',
      label: 'Regions',
      type: 'text',
      defaultValue: 'us-east-1',
      isArray: true,
      help: 'Comma-separated list of regions'
    }
  ];

  const handleSubmit = async (formData: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiPost('/api/alerts/summary', formData);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute API call');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Alert Summary</h1>
      <p>Get summary statistics for alerts across your AWS environment.</p>
      <p><strong>Endpoint:</strong> <code>POST /api/alerts/summary</code></p>
      
      <ApiForm fields={fields} onSubmit={handleSubmit} loading={loading} />
      
      {(data || error) && (
        <ResponseCard
          title="API Response"
          data={data}
          loading={loading}
          error={error}
        />
      )}
    </div>
  );
};

export default AlertsSummaryPage;
