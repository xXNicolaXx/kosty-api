#!/usr/bin/env python3
"""
Example: Simple API Usage
This script demonstrates how to use the Kosty API to run a basic audit.
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:5000"

def main():
    print("🚀 Kosty API - Simple Audit Example")
    print("=" * 60)
    
    # 1. Check API health
    print("\n1. Checking API health...")
    response = requests.get(f"{API_URL}/health")
    print(f"   Status: {response.json()['status']}")
    
    # 2. List available services
    print("\n2. Getting available services...")
    response = requests.get(f"{API_URL}/api/services")
    services = response.json()
    print(f"   Total services: {services['total_services']}")
    print(f"   Services: {', '.join(services['services'].keys())}")
    
    # 3. Run a simple audit
    print("\n3. Running audit for us-east-1...")
    audit_request = {
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
