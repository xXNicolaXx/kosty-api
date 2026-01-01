import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  const endpoints = [
    {
      path: '/health',
      name: 'Health Check',
      description: 'Verify API server is running',
      method: 'GET'
    },
    {
      path: '/account-id',
      name: 'Account ID',
      description: 'Get API server AWS Account ID',
      method: 'GET'
    },
    {
      path: '/services',
      name: 'List Services',
      description: 'List all available AWS services',
      method: 'GET'
    },
    {
      path: '/audit',
      name: 'Full Audit',
      description: 'Run comprehensive AWS audit',
      method: 'POST'
    },
    {
      path: '/costs',
      name: 'Cost Analysis',
      description: 'Get cost analysis by service',
      method: 'POST'
    },
    {
      path: '/costs-trends',
      name: 'Cost Trends',
      description: 'Analyze cost trends over time',
      method: 'POST'
    },
    {
      path: '/costs-anomalies',
      name: 'Cost Anomalies',
      description: 'Detect unusual spending patterns',
      method: 'POST'
    },
    {
      path: '/budgets',
      name: 'Budget Check',
      description: 'Monitor budget thresholds',
      method: 'POST'
    },
    {
      path: '/guardduty',
      name: 'GuardDuty',
      description: 'Security threat detection findings',
      method: 'POST'
    },
    {
      path: '/alerts-feed',
      name: 'Alert Feed',
      description: 'Get aggregated alerts',
      method: 'POST'
    },
    {
      path: '/alerts-summary',
      name: 'Alert Summary',
      description: 'Get alert statistics',
      method: 'POST'
    },
    {
      path: '/alerts-configure',
      name: 'Configure Alerts',
      description: 'Set alert thresholds',
      method: 'POST'
    }
  ];

  return (
    <div className="home">
      <div className="hero">
        <h1>💰 Kosty API Test Dashboard</h1>
        <p>Debug and test all Kosty backend APIs</p>
      </div>

      <div className="endpoints-grid">
        {endpoints.map(endpoint => (
          <Link to={endpoint.path} key={endpoint.path} className="endpoint-card">
            <div className="endpoint-header">
              <h3>{endpoint.name}</h3>
              <span className={`method ${endpoint.method.toLowerCase()}`}>
                {endpoint.method}
              </span>
            </div>
            <p>{endpoint.description}</p>
          </Link>
        ))}
      </div>

      <div className="info-box">
        <h3>ℹ️ Configuration</h3>
        <p>
          The API base URL is configured via the <code>VITE_API_URL</code> environment variable.
          Default: <code>http://localhost:5000</code>
        </p>
        <p>
          Make sure the Kosty API server is running before testing endpoints.
        </p>
      </div>
    </div>
  );
};

export default Home;
