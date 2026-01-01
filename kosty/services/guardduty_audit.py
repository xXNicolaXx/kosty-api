import boto3
from typing import List, Dict, Any
from datetime import datetime, timedelta

class GuardDutyAuditService:
    """
    AWS GuardDuty service for security threat detection and monitoring.
    Checks GuardDuty activation status and retrieves high-severity findings.
    """
    
    # Constants
    HIGH_SEVERITY_THRESHOLD = 7.0  # Severity score threshold for high/critical findings
    CRITICAL_SEVERITY_THRESHOLD = 9.0
    MEDIUM_SEVERITY_THRESHOLD = 4.0
    
    # GuardDuty finding type to action-oriented recommendation mappings
    FINDING_TYPE_ACTIONS = {
        'Backdoor:EC2': 'URGENT: EC2 instance may be compromised and acting as command & control server. Isolate instance, investigate network traffic, and terminate if confirmed malicious.',
        'Behavior:EC2': 'EC2 instance is behaving abnormally. Review CloudTrail logs, check for unauthorized API calls, and verify legitimate usage patterns.',
        'CryptoCurrency:EC2': 'EC2 instance may be mining cryptocurrency. This wastes compute resources. Stop the instance, investigate processes, and secure your environment.',
        'Pentest:IAM': 'IAM credentials are being used in penetration testing activities. If unauthorized, rotate credentials immediately and review IAM permissions.',
        'Persistence:IAM': 'Attacker may be trying to maintain access. Review IAM user/role activity, rotate credentials, and enable MFA.',
        'Policy:IAM': 'IAM entity has suspicious permissions. Review and restrict permissions following least-privilege principle.',
        'PrivilegeEscalation:IAM': 'IAM entity attempting privilege escalation. Revoke excessive permissions and investigate activity.',
        'Recon:IAM': 'IAM credentials used for reconnaissance. This may indicate account compromise. Rotate credentials and review recent API calls.',
        'ResourceConsumption:IAM': 'Unusual resource usage detected. May indicate account compromise or misconfiguration. Review usage patterns.',
        'Stealth:IAM': 'CloudTrail logging has been disabled or modified. Re-enable CloudTrail immediately and investigate who made the changes.',
        'Trojan:EC2': 'EC2 instance may have malware. Isolate instance immediately, take snapshot for forensics, and launch clean replacement.',
        'UnauthorizedAccess:EC2': 'Unauthorized access to EC2 instance detected. Review security groups, rotate SSH keys, and check for unauthorized users.',
        'UnauthorizedAccess:IAM': 'Suspicious login activity detected. Enable MFA, rotate credentials, and review recent account activity.',
        'Exfiltration:S3': 'Data may be exfiltrated from S3. Review bucket policies, enable S3 access logging, and investigate suspicious downloads.',
        'Impact:EC2': 'EC2 instance involved in denial of service or other impacts. Isolate instance and investigate traffic patterns.',
    }
    
    def __init__(self):
        self.cost_checks = []
        self.security_checks = ['check_guardduty_status', 'get_high_severity_findings']
    
    def audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """Run complete security audit (security checks only, no cost for this service)"""
        results = []
        results.extend(self.security_audit(session, region, config_manager=config_manager, **kwargs))
        return results
    
    def cost_audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """No cost checks for GuardDuty"""
        return []
    
    def security_audit(self, session: boto3.Session, region: str, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """Run all security checks"""
        results = []
        
        for check in self.security_checks:
            check_method = getattr(self, check, None)
            if check_method and callable(check_method):
                try:
                    check_results = check_method(session, region, config_manager=config_manager, **kwargs)
                    results.extend(check_results)
                except Exception as e:
                    print(f"Error running {check}: {e}")
        
        return results
    
    def check_guardduty_status(self, session: boto3.Session, region: str, 
                               config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Check if GuardDuty is enabled in the region and account.
        """
        gd = session.client('guardduty', region_name=region)
        sts = session.client('sts')
        account_id = sts.get_caller_identity()['Account']
        results = []
        
        try:
            # List detectors
            detectors_response = gd.list_detectors()
            detectors = detectors_response.get('DetectorIds', [])
            
            if not detectors:
                # GuardDuty not enabled - high priority recommendation
                results.append({
                    'AccountId': account_id,
                    'Service': 'GuardDuty',
                    'service': 'GuardDuty',
                    'Region': region,
                    'region': region,
                    'Issue': 'GuardDuty not enabled',
                    'Details': 'GuardDuty provides intelligent threat detection for your AWS environment',
                    'type': 'security',
                    'severity': 'high',
                    'check': 'guardduty_enabled',
                    'resource_id': f'guardduty-{region}',
                    'resource_name': f'GuardDuty ({region})',
                    'Recommendation': 'Enable GuardDuty to monitor for malicious activity and unauthorized behavior. Cost: ~$4.66/month for 1000 CloudTrail events + data analyzed',
                    'Action': 'Go to GuardDuty console and click "Get Started" to enable threat detection'
                })
            else:
                # GuardDuty is enabled - check status
                for detector_id in detectors:
                    detector = gd.get_detector(DetectorId=detector_id)
                    status = detector.get('Status', 'UNKNOWN')
                    
                    if status != 'ENABLED':
                        results.append({
                            'AccountId': account_id,
                            'Service': 'GuardDuty',
                            'service': 'GuardDuty',
                            'Region': region,
                            'region': region,
                            'Issue': f'GuardDuty detector is {status}',
                            'Details': f'Detector {detector_id} is not actively monitoring',
                            'type': 'security',
                            'severity': 'high',
                            'check': 'guardduty_enabled',
                            'resource_id': detector_id,
                            'resource_name': f'GuardDuty Detector {detector_id}',
                            'Recommendation': 'Enable the GuardDuty detector to resume threat monitoring'
                        })
                    else:
                        # GuardDuty is active - informational
                        results.append({
                            'AccountId': account_id,
                            'Service': 'GuardDuty',
                            'service': 'GuardDuty',
                            'Region': region,
                            'region': region,
                            'Issue': 'GuardDuty is active',
                            'Details': {
                                'detector_id': detector_id,
                                'status': status,
                                'finding_publishing_frequency': detector.get('FindingPublishingFrequency', 'UNKNOWN'),
                                'created_at': detector.get('CreatedAt', 'Unknown'),
                                'updated_at': detector.get('UpdatedAt', 'Unknown')
                            },
                            'type': 'info',
                            'severity': 'info',
                            'check': 'guardduty_status',
                            'resource_id': detector_id,
                            'resource_name': f'GuardDuty Detector {detector_id}'
                        })
        
        except Exception as e:
            # Handle permission errors or GuardDuty not available
            if 'AccessDenied' in str(e) or 'UnauthorizedOperation' in str(e):
                results.append({
                    'AccountId': account_id,
                    'Service': 'GuardDuty',
                    'service': 'GuardDuty',
                    'Region': region,
                    'region': region,
                    'Issue': 'Cannot access GuardDuty',
                    'Details': 'Insufficient permissions to check GuardDuty status',
                    'type': 'recommendation',
                    'severity': 'low',
                    'check': 'guardduty_access',
                    'resource_id': f'guardduty-{region}',
                    'resource_name': 'GuardDuty Access',
                    'Recommendation': 'Grant guardduty:ListDetectors and guardduty:GetDetector permissions'
                })
            else:
                print(f"Error checking GuardDuty status: {e}")
        
        return results
    
    def get_high_severity_findings(self, session: boto3.Session, region: str, 
                                   days: int = 30, config_manager=None, **kwargs) -> List[Dict[str, Any]]:
        """
        Get high and critical severity GuardDuty findings from the last N days.
        Translates findings into clear, action-oriented recommendations.
        """
        gd = session.client('guardduty', region_name=region)
        sts = session.client('sts')
        account_id = sts.get_caller_identity()['Account']
        results = []
        
        try:
            # List detectors first
            detectors_response = gd.list_detectors()
            detectors = detectors_response.get('DetectorIds', [])
            
            if not detectors:
                # No detector, skip findings check
                return results
            
            for detector_id in detectors:
                # List findings with filters for high/critical severity
                findings_response = gd.list_findings(
                    DetectorId=detector_id,
                    FindingCriteria={
                        'Criterion': {
                            'severity': {
                                'Gte': self.HIGH_SEVERITY_THRESHOLD  # High (7.0-8.9) and Critical (9.0-10.0)
                            },
                            'updatedAt': {
                                'Gte': int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
                            }
                        }
                    },
                    MaxResults=50  # Limit to most recent findings
                )
                
                finding_ids = findings_response.get('FindingIds', [])
                
                if not finding_ids:
                    # No high-severity findings - good news!
                    continue
                
                # Get detailed finding information
                findings_details = gd.get_findings(
                    DetectorId=detector_id,
                    FindingIds=finding_ids
                )
                
                for finding in findings_details.get('Findings', []):
                    severity = finding.get('Severity', 0)
                    finding_type = finding.get('Type', 'Unknown')
                    title = finding.get('Title', 'Unknown Threat')
                    description = finding.get('Description', '')
                    
                    # Translate finding to action-oriented recommendation
                    action = self._translate_finding_to_action(finding_type, finding)
                    
                    # Determine severity label
                    if severity >= self.CRITICAL_SEVERITY_THRESHOLD:
                        severity_label = 'critical'
                    elif severity >= self.HIGH_SEVERITY_THRESHOLD:
                        severity_label = 'high'
                    elif severity >= self.MEDIUM_SEVERITY_THRESHOLD:
                        severity_label = 'medium'
                    else:
                        severity_label = 'low'
                    
                    # Get resource information
                    resource = finding.get('Resource', {})
                    resource_type = resource.get('ResourceType', 'Unknown')
                    
                    results.append({
                        'AccountId': account_id,
                        'Service': 'GuardDuty',
                        'service': 'GuardDuty',
                        'Region': region,
                        'region': region,
                        'Issue': f'Security threat: {title}',
                        'Details': {
                            'finding_id': finding.get('Id', 'Unknown'),
                            'finding_type': finding_type,
                            'severity_score': severity,
                            'description': description,
                            'resource_type': resource_type,
                            'resource_details': resource,
                            'first_seen': finding.get('CreatedAt', ''),
                            'last_seen': finding.get('UpdatedAt', ''),
                            'count': finding.get('Service', {}).get('Count', 1)
                        },
                        'type': 'security',
                        'severity': severity_label,
                        'check': 'guardduty_finding',
                        'resource_id': finding.get('Id', 'unknown'),
                        'resource_name': title,
                        'Recommendation': action,
                        'Action': action
                    })
        
        except Exception as e:
            # If we can't get findings, it might be because GuardDuty is not enabled
            if 'BadRequestException' in str(e) or 'NotFoundException' in str(e):
                # Already handled in check_guardduty_status
                pass
            else:
                print(f"Error getting GuardDuty findings: {e}")
        
        return results
    
    def _translate_finding_to_action(self, finding_type: str, finding: Dict[str, Any]) -> str:
        """
        Translate GuardDuty finding type into clear, action-oriented recommendation.
        """
        # Use finding type actions from class constant
        actions = self.FINDING_TYPE_ACTIONS
        
        # Try to find matching action based on finding type prefix
        for pattern, action in actions.items():
            if finding_type.startswith(pattern):
                return action
        
        # Default action if no specific match
        return f'Security issue detected: {finding_type}. Review finding details and take appropriate remediation action based on severity.'
    
    def combine_with_cost_alerts(self, cost_findings: List[Dict[str, Any]], 
                                 security_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine cost and security findings to identify resources that are both expensive and suspicious.
        For example: idle EC2 instances that also have security findings.
        """
        combined_alerts = []
        
        # Create a map of resources from security findings
        security_resources = {}
        for finding in security_findings:
            resource_id = finding.get('resource_id', '')
            if resource_id:
                security_resources[resource_id] = finding
        
        # Check cost findings against security findings
        for cost_finding in cost_findings:
            resource_id = cost_finding.get('resource_id', '')
            
            if resource_id in security_resources:
                security_finding = security_resources[resource_id]
                
                # Create combined alert
                combined_alerts.append({
                    'AccountId': cost_finding.get('AccountId'),
                    'Service': 'Combined',
                    'service': 'Combined',
                    'Region': cost_finding.get('Region'),
                    'region': cost_finding.get('Region'),
                    'Issue': f'Resource is both costly and has security issues: {resource_id}',
                    'Details': {
                        'cost_issue': cost_finding.get('Issue'),
                        'security_issue': security_finding.get('Issue'),
                        'cost_details': cost_finding.get('Details'),
                        'security_details': security_finding.get('Details')
                    },
                    'type': 'combined',
                    'severity': 'critical',
                    'check': 'cost_security_combined',
                    'resource_id': resource_id,
                    'resource_name': cost_finding.get('resource_name', resource_id),
                    'monthly_cost': cost_finding.get('monthly_cost', 0),
                    'Recommendation': f'PRIORITY: Address both cost and security issues. {cost_finding.get("Recommendation", "")} AND {security_finding.get("Recommendation", "")}'
                })
        
        return combined_alerts
