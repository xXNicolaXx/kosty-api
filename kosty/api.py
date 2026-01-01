#!/usr/bin/env python3
"""
Kosty API Server - RESTful API for AWS Cost Optimization & Security Audits
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import os
from typing import Dict, Any, Optional
import traceback

from kosty.core.scanner import ComprehensiveScanner
from kosty.core.config import ConfigManager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def run_audit_sync(
    organization: bool = False,
    regions: Optional[list] = None,
    max_workers: int = 5,
    cross_account_role: str = 'OrganizationAccountAccessRole',
    org_admin_account_id: Optional[str] = None,
    profile: str = 'default',
    config_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a comprehensive audit and return results as JSON.
    This is a synchronous wrapper around the async scanner.
    """
    try:
        # Initialize config manager
        config_manager = ConfigManager(
            config_file=config_file,
            profile=profile
        )
        session = config_manager.get_aws_session()
    except Exception as e:
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
            '/api/audit': 'Run comprehensive AWS audit (POST)',
            '/api/services': 'List available AWS services for auditing (GET)'
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
        "organization": false,          // Optional: Run org-wide scan (default: false)
        "regions": ["us-east-1"],       // Optional: List of regions (default: ["us-east-1"])
        "max_workers": 5,               // Optional: Parallel workers (default: 5)
        "cross_account_role": "...",    // Optional: Cross-account role name
        "org_admin_account_id": "...",  // Optional: Org admin account ID
        "profile": "default",           // Optional: Config profile (default: "default")
        "config_file": null             // Optional: Path to config file
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
            config_file=config_file
        )
        
        return jsonify(result)
        
    except Exception as e:
        # Return error details
        error_trace = traceback.format_exc()
        return jsonify({
            'error': str(e),
            'traceback': error_trace
        }), 500


def main():
    """Run the Flask development server"""
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║          Kosty API Server Starting                    ║
    ╠═══════════════════════════════════════════════════════╣
    ║  🌐 Host: {host:40s}   ║
    ║  🔌 Port: {str(port):40s}   ║
    ║  🐛 Debug: {str(debug):39s}   ║
    ╠═══════════════════════════════════════════════════════╣
    ║  📚 API Documentation: http://{host}:{port}/        ║
    ║  🏥 Health Check: http://{host}:{port}/health       ║
    ║  🔍 Run Audit: POST http://{host}:{port}/api/audit  ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
