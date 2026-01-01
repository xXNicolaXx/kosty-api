import React, { useState } from 'react';
import { apiPost } from '../utils/api';
import ApiForm, { type FormField } from '../components/ApiForm';
import ResponseCard from '../components/ResponseCard';

const AuditPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fields: FormField[] = [
    {
      name: 'user_role_arn',
      label: 'User Role ARN',
      type: 'text',
      placeholder: 'arn:aws:iam::123456789012:role/KostyAuditRole',
      help: 'ARN of the IAM role in your AWS account (optional for testing with default credentials)'
    },
    {
      name: 'external_id',
      label: 'External ID',
      type: 'text',
      placeholder: 'unique-external-id',
      help: 'External ID for additional security when assuming the role'
    },
    {
      name: 'regions',
      label: 'Regions',
      type: 'text',
      defaultValue: 'us-east-1',
      isArray: true,
      help: 'Comma-separated list of AWS regions (e.g., us-east-1,eu-west-1)'
    },
    {
      name: 'max_workers',
      label: 'Max Workers',
      type: 'number',
      defaultValue: 5,
      help: 'Number of parallel workers for the audit'
    },
    {
      name: 'organization',
      label: 'Organization-wide Scan',
      type: 'select',
      options: ['false', 'true'],
      defaultValue: 'false',
      help: 'Run audit across entire AWS organization'
    }
  ];

  const handleSubmit = async (formData: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      
      // Convert organization to boolean
      if (formData.organization) {
        formData.organization = formData.organization === 'true';
      }
      
      const result = await apiPost('/api/audit', formData);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute API call');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Full AWS Audit</h1>
      <p>Run a comprehensive AWS audit across specified services and regions.</p>
      <p><strong>Endpoint:</strong> <code>POST /api/audit</code></p>
      
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

export default AuditPage;
