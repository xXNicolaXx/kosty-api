import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Pages
import Home from './pages/Home';
import HealthPage from './pages/HealthPage';
import AccountIdPage from './pages/AccountIdPage';
import ServicesPage from './pages/ServicesPage';
import AuditPage from './pages/AuditPage';
import CostsPage from './pages/CostsPage';
import CostsTrendsPage from './pages/CostsTrendsPage';
import CostsAnomaliesPage from './pages/CostsAnomaliesPage';
import BudgetsPage from './pages/BudgetsPage';
import GuardDutyPage from './pages/GuardDutyPage';
import AlertsFeedPage from './pages/AlertsFeedPage';
import AlertsSummaryPage from './pages/AlertsSummaryPage';
import AlertsConfigurePage from './pages/AlertsConfigurePage';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <Link to="/" className="brand">
            <span className="logo">💰</span>
            Kosty API Test Dashboard
          </Link>
          <div className="nav-links">
            <a href="https://github.com/kosty-cloud/kosty" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <a href="http://localhost:5000" target="_blank" rel="noopener noreferrer">
              API Server
            </a>
          </div>
        </nav>

        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/account-id" element={<AccountIdPage />} />
            <Route path="/services" element={<ServicesPage />} />
            <Route path="/audit" element={<AuditPage />} />
            <Route path="/costs" element={<CostsPage />} />
            <Route path="/costs-trends" element={<CostsTrendsPage />} />
            <Route path="/costs-anomalies" element={<CostsAnomaliesPage />} />
            <Route path="/budgets" element={<BudgetsPage />} />
            <Route path="/guardduty" element={<GuardDutyPage />} />
            <Route path="/alerts-feed" element={<AlertsFeedPage />} />
            <Route path="/alerts-summary" element={<AlertsSummaryPage />} />
            <Route path="/alerts-configure" element={<AlertsConfigurePage />} />
          </Routes>
        </div>

        <footer className="footer">
          <p>
            Kosty API Test Dashboard - Built with React + Vite + TypeScript
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
