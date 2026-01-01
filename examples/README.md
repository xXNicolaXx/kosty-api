# Kosty API Examples

This directory contains example scripts demonstrating how to use the Kosty API.

## Prerequisites

1. **Start the API server:**
   ```bash
   cd ..
   ./start-api.sh
   ```

2. **Install Python requests library** (for Python examples):
   ```bash
   pip install requests
   ```

## Examples

### 1. Simple API Usage (Python)
**File:** `simple_api_usage.py`

Basic example showing how to:
- Check API health
- List available services
- Run a simple audit
- Process and display results

**Run:**
```bash
python3 simple_api_usage.py
```

### 2. Multi-Region Audit (Python)
**File:** `multi_region_audit.py`

Advanced example demonstrating:
- Auditing multiple AWS regions simultaneously
- Processing large result sets
- Finding top cost savings opportunities
- Saving detailed results to files

**Run:**
```bash
python3 multi_region_audit.py
```

### 3. cURL Examples (Bash)
**File:** `curl_examples.sh`

Shell script showing basic API usage with cURL:
- Health checks
- Getting API information
- Listing services
- Running audits with JSON payloads

**Run:**
```bash
./curl_examples.sh
```

## API Endpoints Reference

### GET /health
Health check endpoint
```bash
curl http://localhost:5000/health
```

### GET /
API documentation
```bash
curl http://localhost:5000/
```

### GET /api/services
List all available services and checks
```bash
curl http://localhost:5000/api/services
```

### POST /api/audit
Run a comprehensive audit

**Simple audit:**
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Multi-region audit:**
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "regions": ["us-east-1", "us-west-2", "eu-west-1"],
    "max_workers": 10
  }'
```

**Organization-wide audit:**
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "organization": true,
    "regions": ["us-east-1"],
    "max_workers": 20,
    "cross_account_role": "OrganizationAccountAccessRole"
  }'
```

## Integration Examples

### JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

async function runAudit() {
  const response = await fetch('http://localhost:5000/api/audit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      regions: ['us-east-1'],
      max_workers: 5
    })
  });
  
  const results = await response.json();
  console.log(`Found ${results.summary.total_issues} issues`);
  console.log(`Potential savings: $${results.summary.total_monthly_savings}/month`);
}

runAudit();
```

### Python with requests
```python
import requests

response = requests.post(
    'http://localhost:5000/api/audit',
    json={'regions': ['us-east-1'], 'max_workers': 5}
)

results = response.json()
print(f"Found {results['summary']['total_issues']} issues")
print(f"Potential savings: ${results['summary']['total_monthly_savings']}/month")
```

### Go
```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

func main() {
    data := map[string]interface{}{
        "regions": []string{"us-east-1"},
        "max_workers": 5,
    }
    
    jsonData, _ := json.Marshal(data)
    resp, _ := http.Post(
        "http://localhost:5000/api/audit",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    
    var results map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&results)
    
    summary := results["summary"].(map[string]interface{})
    fmt.Printf("Found %.0f issues\n", summary["total_issues"])
    fmt.Printf("Potential savings: $%.2f/month\n", summary["total_monthly_savings"])
}
```

## Troubleshooting

### "Connection refused" error
Make sure the API server is running:
```bash
cd ..
./start-api.sh
```

### "Module not found: requests"
Install the requests library:
```bash
pip install requests
```

### Audit takes too long
- Reduce the number of regions
- Increase `max_workers` for parallel processing
- Run audits for specific services instead of all

## Further Reading

- [Complete API Documentation](../API_README.md)
- [Main Documentation](../docs/DOCUMENTATION.md)
- [Configuration Guide](../docs/CONFIGURATION.md)
