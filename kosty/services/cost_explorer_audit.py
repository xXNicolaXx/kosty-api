import boto3
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

class CostExplorerAuditService:
    """
    AWS Cost Explorer service for cost analysis, trend monitoring, and anomaly detection.
    Supports multi-account cost aggregation and budget monitoring.
    """
    
    def __init__(self):
        self.cost_checks = ['analyze_costs_by_service', 'detect_cost_anomalies', 'check_budget_thresholds']
        self.security_checks = []
    
    def audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """Run complete cost audit (cost checks only, no security for this service)"""
        results = []
        results.extend(self.cost_audit(session, region, config_manager=config_manager, **kwargs))
        return results
    
    def cost_audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """Run all cost optimization checks"""
        results = []
        
        for check in self.cost_checks:
            check_method = getattr(self, check, None)
            if check_method and callable(check_method):
                try:
                    check_results = check_method(session, region, config_manager=config_manager, **kwargs)
                    results.extend(check_results)
                except Exception as e:
                    print(f"Error running {check}: {e}")
        
        return results
    
    def security_audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """No security checks for Cost Explorer"""
        return []
    
    def analyze_costs_by_service(self, session: boto3.Session, region: str, 
                                  period: str = 'MONTHLY', 
                                  config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Analyze costs by AWS service for the specified period.
        
        Args:
            period: DAILY, WEEKLY, or MONTHLY
        """
        ce = session.client('ce', region_name='us-east-1')  # Cost Explorer is global
        sts = session.client('sts')
        account_id = sts.get_caller_identity()['Account']
        results = []
        
        try:
            # Define time ranges based on period
            end_date = datetime.now().date()
            
            if period == 'DAILY':
                start_date = end_date - timedelta(days=7)
                granularity = 'DAILY'
            elif period == 'WEEKLY':
                start_date = end_date - timedelta(days=28)
                granularity = 'DAILY'
            else:  # MONTHLY
                start_date = end_date - timedelta(days=90)
                granularity = 'MONTHLY'
            
            # Services to monitor specifically
            target_services = ['Amazon Elastic Compute Cloud - Compute', 'Amazon Simple Storage Service',
                             'AWS Lambda', 'Amazon Relational Database Service', 
                             'Amazon CloudFront', 'Amazon API Gateway', 'Amazon DynamoDB']
            
            # Get cost and usage data
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity=granularity,
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            # Process results
            service_costs = {}
            for result_by_time in response.get('ResultsByTime', []):
                for group in result_by_time.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if service not in service_costs:
                        service_costs[service] = {
                            'total': 0,
                            'data_points': []
                        }
                    
                    service_costs[service]['total'] += cost
                    service_costs[service]['data_points'].append({
                        'date': result_by_time['TimePeriod']['Start'],
                        'cost': cost
                    })
            
            # Create findings for services with significant costs
            for service, data in service_costs.items():
                if data['total'] > 1.0:  # Only report services costing > $1
                    # Calculate trend
                    if len(data['data_points']) >= 2:
                        recent_cost = sum(dp['cost'] for dp in data['data_points'][-3:]) / min(3, len(data['data_points'][-3:]))
                        older_cost = sum(dp['cost'] for dp in data['data_points'][:3]) / min(3, len(data['data_points'][:3]))
                        trend_pct = ((recent_cost - older_cost) / older_cost * 100) if older_cost > 0 else 0
                        trend = 'increasing' if trend_pct > 10 else ('decreasing' if trend_pct < -10 else 'stable')
                    else:
                        trend = 'unknown'
                        trend_pct = 0
                    
                    results.append({
                        'AccountId': account_id,
                        'Service': 'CostExplorer',
                        'service': 'CostExplorer',
                        'Region': 'global',
                        'region': 'global',
                        'Issue': f'{service} - {period.lower()} cost analysis',
                        'Details': {
                            'aws_service': service,
                            'total_cost': round(data['total'], 2),
                            'period': period,
                            'trend': trend,
                            'trend_percentage': round(trend_pct, 2),
                            'data_points': data['data_points']
                        },
                        'type': 'info',
                        'severity': 'info',
                        'check': 'cost_by_service',
                        'resource_id': service,
                        'resource_name': service,
                        'monthly_cost': round(data['total'], 2) if period == 'MONTHLY' else round(data['total'] * 30 / ((end_date - start_date).days), 2)
                    })
        
        except Exception as e:
            # If Cost Explorer is not available, return mock data
            if 'OptInRequired' in str(e) or 'AccessDenied' in str(e):
                return self._get_mock_cost_data(account_id, period)
            print(f"Error analyzing costs by service: {e}")
        
        return results
    
    def detect_cost_anomalies(self, session: boto3.Session, region: str, 
                             config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Detect cost anomalies using AWS Cost Anomaly Detection.
        """
        ce = session.client('ce', region_name='us-east-1')
        sts = session.client('sts')
        account_id = sts.get_caller_identity()['Account']
        results = []
        
        try:
            # Get anomaly monitors
            monitors_response = ce.get_anomaly_monitors()
            monitors = monitors_response.get('AnomalyMonitors', [])
            
            if not monitors:
                # Suggest enabling anomaly detection
                results.append({
                    'AccountId': account_id,
                    'Service': 'CostExplorer',
                    'service': 'CostExplorer',
                    'Region': 'global',
                    'region': 'global',
                    'Issue': 'Cost Anomaly Detection not configured',
                    'Details': 'Enable Cost Anomaly Detection to automatically identify unusual spending patterns',
                    'type': 'recommendation',
                    'severity': 'medium',
                    'check': 'cost_anomaly_detection',
                    'resource_id': 'anomaly-detection',
                    'resource_name': 'Cost Anomaly Detection',
                    'Recommendation': 'Set up Cost Anomaly Detection monitors in AWS Cost Explorer console'
                })
                return results
            
            # Get anomalies from the last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            anomalies_response = ce.get_anomalies(
                DateInterval={
                    'StartDate': start_date.strftime('%Y-%m-%d'),
                    'EndDate': end_date.strftime('%Y-%m-%d')
                },
                Feedback='ALL'
            )
            
            for anomaly in anomalies_response.get('Anomalies', []):
                impact = anomaly.get('Impact', {})
                max_impact = impact.get('MaxImpact', 0)
                total_impact = impact.get('TotalImpact', 0)
                
                # Only report significant anomalies (> $10 impact)
                if float(total_impact) > 10:
                    results.append({
                        'AccountId': account_id,
                        'Service': 'CostExplorer',
                        'service': 'CostExplorer',
                        'Region': 'global',
                        'region': 'global',
                        'Issue': 'Cost anomaly detected',
                        'Details': {
                            'anomaly_id': anomaly['AnomalyId'],
                            'anomaly_score': anomaly.get('AnomalyScore', {}).get('MaxScore', 0),
                            'impact': round(float(total_impact), 2),
                            'max_impact': round(float(max_impact), 2),
                            'dimension_value': anomaly.get('DimensionValue', 'Unknown'),
                            'start_date': anomaly.get('AnomalyStartDate', ''),
                            'end_date': anomaly.get('AnomalyEndDate', '')
                        },
                        'type': 'cost',
                        'severity': 'high' if float(total_impact) > 100 else 'medium',
                        'check': 'cost_anomaly',
                        'resource_id': anomaly['AnomalyId'],
                        'resource_name': f"Anomaly-{anomaly.get('DimensionValue', 'Unknown')}",
                        'monthly_cost_impact': round(float(total_impact), 2)
                    })
        
        except Exception as e:
            # If anomaly detection is not enabled, return recommendation
            if 'AccessDenied' in str(e) or 'not subscribed' in str(e):
                results.append({
                    'AccountId': account_id,
                    'Service': 'CostExplorer',
                    'service': 'CostExplorer',
                    'Region': 'global',
                    'region': 'global',
                    'Issue': 'Cost Anomaly Detection not enabled',
                    'Details': 'Enable Cost Anomaly Detection to monitor for unusual spending',
                    'type': 'recommendation',
                    'severity': 'medium',
                    'check': 'cost_anomaly_detection',
                    'resource_id': 'anomaly-detection',
                    'resource_name': 'Cost Anomaly Detection',
                    'Recommendation': 'Enable Cost Anomaly Detection in AWS Cost Explorer'
                })
            else:
                print(f"Error detecting cost anomalies: {e}")
        
        return results
    
    def check_budget_thresholds(self, session: boto3.Session, region: str, 
                                config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Check AWS Budgets and identify budgets that have exceeded or are approaching thresholds.
        """
        budgets = session.client('budgets', region_name='us-east-1')  # Budgets is global
        sts = session.client('sts')
        account_id = sts.get_caller_identity()['Account']
        results = []
        
        try:
            # List all budgets
            budgets_response = budgets.describe_budgets(AccountId=account_id)
            
            if not budgets_response.get('Budgets'):
                # Recommend setting up budgets
                results.append({
                    'AccountId': account_id,
                    'Service': 'CostExplorer',
                    'service': 'CostExplorer',
                    'Region': 'global',
                    'region': 'global',
                    'Issue': 'No AWS Budgets configured',
                    'Details': 'Set up AWS Budgets to receive alerts when costs exceed thresholds',
                    'type': 'recommendation',
                    'severity': 'medium',
                    'check': 'budget_configuration',
                    'resource_id': 'budgets',
                    'resource_name': 'AWS Budgets',
                    'Recommendation': 'Configure AWS Budgets with appropriate thresholds and alerts'
                })
                return results
            
            for budget in budgets_response.get('Budgets', []):
                budget_name = budget['BudgetName']
                budget_limit = float(budget['BudgetLimit']['Amount'])
                
                # Get actual spend
                calculated_spend = budget.get('CalculatedSpend', {})
                actual_spend = float(calculated_spend.get('ActualSpend', {}).get('Amount', 0))
                forecasted_spend = float(calculated_spend.get('ForecastedSpend', {}).get('Amount', 0))
                
                # Calculate usage percentage
                usage_pct = (actual_spend / budget_limit * 100) if budget_limit > 0 else 0
                forecast_pct = (forecasted_spend / budget_limit * 100) if budget_limit > 0 else 0
                
                # Report if budget is exceeded or approaching threshold (>80%)
                if usage_pct > 80 or forecast_pct > 100:
                    severity = 'critical' if usage_pct > 100 else 'high' if usage_pct > 90 else 'medium'
                    
                    results.append({
                        'AccountId': account_id,
                        'Service': 'CostExplorer',
                        'service': 'CostExplorer',
                        'Region': 'global',
                        'region': 'global',
                        'Issue': f'Budget threshold alert: {budget_name}',
                        'Details': {
                            'budget_name': budget_name,
                            'budget_limit': round(budget_limit, 2),
                            'actual_spend': round(actual_spend, 2),
                            'forecasted_spend': round(forecasted_spend, 2),
                            'usage_percentage': round(usage_pct, 2),
                            'forecast_percentage': round(forecast_pct, 2),
                            'time_period': budget.get('TimeUnit', 'MONTHLY')
                        },
                        'type': 'cost',
                        'severity': severity,
                        'check': 'budget_threshold',
                        'resource_id': budget_name,
                        'resource_name': budget_name,
                        'Recommendation': f'Review spending for {budget_name}. Current: ${actual_spend:.2f} / ${budget_limit:.2f} ({usage_pct:.1f}%)'
                    })
        
        except Exception as e:
            # If budgets are not configured, return recommendation
            if 'AccessDenied' in str(e):
                results.append({
                    'AccountId': account_id,
                    'Service': 'CostExplorer',
                    'service': 'CostExplorer',
                    'Region': 'global',
                    'region': 'global',
                    'Issue': 'Cannot access AWS Budgets',
                    'Details': 'Ensure you have permissions to access AWS Budgets API',
                    'type': 'recommendation',
                    'severity': 'low',
                    'check': 'budget_access',
                    'resource_id': 'budgets',
                    'resource_name': 'AWS Budgets'
                })
            else:
                print(f"Error checking budget thresholds: {e}")
        
        return results
    
    def _get_mock_cost_data(self, account_id: str, period: str) -> List[Dict[str, Any]]:
        """
        Generate mock cost data for testing when Cost Explorer is not available.
        This provides realistic sample data matching production API response format.
        """
        results = []
        
        # Mock services with realistic cost data
        mock_services = {
            'Amazon Elastic Compute Cloud - Compute': {'daily': 15.50, 'weekly': 108.50, 'monthly': 465.00},
            'Amazon Simple Storage Service': {'daily': 3.20, 'weekly': 22.40, 'monthly': 96.00},
            'AWS Lambda': {'daily': 0.85, 'weekly': 5.95, 'monthly': 25.50},
            'Amazon Relational Database Service': {'daily': 12.00, 'weekly': 84.00, 'monthly': 360.00},
            'Amazon CloudFront': {'daily': 2.10, 'weekly': 14.70, 'monthly': 63.00},
            'Amazon API Gateway': {'daily': 0.45, 'weekly': 3.15, 'monthly': 13.50},
            'Amazon DynamoDB': {'daily': 1.80, 'weekly': 12.60, 'monthly': 54.00}
        }
        
        for service, costs in mock_services.items():
            cost_key = period.lower() if period.lower() in costs else 'monthly'
            total_cost = costs[cost_key]
            
            # Generate mock data points
            if period == 'DAILY':
                days = 7
                data_points = [{'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                               'cost': round(total_cost / days + (i % 3 - 1) * 0.5, 2)} 
                              for i in range(days)]
            elif period == 'WEEKLY':
                days = 28
                data_points = [{'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
                               'cost': round(total_cost / days + (i % 5 - 2) * 0.3, 2)} 
                              for i in range(0, days, 7)]
            else:  # MONTHLY
                months = 3
                data_points = [{'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'), 
                               'cost': round(total_cost + (i % 3 - 1) * 20, 2)} 
                              for i in range(months)]
            
            # Calculate trend
            if len(data_points) >= 2:
                recent = data_points[0]['cost']
                older = data_points[-1]['cost']
                trend_pct = ((recent - older) / older * 100) if older > 0 else 0
                trend = 'increasing' if trend_pct > 10 else ('decreasing' if trend_pct < -10 else 'stable')
            else:
                trend = 'stable'
                trend_pct = 0
            
            results.append({
                'AccountId': account_id,
                'Service': 'CostExplorer',
                'service': 'CostExplorer',
                'Region': 'global',
                'region': 'global',
                'Issue': f'{service} - {period.lower()} cost analysis (MOCK DATA)',
                'Details': {
                    'aws_service': service,
                    'total_cost': round(total_cost, 2),
                    'period': period,
                    'trend': trend,
                    'trend_percentage': round(trend_pct, 2),
                    'data_points': data_points,
                    'note': 'This is mock data for testing purposes'
                },
                'type': 'info',
                'severity': 'info',
                'check': 'cost_by_service',
                'resource_id': f'mock-{service}',
                'resource_name': service,
                'monthly_cost': round(costs['monthly'], 2)
            })
        
        return results
