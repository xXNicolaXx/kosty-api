"""
Alert Feed Service - Aggregates and manages alerts from all sources
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

class AlertFeedService:
    """
    Service to aggregate, filter, and manage alerts from cost, security, and resource optimization sources.
    """
    
    def __init__(self):
        self.alert_types = {
            'cost_spike': 'Cost Spike',
            'idle_resource': 'Idle/Unused Resource',
            'security_high': 'High Severity Security',
            'budget_threshold': 'Budget Threshold Exceeded',
            'cost_anomaly': 'Cost Anomaly Detected',
            'combined': 'Combined Cost & Security'
        }
    
    def aggregate_alerts(self, all_findings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aggregate alerts from all audit results into a unified feed.
        
        Args:
            all_findings: Dictionary of all findings from comprehensive scan
            
        Returns:
            List of aggregated alerts sorted by priority
        """
        alerts = []
        
        # Process findings from each account
        for account_id, account_findings in all_findings.items():
            for service, service_findings in account_findings.items():
                # Each service can have multiple check types
                for check_type, check_results in service_findings.items():
                    if isinstance(check_results, dict) and 'items' in check_results:
                        items = check_results['items']
                    elif isinstance(check_results, list):
                        items = check_results
                    else:
                        continue
                    
                    for item in items:
                        alert = self._create_alert_from_finding(item, account_id, service)
                        if alert:
                            alerts.append(alert)
        
        # Sort alerts by priority (severity and cost impact)
        alerts.sort(key=lambda x: (
            self._severity_priority(x.get('severity', 'low')),
            x.get('monthly_cost', 0)
        ), reverse=True)
        
        return alerts
    
    def _create_alert_from_finding(self, finding: Dict[str, Any], 
                                   account_id: str, service: str) -> Dict[str, Any]:
        """
        Convert a finding into a standardized alert format.
        """
        # Determine alert type
        alert_type = self._determine_alert_type(finding)
        
        if not alert_type:
            return None
        
        # Create standardized alert
        alert = {
            'alert_id': f"{account_id}-{service}-{finding.get('resource_id', 'unknown')}-{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'account_id': account_id,
            'service': service,
            'alert_type': alert_type,
            'alert_type_label': self.alert_types.get(alert_type, 'Unknown'),
            'severity': finding.get('severity', 'medium'),
            'title': finding.get('Issue', 'Unknown Issue'),
            'description': self._format_description(finding),
            'resource_id': finding.get('resource_id', 'unknown'),
            'resource_name': finding.get('resource_name', 'Unknown'),
            'region': finding.get('Region', finding.get('region', 'unknown')),
            'monthly_cost': finding.get('monthly_cost', finding.get('monthly_savings', 0)),
            'recommendation': finding.get('Recommendation', finding.get('Action', '')),
            'details': finding.get('Details', {}),
            'check': finding.get('check', 'unknown')
        }
        
        return alert
    
    def _determine_alert_type(self, finding: Dict[str, Any]) -> str:
        """
        Determine the alert type based on finding characteristics.
        """
        check = finding.get('check', '').lower()
        finding_type = finding.get('type', '').lower()
        severity = finding.get('severity', '').lower()
        
        # Combined alerts
        if finding_type == 'combined':
            return 'combined'
        
        # Security alerts
        if finding_type == 'security' and severity in ['high', 'critical']:
            return 'security_high'
        
        # Cost-related alerts
        if 'anomaly' in check:
            return 'cost_anomaly'
        
        if 'budget' in check and 'threshold' in check:
            return 'budget_threshold'
        
        # Idle/unused resources
        idle_patterns = ['idle', 'unused', 'stopped', 'empty', 'orphan', 'unattached']
        if any(pattern in check for pattern in idle_patterns):
            return 'idle_resource'
        
        # Cost spikes (high cost items)
        if finding_type == 'cost' and finding.get('monthly_cost', 0) > 100:
            return 'cost_spike'
        
        # Default to info type for non-actionable items
        return None
    
    def _severity_priority(self, severity: str) -> int:
        """
        Convert severity to numeric priority for sorting.
        """
        priorities = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'info': 1
        }
        return priorities.get(severity.lower(), 0)
    
    def _format_description(self, finding: Dict[str, Any]) -> str:
        """
        Format a clear description for the alert.
        """
        issue = finding.get('Issue', '')
        details = finding.get('Details', {})
        
        if isinstance(details, str):
            return f"{issue}. {details}"
        elif isinstance(details, dict):
            # Extract key information from details
            key_info = []
            if 'total_cost' in details:
                key_info.append(f"Cost: ${details['total_cost']:.2f}")
            if 'usage_percentage' in details:
                key_info.append(f"Usage: {details['usage_percentage']:.1f}%")
            if 'severity_score' in details:
                key_info.append(f"Severity: {details['severity_score']}/10")
            
            if key_info:
                return f"{issue}. {', '.join(key_info)}"
        
        return issue
    
    def filter_alerts(self, alerts: List[Dict[str, Any]], 
                     alert_types: List[str] = None,
                     severity_min: str = None,
                     days: int = None) -> List[Dict[str, Any]]:
        """
        Filter alerts based on criteria.
        
        Args:
            alert_types: List of alert types to include
            severity_min: Minimum severity level (low, medium, high, critical)
            days: Only include alerts from last N days
        """
        filtered = alerts
        
        # Filter by alert type
        if alert_types:
            filtered = [a for a in filtered if a.get('alert_type') in alert_types]
        
        # Filter by severity
        if severity_min:
            min_priority = self._severity_priority(severity_min)
            filtered = [a for a in filtered if self._severity_priority(a.get('severity', 'low')) >= min_priority]
        
        # Filter by date
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered = [a for a in filtered if datetime.fromisoformat(a.get('timestamp', '')) >= cutoff_date]
        
        return filtered
    
    def get_alert_summary(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for alerts.
        """
        summary = {
            'total_alerts': len(alerts),
            'by_type': {},
            'by_severity': {},
            'by_service': {},
            'total_monthly_cost_impact': 0,
            'top_alerts': []
        }
        
        for alert in alerts:
            # Count by type
            alert_type = alert.get('alert_type', 'unknown')
            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            
            # Count by severity
            severity = alert.get('severity', 'unknown')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by service
            service = alert.get('service', 'unknown')
            summary['by_service'][service] = summary['by_service'].get(service, 0) + 1
            
            # Sum cost impact
            summary['total_monthly_cost_impact'] += alert.get('monthly_cost', 0)
        
        # Get top 10 alerts by priority
        summary['top_alerts'] = alerts[:10]
        
        return summary
    
    def generate_daily_feed(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a daily alert feed report.
        """
        # Filter to last 24 hours
        daily_alerts = self.filter_alerts(alerts, days=1)
        
        feed = {
            'feed_date': datetime.now().strftime('%Y-%m-%d'),
            'feed_type': 'daily',
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_alert_summary(daily_alerts),
            'alerts': daily_alerts,
            'recommendations': self._generate_recommendations(daily_alerts)
        }
        
        return feed
    
    def _generate_recommendations(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """
        Generate top-level recommendations based on alert patterns.
        """
        recommendations = []
        
        # Analyze alert patterns
        high_cost_alerts = [a for a in alerts if a.get('monthly_cost', 0) > 50]
        security_alerts = [a for a in alerts if a.get('alert_type') == 'security_high']
        idle_alerts = [a for a in alerts if a.get('alert_type') == 'idle_resource']
        
        if high_cost_alerts:
            total_potential_savings = sum(a.get('monthly_cost', 0) for a in high_cost_alerts)
            recommendations.append(f"💰 Potential savings: ${total_potential_savings:.2f}/month by addressing {len(high_cost_alerts)} high-cost items")
        
        if security_alerts:
            recommendations.append(f"🔒 Security: {len(security_alerts)} high-severity security issues require immediate attention")
        
        if idle_alerts:
            recommendations.append(f"♻️ Resource optimization: {len(idle_alerts)} idle/unused resources can be removed")
        
        # GuardDuty recommendation
        guardduty_needed = any('GuardDuty not enabled' in a.get('title', '') for a in alerts)
        if guardduty_needed:
            recommendations.append("🛡️ Enable GuardDuty for continuous threat detection (~$4.66/month)")
        
        # Budget recommendation
        budget_exceeded = any(a.get('alert_type') == 'budget_threshold' for a in alerts)
        if budget_exceeded:
            recommendations.append("⚠️ Budget thresholds exceeded - review spending immediately")
        
        return recommendations
