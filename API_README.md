# Kosty API - RESTful API Server

This document describes how to use the Kosty API server for AWS cost optimization and security audits.

## Overview

The Kosty API provides a RESTful web service interface to run AWS audits and retrieve cost optimization recommendations. It exposes the same powerful auditing capabilities as the CLI tool through HTTP endpoints.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Using the startup script (recommended)
./start-api.sh

# Or directly with Python
python3 -m kosty.api
```

The server will start on `http://0.0.0.0:5000` by default.

### 3. Test the API

```bash
# Check health
curl http://localhost:5000/health

# Get API documentation
curl http://localhost:5000/

# List available services
curl http://localhost:5000/api/services
```

## API Endpoints

### GET /

Returns API documentation and available endpoints.

**Response:**
```json
{
  "name": "Kosty API",
  "version": "1.0.0",
  "description": "AWS Cost Optimization & Security Audit API",
  "endpoints": { ... }
}
```

### GET /health

Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "kosty-api"
}
```

### GET /api/services

List all available AWS services that can be audited.

**Response:**
```json
{
  "services": {
    "ec2": {
      "name": "EC2",
      "description": "Elastic Compute Cloud instances",
      "checks": ["stopped_instances", "idle_instances", ...]
    },
    ...
  },
  "total_services": 16
}
```

### POST /api/audit

Run a comprehensive AWS audit across specified services and regions.

**Request Body:**
```json
{
  "organization": false,
  "regions": ["us-east-1", "eu-west-1"],
  "max_workers": 5,
  "cross_account_role": "OrganizationAccountAccessRole",
  "org_admin_account_id": null,
  "profile": "default",
  "config_file": null
}
```

**Parameters:**
- `organization` (boolean, optional): Run organization-wide scan. Default: `false`
- `regions` (array, optional): List of AWS regions to scan. Default: `["us-east-1"]`
- `max_workers` (integer, optional): Number of parallel workers. Default: `5`
- `cross_account_role` (string, optional): Cross-account IAM role name. Default: `"OrganizationAccountAccessRole"`
- `org_admin_account_id` (string, optional): Organization admin account ID
- `profile` (string, optional): Configuration profile to use. Default: `"default"`
- `config_file` (string, optional): Path to configuration file

**Response:**
```json
{
  "scan_timestamp": "2024-01-01T12:00:00",
  "organization": false,
  "org_admin_account_id": null,
  "results": {
    "current": {
      "ec2": {
        "audit": {
          "count": 5,
          "items": [...],
          "monthly_savings": 280.50
        }
      },
      "s3": {
        "audit": {
          "count": 3,
          "items": [...],
          "monthly_savings": 45.00
        }
      }
    }
  },
  "summary": {
    "total_issues": 8,
    "total_monthly_savings": 325.50,
    "total_annual_savings": 3906.00
  }
}
```

## Usage Examples

### Simple Single-Region Audit

```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Multi-Region Audit

```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "regions": ["us-east-1", "us-west-2", "eu-west-1"],
    "max_workers": 10
  }'
```

### Organization-Wide Audit

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

### Using a Specific Profile

```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "production",
    "regions": ["us-east-1"]
  }'
```

### Save Results to File

```bash
curl -X POST http://localhost:5000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-east-1"]}' \
  -o audit_results.json
```

## Configuration

### Environment Variables

The API server can be configured using environment variables:

- `PORT`: Port to run the server on (default: `5000`)
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `DEBUG`: Enable debug mode (default: `false`)

Example:
```bash
export PORT=8080
export HOST=127.0.0.1
export DEBUG=true
python3 -m kosty.api
```

### AWS Credentials

The API uses the same AWS credentials configuration as the CLI:

1. **Environment Variables**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
2. **AWS Credentials File**: `~/.aws/credentials`
3. **IAM Instance Profile**: For EC2 instances
4. **Configuration File**: Use `kosty.yaml` for profile-based credentials

See the [Configuration Guide](../docs/CONFIGURATION.md) for more details.

## Deployment

### Development Server

For local development and testing:

```bash
./start-api.sh
```

### Production Deployment

For production deployment, use a production-grade WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 kosty.api:app
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "-m", "kosty.api"]
```

Build and run:

```bash
docker build -t kosty-api .
docker run -p 5000:5000 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY kosty-api
```

### Cloud Hosting

The API can be hosted on various cloud platforms:

- **AWS Lambda + API Gateway**: Serverless deployment
- **AWS ECS/Fargate**: Container-based deployment
- **Heroku**: Platform-as-a-Service deployment
- **DigitalOcean App Platform**: Simple container deployment
- **Google Cloud Run**: Serverless container deployment

## Security Considerations

1. **Authentication**: The API currently does not include authentication. Add API keys, JWT, or OAuth before exposing to the internet.

2. **AWS Credentials**: Never expose AWS credentials in API responses. The API only uses credentials for internal AWS API calls.

3. **Rate Limiting**: Consider adding rate limiting to prevent abuse.

4. **HTTPS**: Use HTTPS in production to encrypt data in transit.

5. **Network Security**: Restrict access using firewalls, security groups, or VPC configurations.

## Response Format

All audit results include:

- **scan_timestamp**: When the scan was performed (ISO 8601 format)
- **results**: Detailed findings organized by account and service
- **summary**: High-level statistics including:
  - `total_issues`: Number of issues found
  - `total_monthly_savings`: Potential monthly cost savings
  - `total_annual_savings`: Potential annual cost savings

Each issue includes:
- Resource identifier (ARN, ID, or name)
- Service type
- Issue description
- Severity level
- Cost impact (when applicable)
- Recommendations

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `500`: Server error (audit failure, AWS errors)

Error responses include:
```json
{
  "error": "Error message",
  "type": "ExceptionType"
}
```

**Debug Mode:** When `DEBUG=true` is set, error responses also include detailed tracebacks. For security, this should only be enabled in development environments:
```json
{
  "error": "Error message",
  "type": "ExceptionType",
  "traceback": "Detailed error trace (only in debug mode)"
}
```

## Limitations

- Long-running audits may timeout depending on your deployment configuration
- Organization-wide scans can take several minutes depending on the number of accounts
- AWS API rate limits apply and may slow down large scans

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/kosty-cloud/kosty
- Email: yassir@kosty.cloud
- Documentation: https://github.com/kosty-cloud/kosty/blob/main/docs/DOCUMENTATION.md
