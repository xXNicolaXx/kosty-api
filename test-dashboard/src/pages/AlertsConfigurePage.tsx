import React, { useState } from 'react';
import { apiPost } from '../utils/api';
import ApiForm, { type FormField } from '../components/ApiForm';
import ResponseCard from '../components/ResponseCard';

const AlertsConfigurePage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fields: FormField[] = [
    {
      name: 'budget_threshold_percentage',
      label: 'Budget Threshold %',
      type: 'number',
      defaultValue: 80,
      help: 'Budget alert threshold percentage'
    },
    {
      name: 'cost_spike_threshold',
      label: 'Cost Spike Threshold',
      type: 'number',
      defaultValue: 100,
      help: 'Cost spike detection threshold in dollars'
    },
    {
      name: 'idle_days_threshold',
      label: 'Idle Days Threshold',
      type: 'number',
      defaultValue: 7,
      help: 'Number of idle days before alerting'
    }
  ];

  const handleSubmit = async (formData: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiPost('/api/alerts/configure', formData);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute API call');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Configure Alerts</h1>
      <p>Configure alert thresholds for cost and resource monitoring.</p>
      <p><strong>Endpoint:</strong> <code>POST /api/alerts/configure</code></p>
      
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

export default AlertsConfigurePage;
