#!/usr/bin/env python3
"""
Kosty API Server - RESTful API for AWS Cost Optimization & Security Audits
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

from kosty.core.scanner import ComprehensiveScanner
from kosty.core.config import ConfigManager
from kosty.core.alert_feed import AlertFeedService

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def run_audit_sync(
    organization: bool = False,
    regions: Optional[list] = None,
    max_workers: int = 5,
    cross_account_role: str = 'OrganizationAccountAccessRole',
    org_admin_account_id: Optional[str] = None,
    profile: str = 'default',
    config_file: Optional[str] = None,
    user_role_arn: Optional[str] = None,
    external_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a comprehensive audit and return results as JSON.
    This is a synchronous wrapper around the async scanner.
    
    Args:
        user_role_arn: ARN of the role in the user's AWS account to assume
        external_id: External ID for additional security when assuming the role
    """
    import boto3
    
    session = None
    config_manager = None
    
    # Priority: user_role_arn > config file > default credentials
    if user_role_arn:
        # Assume role in user's account
        try:
            sts = boto3.client('sts')
            
            assume_role_params = {
                'RoleArn': user_role_arn,
                'RoleSessionName': 'kosty-api-audit',
                'DurationSeconds': 3600
            }
            
            # Add external ID if provided for additional security
            if external_id:
                assume_role_params['ExternalId'] = external_id
            
            response = sts.assume_role(**assume_role_params)
            
            session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken']
            )
        except Exception as e:
            import sys
            print(f"Error: Failed to assume role {user_role_arn}: {e}", file=sys.stderr)
            raise Exception(f"Failed to assume role in user's account: {str(e)}")
    else:
        # Try to use config file or default credentials
        try:
            config_manager = ConfigManager(
                config_file=config_file,
                profile=profile
            )
            session = config_manager.get_aws_session()
        except Exception as e:
            # Config manager initialization failed, will use default AWS credentials
            import sys
            print(f"Warning: Config manager initialization failed: {e}", file=sys.stderr)
            print("Using default AWS credentials from environment or credentials file", file=sys.stderr)
            config_manager = None
            session = None
    
    # Default to us-east-1 if no regions specified
    if regions is None:
        regions = ['us-east-1']
    
    # Create scanner
    scanner = ComprehensiveScanner(
        organization=organization,
        regions=regions,
        max_workers=max_workers,
        cross_account_role=cross_account_role,
        org_admin_account_id=org_admin_account_id,
        config_manager=config_manager,
        session=session
    )
    
    # Run scan
    reporter = asyncio.run(scanner.run_comprehensive_scan())
    
    # Prepare response data
    response_data = {
        'scan_timestamp': reporter.scan_timestamp.isoformat(),
        'organization': reporter.organization,
        'org_admin_account_id': reporter.org_admin_account_id,
        'results': reporter.results,
        'summary': {
            'total_issues': sum(
                sum(cmd['count'] for cmd in svc.values()) 
                for acc in reporter.results.values() 
                for svc in acc.values()
            ),
            'total_monthly_savings': sum(
                sum(cmd.get('monthly_savings', 0) for cmd in svc.values()) 
                for acc in reporter.results.values() 
                for svc in acc.values()
            )
        }
    }
    
    # Add annual savings
    response_data['summary']['total_annual_savings'] = (
        response_data['summary']['total_monthly_savings'] * 12
    )
    
    return response_data


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API documentation"""
    return jsonify({
        'name': 'Kosty API',
        'version': '1.0.0',
        'description': 'AWS Cost Optimization & Security Audit API',
        'endpoints': {
            '/': 'API documentation (this page)',
            '/health': 'Health check endpoint',
            '/api/account-id': 'Get API server AWS Account ID (needed for IAM role setup)',
            '/api/audit': 'Run comprehensive AWS audit (POST)',
            '/api/services': 'List available AWS services for auditing (GET)',
            '/api/costs': 'Get cost analysis by service (POST)',
            '/api/costs/trends': 'Get cost trends over time (POST)',
            '/api/costs/anomalies': 'Detect cost anomalies (POST)',
            '/api/budgets': 'Check budget thresholds (POST)',
            '/api/guardduty': 'Check GuardDuty status and findings (POST)',
            '/api/alerts/feed': 'Get alert feed (daily or real-time) (POST)',
            '/api/alerts/summary': 'Get alert summary statistics (POST)',
            '/api/alerts/configure': 'Configure alert thresholds (POST)'
        },
        'documentation': 'https://github.com/kosty-cloud/kosty'
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'kosty-api'
    })


@app.route('/api/account-id', methods=['GET'])
def get_account_id():
    """
    Get the AWS Account ID of the API server.
    Users need this to create the trust relationship in their IAM role.
    
    Response (JSON):
    {
        "account_id": "123456789012",
        "instructions": "Use this Account ID when creating the IAM role in your AWS account"
    }
    """
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        return jsonify({
            'account_id': identity['Account'],
            'arn': identity['Arn'],
            'instructions': 'Use this Account ID when creating the trust relationship for the IAM role in your AWS account'
        })
    except Exception as e:
        import os
        debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        error_response = {
            'error': str(e),
            'type': type(e).__name__
        }
        
        if debug_mode:
            error_response['traceback'] = traceback.format_exc()
        
        return jsonify(error_response), 500


@app.route('/api/services', methods=['GET'])
def list_services():
    """List all available services that can be audited"""
    services_info = {
        'ec2': {
            'name': 'EC2',
            'description': 'Elastic Compute Cloud instances',
            'checks': ['stopped_instances', 'idle_instances', 'oversized_instances', 'ssh_open', 'imdsv1']
        },
        's3': {
            'name': 'S3',
            'description': 'Simple Storage Service buckets',
            'checks': ['empty_buckets', 'public_read_access', 'encryption_at_rest', 'lifecycle_policy']
        },
        'rds': {
            'name': 'RDS',
            'description': 'Relational Database Service instances',
            'checks': ['public_databases', 'oversized_instances', 'unused_read_replicas', 'unencrypted_storage']
        },
        'lambda': {
            'name': 'Lambda',
            'description': 'Serverless compute functions',
            'checks': ['unused_functions', 'over_provisioned_memory']
        },
        'ebs': {
            'name': 'EBS',
            'description': 'Elastic Block Store volumes',
            'checks': ['orphan_volumes', 'unencrypted_orphan', 'old_snapshots']
        },
        'iam': {
            'name': 'IAM',
            'description': 'Identity and Access Management',
            'checks': ['root_access_keys', 'unused_roles', 'inactive_users', 'old_access_keys']
        },
        'eip': {
            'name': 'EIP',
            'description': 'Elastic IP addresses',
            'checks': ['unattached_eips', 'eips_on_stopped_instances']
        },
        'lb': {
            'name': 'Load Balancer',
            'description': 'Application and Network Load Balancers',
            'checks': ['no_healthy_targets', 'unused_load_balancers']
        },
        'nat': {
            'name': 'NAT Gateway',
            'description': 'Network Address Translation gateways',
            'checks': ['unused_gateways', 'redundant_gateways']
        },
        'sg': {
            'name': 'Security Groups',
            'description': 'VPC security groups',
            'checks': ['unused_groups', 'overly_permissive']
        },
        'cloudwatch': {
            'name': 'CloudWatch',
            'description': 'Monitoring and logging service',
            'checks': ['unused_alarms', 'expensive_log_retention']
        },
        'dynamodb': {
            'name': 'DynamoDB',
            'description': 'NoSQL database service',
            'checks': ['idle_tables', 'over_provisioned_capacity']
        },
        'route53': {
            'name': 'Route53',
            'description': 'DNS web service',
            'checks': ['unused_hosted_zones']
        },
        'apigateway': {
            'name': 'API Gateway',
            'description': 'API management service',
            'checks': ['unused_apis']
        },
        'backup': {
            'name': 'AWS Backup',
            'description': 'Centralized backup service',
            'checks': ['empty_vaults']
        },
        'snapshots': {
            'name': 'EBS Snapshots',
            'description': 'EBS volume snapshots',
            'checks': ['old_snapshots', 'public_snapshots']
        },
        'cost_explorer': {
            'name': 'Cost Explorer',
            'description': 'AWS cost analysis and monitoring',
            'checks': ['cost_by_service', 'cost_anomaly_detection', 'budget_threshold']
        },
        'guardduty': {
            'name': 'GuardDuty',
            'description': 'Intelligent threat detection service',
            'checks': ['guardduty_enabled', 'guardduty_finding']
        }
    }
    
    return jsonify({
        'services': services_info,
        'total_services': len(services_info)
    })


@app.route('/api/audit', methods=['POST'])
def run_audit():
    """
    Run a comprehensive AWS audit.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",  // Required: Role ARN in user's account
        "external_id": "unique-external-id",      // Recommended: External ID for security
        "regions": ["us-east-1"],                 // Optional: List of regions (default: ["us-east-1"])
        "max_workers": 5,                         // Optional: Parallel workers (default: 5)
        "organization": false,                    // Optional: Run org-wide scan (default: false)
        "cross_account_role": "...",              // Optional: Cross-account role name
        "org_admin_account_id": "...",            // Optional: Org admin account ID
        "profile": "default",                     // Optional: Config profile (default: "default")
        "config_file": null                       // Optional: Path to config file
    }
    
    Response (JSON):
    {
        "scan_timestamp": "2024-01-01T12:00:00",
        "results": { ... },
        "summary": {
            "total_issues": 42,
            "total_monthly_savings": 1234.56,
            "total_annual_savings": 14814.72
        }
    }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Extract parameters with defaults
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        organization = data.get('organization', False)
        regions = data.get('regions', ['us-east-1'])
        max_workers = data.get('max_workers', 5)
        cross_account_role = data.get('cross_account_role', 'OrganizationAccountAccessRole')
        org_admin_account_id = data.get('org_admin_account_id')
        profile = data.get('profile', 'default')
        config_file = data.get('config_file')
        
        # Validate regions is a list
        if not isinstance(regions, list):
            return jsonify({
                'error': 'regions must be a list of region names'
            }), 400
        
        # Run the audit
        result = run_audit_sync(
            organization=organization,
            regions=regions,
            max_workers=max_workers,
            cross_account_role=cross_account_role,
            org_admin_account_id=org_admin_account_id,
            profile=profile,
            config_file=config_file,
            user_role_arn=user_role_arn,
            external_id=external_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        # Return error details
        import os
        debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        error_response = {
            'error': str(e),
            'type': type(e).__name__
        }
        
        # Only include traceback in debug mode to avoid leaking system information
        if debug_mode:
            error_response['traceback'] = traceback.format_exc()
        
        return jsonify(error_response), 500


@app.route('/api/costs', methods=['POST'])
def get_costs():
    """
    Get cost analysis by AWS service.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id",
        "regions": ["us-east-1"],
        "period": "MONTHLY"  // DAILY, WEEKLY, or MONTHLY
    }
    """
    try:
        from kosty.services.cost_explorer_audit import CostExplorerAuditService
        import boto3
        
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        regions = data.get('regions', ['us-east-1'])
        period = data.get('period', 'MONTHLY')
        
        # Create session
        session = _create_session(user_role_arn, external_id)
        
        # Run cost analysis
        service = CostExplorerAuditService()
        results = []
        
        for region in regions:
            cost_data = service.analyze_costs_by_service(session, region, period=period)
            results.extend(cost_data)
        
        return jsonify({
            'period': period,
            'regions': regions,
            'costs': results,
            'total_services': len(results)
        })
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/costs/trends', methods=['POST'])
def get_cost_trends():
    """
    Get cost trends over time for specific services.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id",
        "services": ["EC2", "S3", "Lambda"],  // Optional: specific services
        "days": 30  // Number of days to analyze
    }
    """
    try:
        from kosty.services.cost_explorer_audit import CostExplorerAuditService
        
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        days = data.get('days', 30)
        
        session = _create_session(user_role_arn, external_id)
        
        # Get cost trends (use daily granularity for trends)
        service = CostExplorerAuditService()
        results = service.analyze_costs_by_service(session, 'us-east-1', period='DAILY')
        
        return jsonify({
            'days': days,
            'trends': results
        })
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/costs/anomalies', methods=['POST'])
def detect_anomalies():
    """
    Detect cost anomalies using AWS Cost Anomaly Detection.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id"
    }
    """
    try:
        from kosty.services.cost_explorer_audit import CostExplorerAuditService
        
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        
        session = _create_session(user_role_arn, external_id)
        
        service = CostExplorerAuditService()
        anomalies = service.detect_cost_anomalies(session, 'us-east-1')
        
        return jsonify({
            'anomalies': anomalies,
            'total_anomalies': len(anomalies)
        })
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/budgets', methods=['POST'])
def check_budgets():
    """
    Check AWS Budget thresholds.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id"
    }
    """
    try:
        from kosty.services.cost_explorer_audit import CostExplorerAuditService
        
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        
        session = _create_session(user_role_arn, external_id)
        
        service = CostExplorerAuditService()
        budget_alerts = service.check_budget_thresholds(session, 'us-east-1')
        
        return jsonify({
            'budget_alerts': budget_alerts,
            'total_alerts': len(budget_alerts)
        })
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/guardduty', methods=['POST'])
def check_guardduty():
    """
    Check GuardDuty status and get high-severity findings.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id",
        "regions": ["us-east-1"],
        "days": 30  // Days to look back for findings
    }
    """
    try:
        from kosty.services.guardduty_audit import GuardDutyAuditService
        
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        regions = data.get('regions', ['us-east-1'])
        days = data.get('days', 30)
        
        session = _create_session(user_role_arn, external_id)
        
        service = GuardDutyAuditService()
        all_findings = []
        
        for region in regions:
            findings = service.audit(session, region, days=days)
            all_findings.extend(findings)
        
        # Separate status and findings
        status_info = [f for f in all_findings if f.get('check') in ['guardduty_enabled', 'guardduty_status']]
        security_findings = [f for f in all_findings if f.get('check') == 'guardduty_finding']
        
        return jsonify({
            'regions': regions,
            'status': status_info,
            'findings': security_findings,
            'total_findings': len(security_findings)
        })
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/alerts/feed', methods=['POST'])
def get_alert_feed():
    """
    Get aggregated alert feed.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id",
        "regions": ["us-east-1"],
        "feed_type": "daily",  // "daily" or "realtime"
        "alert_types": [],  // Optional: filter by alert types
        "severity_min": "medium"  // Optional: minimum severity
    }
    """
    try:
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        regions = data.get('regions', ['us-east-1'])
        feed_type = data.get('feed_type', 'daily')
        alert_types = data.get('alert_types')
        severity_min = data.get('severity_min')
        
        # Run a comprehensive audit to get all findings
        result = run_audit_sync(
            organization=False,
            regions=regions,
            max_workers=5,
            user_role_arn=user_role_arn,
            external_id=external_id
        )
        
        # Aggregate alerts
        alert_service = AlertFeedService()
        alerts = alert_service.aggregate_alerts(result['results'])
        
        # Filter if requested
        if alert_types or severity_min:
            alerts = alert_service.filter_alerts(
                alerts, 
                alert_types=alert_types,
                severity_min=severity_min
            )
        
        # Generate feed
        if feed_type == 'daily':
            feed = alert_service.generate_daily_feed(alerts)
        else:
            feed = {
                'feed_type': 'realtime',
                'generated_at': datetime.now().isoformat(),
                'summary': alert_service.get_alert_summary(alerts),
                'alerts': alerts
            }
        
        return jsonify(feed)
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/alerts/summary', methods=['POST'])
def get_alert_summary():
    """
    Get summary statistics for alerts.
    
    Request body (JSON):
    {
        "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
        "external_id": "unique-external-id",
        "regions": ["us-east-1"]
    }
    """
    try:
        data = request.get_json() or {}
        user_role_arn = data.get('user_role_arn')
        external_id = data.get('external_id')
        regions = data.get('regions', ['us-east-1'])
        
        # Run audit
        result = run_audit_sync(
            organization=False,
            regions=regions,
            max_workers=5,
            user_role_arn=user_role_arn,
            external_id=external_id
        )
        
        # Get alert summary
        alert_service = AlertFeedService()
        alerts = alert_service.aggregate_alerts(result['results'])
        summary = alert_service.get_alert_summary(alerts)
        
        return jsonify(summary)
    
    except Exception as e:
        return _handle_error(e)


@app.route('/api/alerts/configure', methods=['POST'])
def configure_alerts():
    """
    Configure alert thresholds (stored in memory for this session).
    
    Request body (JSON):
    {
        "budget_threshold_percentage": 80,
        "cost_spike_threshold": 100,
        "idle_days_threshold": 7
    }
    """
    try:
        data = request.get_json() or {}
        
        # In a production system, these would be persisted to a database
        # For now, we'll just return the configuration
        config = {
            'budget_threshold_percentage': data.get('budget_threshold_percentage', 80),
            'cost_spike_threshold': data.get('cost_spike_threshold', 100),
            'idle_days_threshold': data.get('idle_days_threshold', 7),
            'configured_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'message': 'Alert thresholds configured',
            'configuration': config
        })
    
    except Exception as e:
        return _handle_error(e)


