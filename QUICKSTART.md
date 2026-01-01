# Quick Start Guide: Kosty API

This guide will help you get the Kosty API up and running in minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Flask-CORS, boto3, and other required packages.

## Step 2: Configure AWS Credentials

The API needs AWS credentials to scan your infrastructure. Choose one method:

### Option A: Environment Variables (Recommended for production)
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Option B: AWS Credentials File (For local development)
```bash
# File: ~/.aws/credentials
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

### Option C: IAM Instance Profile (For EC2 deployment)
When running on EC2, the API can use the instance's IAM role automatically. No configuration needed!

## Step 3: Start the API Server

```bash
./start-api.sh
```

Or manually:
```bash
python3 -m kosty.api
```

The server will start on `http://0.0.0.0:5000` by default.

## Step 4: Test the API

### Using cURL
```bash
# Health check
curl http://localhost:5000/health

# Run a simple audit
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-east-1"]}'
```

### Using the Example Script
```bash
cd examples
python3 simple_api_usage.py
```

## Step 5: View Results

The API returns JSON with:
- All discovered issues
- Cost savings estimates (monthly & annual)
- Resource details
- Security findings

Example response:
```json
{
  "scan_timestamp": "2024-01-01T12:00:00",
  "summary": {
    "total_issues": 42,
    "total_monthly_savings": 1234.56,
    "total_annual_savings": 14814.72
  },
  "results": {
    "current": {
      "ec2": {...},
      "s3": {...},
      ...
    }
  }
}
```

## Configuration Options

### Environment Variables

- `PORT`: Server port (default: 5000)
- `HOST`: Bind address (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: false)

Example:
```bash
PORT=8080 HOST=127.0.0.1 DEBUG=true python3 -m kosty.api
```

### API Request Parameters

When calling `/api/audit`, you can customize:

```json
{
  "regions": ["us-east-1", "eu-west-1"],  // AWS regions to scan
  "max_workers": 10,                       // Parallel workers
  "organization": false,                   // Organization-wide scan
  "profile": "default"                     // Config profile to use
}
```

## Common Use Cases

### 1. Single Region Audit
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-east-1"]}'
```

### 2. Multi-Region Audit
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "regions": ["us-east-1", "us-west-2", "eu-west-1"],
    "max_workers": 10
  }'
```

### 3. Organization-Wide Audit
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "organization": true,
    "regions": ["us-east-1"],
    "max_workers": 20
  }'
```

## Deployment

### Development
```bash
./start-api.sh
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 kosty.api:app
```

### Docker
```bash
docker build -t kosty-api .
docker run -p 5000:5000 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  kosty-api
```

## Troubleshooting

### "Connection refused" error
Make sure the API server is running:
```bash
./start-api.sh
```

### "AWS credentials not found" error
Set up AWS credentials using one of the methods in Step 2.

### "Permission denied" errors
Ensure your AWS credentials have the necessary permissions:
- `ec2:Describe*`
- `s3:List*`, `s3:Get*`
- `rds:Describe*`
- `iam:Get*`, `iam:List*`
- And similar read-only permissions for other services

### API returns 500 errors
Enable debug mode to see detailed errors:
```bash
DEBUG=true python3 -m kosty.api
```

## Next Steps

- Read the [complete API documentation](API_README.md)
- Explore [example scripts](examples/README.md)
- Review [CLI documentation](docs/DOCUMENTATION.md)
- Check out the [dashboard](dashboard/README.md)

## Support

- GitHub Issues: https://github.com/kosty-cloud/kosty/issues
- Documentation: https://github.com/kosty-cloud/kosty
- Email: yassir@kosty.cloud
