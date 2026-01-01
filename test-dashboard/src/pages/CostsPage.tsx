import React, { useState } from 'react';
import { apiPost } from '../utils/api';
import ApiForm, { type FormField } from '../components/ApiForm';
import ResponseCard from '../components/ResponseCard';

const CostsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fields: FormField[] = [
    {
      name: 'user_role_arn',
      label: 'User Role ARN',
      type: 'text',
      placeholder: 'arn:aws:iam::123456789012:role/KostyAuditRole',
      help: 'ARN of the IAM role in your AWS account (optional for testing)'
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
    },
    {
      name: 'period',
      label: 'Period',
      type: 'select',
      options: ['DAILY', 'WEEKLY', 'MONTHLY'],
      defaultValue: 'MONTHLY',
      help: 'Cost analysis period'
    }
  ];

  const handleSubmit = async (formData: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiPost('/api/costs', formData);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute API call');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Cost Analysis</h1>
      <p>Get cost analysis by AWS service for the specified period.</p>
      <p><strong>Endpoint:</strong> <code>POST /api/costs</code></p>
      
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

export default CostsPage;