def _create_session(user_role_arn: str, external_id: str = None):
    """Helper to create AWS session with role assumption"""
    import boto3
    
    if user_role_arn:
        sts = boto3.client('sts')
        assume_role_params = {
            'RoleArn': user_role_arn,
            'RoleSessionName': 'kosty-api-request',
            'DurationSeconds': 3600
        }
        if external_id:
            assume_role_params['ExternalId'] = external_id
        
        response = sts.assume_role(**assume_role_params)
        return boto3.Session(
            aws_access_key_id=response['Credentials']['AccessKeyId'],
            aws_secret_access_key=response['Credentials']['SecretAccessKey'],
            aws_session_token=response['Credentials']['SessionToken']
        )
    else:
        return boto3.Session()


def _handle_error(e: Exception):
    """Helper to handle and format errors"""
    import os
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    error_response = {
        'error': str(e),
        'type': type(e).__name__
    }
    
    if debug_mode:
        error_response['traceback'] = traceback.format_exc()
    
    return jsonify(error_response), 500


def main():
    """Run the Flask development server"""
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"""
╔════════════════════════════════════════════════════╗
║       Kosty API Server Starting                    ║
╠════════════════════════════════════════════════════╣
║  🌐 Host: {host:<38s} ║
║  🔌 Port: {str(port):<38s} ║
║  🐛 Debug: {str(debug):<37s} ║
╠════════════════════════════════════════════════════╣
║  📚 Docs: http://{host}:{port}/<{' ' * max(0, 22 - len(host) - len(str(port)))} ║
║  🏥 Health: http://{host}:{port}/health<{' ' * max(0, 16 - len(host) - len(str(port)))} ║
║  🔍 Audit: POST http://{host}:{port}/api/audit<{' ' * max(0, 10 - len(host) - len(str(port)))} ║
╚════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
