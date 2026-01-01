#!/usr/bin/env python3
"""
Example: Multi-Region Audit with Cross-Account Role
This script demonstrates how to run audits across multiple AWS regions using IAM role assumption.
"""

import requests
import json
from datetime import datetime
import sys

# API endpoint
API_URL = "http://localhost:5000"

# User configuration - REPLACE THESE VALUES
USER_ROLE_ARN = "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole"
EXTERNAL_ID = "your-unique-external-id"

def run_multi_region_audit(regions, role_arn, external_id):
    """Run audit across multiple regions"""
    print(f"\n🌍 Running audit across {len(regions)} regions...")
    print(f"   Regions: {', '.join(regions)}")
    
    audit_request = {
        "user_role_arn": role_arn,
        "external_id": external_id,
        "regions": regions,
        "max_workers": 10  # Increase workers for parallel processing
    }
    
    response = requests.post(
        f"{API_URL}/api/audit",
        json=audit_request,
        headers={"Content-Type": "application/json"},
        timeout=600  # 10 minute timeout for large scans
    )
    
    return response

def main():
    print("🚀 Kosty API - Multi-Region Audit Example")
    print("=" * 60)
    
    # Check if user has configured their credentials
    if USER_ROLE_ARN == "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole":
        print("\n⚠️  WARNING: You need to configure your IAM role ARN!")
        print("   Please update USER_ROLE_ARN and EXTERNAL_ID in this script.")
        print("\n📚 Setup Instructions:")
        print("   1. Get API Account ID: curl http://localhost:5000/api/account-id")
        print("   2. Create IAM role 'KostyAuditRole' in your AWS account")
        print("   3. Configure trust policy with API's account ID")
        print("   4. Add read-only permissions")
        print("   5. Update this script with your role ARN and external ID")
        sys.exit(0)
    
    # Define regions to scan
    regions = [
        "us-east-1",      # US East (N. Virginia)
        "us-west-2",      # US West (Oregon)
        "eu-west-1",      # Europe (Ireland)
        "ap-southeast-1"  # Asia Pacific (Singapore)
    ]
    
    # Run the audit
    print("\n⏳ Starting multi-region audit...")
    print("   This may take 5-10 minutes depending on your infrastructure...")
    
    try:
        response = run_multi_region_audit(regions, USER_ROLE_ARN, EXTERNAL_ID)
        
        if response.status_code == 200:
            results = response.json()
            
            print("\n✅ Multi-region audit completed!")
            print("=" * 60)
            
            # Summary
            summary = results['summary']
            print(f"\n📊 SUMMARY")
            print(f"   Total issues: {summary['total_issues']}")
            print(f"   Monthly savings: ${summary['total_monthly_savings']:,.2f}")
            print(f"   Annual savings: ${summary['total_annual_savings']:,.2f}")
            
            # Break down by region (account in this case)
            print(f"\n📍 BREAKDOWN BY ACCOUNT/REGION")
            for account_id, account_data in results['results'].items():
                account_issues = sum(
                    sum(cmd['count'] for cmd in svc.values())
                    for svc in account_data.values()
                )
                account_savings = sum(
                    sum(cmd.get('monthly_savings', 0) for cmd in svc.values())
                    for svc in account_data.values()
                )
                
                print(f"   Account {account_id}:")
                print(f"      Issues: {account_issues}")
                if account_savings > 0:
                    print(f"      Savings: ${account_savings:,.2f}/month")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multi_region_audit_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n📄 Full results saved to: {filename}")
            
            # Top cost savings opportunities
            print(f"\n💰 TOP COST SAVINGS OPPORTUNITIES")
            
            all_items = []
            for account_id, account_data in results['results'].items():
                for service, service_data in account_data.items():
                    for check, check_data in service_data.items():
                        for item in check_data.get('items', []):
                            if item.get('monthly_cost', 0) > 0:
                                all_items.append({
                                    'service': service,
                                    'resource': item.get('resource_name', item.get('resource_id', 'Unknown')),
                                    'issue': item.get('Issue', 'Unknown issue'),
                                    'monthly_cost': item.get('monthly_cost', 0),
                                    'region': item.get('region', 'Unknown')
                                })
            
            # Sort by monthly cost
            all_items.sort(key=lambda x: x['monthly_cost'], reverse=True)
            
            # Show top 10
            for idx, item in enumerate(all_items[:10], 1):
                print(f"   {idx}. {item['service'].upper()} - {item['resource']}")
                print(f"      Region: {item['region']}")
                print(f"      Issue: {item['issue']}")
                print(f"      Savings: ${item['monthly_cost']:,.2f}/month")
                print()
            
        else:
            print(f"\n❌ Audit failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out. The audit may still be running.")
        print("   Try increasing the timeout or reducing the number of regions.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server.")
        print("   Make sure the server is running: ./start-api.sh")
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user.")
