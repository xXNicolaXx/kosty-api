#!/usr/bin/env python3
"""
Example: Simple API Usage with Cross-Account Role
This script demonstrates how to use the Kosty API to run audits using IAM role assumption.
"""

import requests
import json
import sys

# API endpoint
API_URL = "http://localhost:5000"

# User configuration - REPLACE THESE VALUES
USER_ROLE_ARN = "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole"
EXTERNAL_ID = "your-unique-external-id"  # Unique identifier for your user

def main():
    print("🚀 Kosty API - Simple Audit Example")
    print("=" * 60)
    
    # 0. Get API Account ID (needed for IAM role setup)
    print("\n0. Getting API server Account ID...")
    response = requests.get(f"{API_URL}/api/account-id")
    if response.status_code == 200:
        account_info = response.json()
        print(f"   API Account ID: {account_info['account_id']}")
        print(f"   Use this when creating the IAM role trust policy")
    else:
        print(f"   Warning: Could not get account ID: {response.text}")
    
    # 1. Check API health
    print("\n1. Checking API health...")
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.json()['status']}")
    
    # 2. List available services
    print("\n2. Getting available services...")
    response = requests.get(f"{API_URL}/api/services")
    services = response.json()
    print(f"   Total services: {services['total_services']}")
    print(f"   Services: {', '.join(list(services['services'].keys())[:5])}...")
    
    # 3. Check if user has configured their credentials
    if USER_ROLE_ARN == "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole":
        print("\n⚠️  WARNING: You need to configure your IAM role ARN!")
        print("   Please update USER_ROLE_ARN and EXTERNAL_ID in this script.")
        print("\n📚 Setup Instructions:")
        print("   1. Create an IAM role in your AWS account named 'KostyAuditRole'")
        print(f"   2. Set trust policy to allow account: {account_info.get('account_id', 'UNKNOWN')}")
        print("   3. Add read-only permissions (e.g., ReadOnlyAccess policy)")
        print("   4. Update this script with your role ARN and external ID")
        sys.exit(0)
    
    # 3. Run a simple audit
    print("\n3. Running audit for us-east-1...")
    audit_request = {
        "user_role_arn": USER_ROLE_ARN,
        "external_id": EXTERNAL_ID,
        "regions": ["us-east-1"],
        "max_workers": 5
    }
    
    print("   This may take a few minutes...")
    response = requests.post(
        f"{API_URL}/api/audit",
        json=audit_request,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        results = response.json()
        
        print("\n✅ Audit completed successfully!")
        print("=" * 60)
        print(f"📅 Scan time: {results['scan_timestamp']}")
        print(f"🔍 Total issues: {results['summary']['total_issues']}")
        print(f"💰 Monthly savings: ${results['summary']['total_monthly_savings']:,.2f}")
        print(f"📈 Annual savings: ${results['summary']['total_annual_savings']:,.2f}")
        
        # Save full results to file
        with open('audit_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\n📄 Full results saved to: audit_results.json")
        
        # Show top issues by service
        print("\n🎯 Issues by service:")
        for account_id, account_data in results['results'].items():
            for service, service_data in account_data.items():
                for check, check_data in service_data.items():
                    if check_data['count'] > 0:
                        savings = check_data.get('monthly_savings', 0)
                        if savings > 0:
                            print(f"   • {service.upper()}: {check_data['count']} issues (${savings:,.2f}/mo)")
                        else:
                            print(f"   • {service.upper()}: {check_data['count']} issues")
    else:
        print(f"\n❌ Audit failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server.")
        print("   Make sure the server is running:")
        print("   From repository root: ./start-api.sh")
        print("   Or: python3 -m kosty.api")
    except Exception as e:
        print(f"\n❌ Error: {e}")
