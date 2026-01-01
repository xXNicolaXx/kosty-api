# Quick Start Guide: Kosty API

This guide will help you get the Kosty API up and running in minutes.

## Authentication Model

The Kosty API uses **AWS cross-account IAM roles** for secure access. This means:

1. **You create an IAM role** in your AWS account
2. **Configure it to trust** the API's AWS account
3. **API assumes the role** to get temporary credentials
4. **No permanent credentials** are stored or transmitted

This is the industry-standard secure pattern for SaaS applications.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Flask-CORS, boto3, and other required packages.

## Step 2: Start the API Server

```bash
./start-api.sh
```

Or manually:
```bash
python3 -m kosty.api
```

The server will start on `http://0.0.0.0:5000` by default.

## Step 3: Get the API's AWS Account ID

```bash
curl http://localhost:5000/api/account-id
```

**Response:**
```json
{
  "account_id": "123456789012",
  "arn": "arn:aws:sts::123456789012:assumed-role/...",
  "instructions": "Use this Account ID when creating the trust relationship..."
}
```

**Save this Account ID** - you'll need it to configure the IAM role.

## Step 4: Create IAM Role in Your AWS Account

### 4a. Create the Role

Go to AWS Console → IAM → Roles → Create Role

**Trusted Entity Type:** AWS Account
**Account ID:** Enter the Account ID from Step 3
**Role Name:** `KostyAuditRole` (or your preferred name)

### 4b. Configure Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "your-unique-external-id"
        }
      }
    }
  ]
}
```

Replace:
- `123456789012` with the Account ID from Step 3
- `your-unique-external-id` with a unique identifier (e.g., your user ID)

### 4c. Attach Permissions Policy

Attach the **ReadOnlyAccess** managed policy, or create a custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:List*",
        "s3:Get*",
        "rds:Describe*",
        "lambda:List*",
        "lambda:Get*",
        "iam:Get*",
        "iam:List*",
        "cloudwatch:*",
        "elasticloadbalancing:Describe*",
        "dynamodb:Describe*",
        "route53:List*",
        "apigateway:GET",
        "backup:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4d. Copy the Role ARN

After creating the role, copy its ARN. It looks like:
```
arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole
```

## Step 5: Run an Audit

### Using cURL
```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole",
    "external_id": "your-unique-external-id",
    "regions": ["us-east-1"]
  }'
```

### Using the Example Script

Edit `examples/simple_api_usage.py` and update:
```python
USER_ROLE_ARN = "arn:aws:iam::YOUR_ACCOUNT_ID:role/KostyAuditRole"
EXTERNAL_ID = "your-unique-external-id"
```

Then run:
```bash
cd examples
python3 simple_api_usage.py
```

## Step 6: View Results

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
