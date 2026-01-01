#!/bin/bash
#
# Example: Simple cURL-based API Usage
# This script demonstrates basic API calls using cURL
#

API_URL="http://localhost:5000"

echo "🚀 Kosty API - cURL Examples"
echo "============================================================"

# 1. Health Check
echo -e "\n1️⃣  Health Check"
echo "   Command: curl $API_URL/health"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# 2. Get API Info
echo -e "\n2️⃣  API Information"
echo "   Command: curl $API_URL/"
curl -s "$API_URL/" | python3 -m json.tool
echo ""

# 3. List Services
echo -e "\n3️⃣  List Available Services"
echo "   Command: curl $API_URL/api/services"
echo "   (Showing first few services...)"
curl -s "$API_URL/api/services" | python3 -m json.tool | head -40
echo "   ..."
echo ""

# 4. Run Simple Audit
echo -e "\n4️⃣  Run Simple Audit (Single Region)"
echo "   Command: curl -X POST $API_URL/api/audit -H 'Content-Type: application/json' -d '{}'"
echo "   Note: This will use default settings (us-east-1, single account)"
echo "   Running audit..."

AUDIT_RESULT=$(curl -s -X POST "$API_URL/api/audit" \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-east-1"], "max_workers": 5}')

# Check if audit was successful
if echo "$AUDIT_RESULT" | grep -q "scan_timestamp"; then
    echo "   ✅ Audit completed!"
    
    # Extract summary
    TOTAL_ISSUES=$(echo "$AUDIT_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['summary']['total_issues'])")
    MONTHLY_SAVINGS=$(echo "$AUDIT_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data['summary']['total_monthly_savings']:.2f}\")")
    ANNUAL_SAVINGS=$(echo "$AUDIT_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data['summary']['total_annual_savings']:.2f}\")")
    
    echo ""
    echo "   📊 Summary:"
    echo "      Total Issues: $TOTAL_ISSUES"
    echo "      Monthly Savings: \$$MONTHLY_SAVINGS"
    echo "      Annual Savings: \$$ANNUAL_SAVINGS"
    
    # Save full results
    echo "$AUDIT_RESULT" | python3 -m json.tool > audit_results.json
    echo "      Full results saved to: audit_results.json"
else
    echo "   ❌ Audit failed or returned unexpected data"
    echo "$AUDIT_RESULT" | python3 -m json.tool
fi

echo ""
echo "============================================================"
echo "✅ Examples completed!"
echo ""
echo "💡 More examples:"
echo "   - Multi-region: examples/multi_region_audit.py"
echo "   - Python client: examples/simple_api_usage.py"
echo "   - Full API docs: API_README.md"
