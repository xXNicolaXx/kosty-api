# Kosty API - New Features Documentation

## Overview of New Features

The Kosty API has been enhanced with comprehensive cost monitoring, security threat detection, and alert aggregation capabilities. These features help you:

1. **Monitor AWS costs** by service with trend analysis
2. **Detect cost anomalies** automatically
3. **Track budget thresholds** and receive alerts
4. **Monitor security threats** via GuardDuty integration
5. **Aggregate alerts** from all sources into a unified feed

## New API Endpoints

### 1. Cost Analysis by Service

Get detailed cost breakdown by AWS service.

**Endpoint:** `POST /api/costs`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id",
  "regions": ["us-east-1"],
  "period": "MONTHLY"
}
```

**Parameters:**
- `period`: `DAILY`, `WEEKLY`, or `MONTHLY` (default: `MONTHLY`)

**Response:**
```json
{
  "period": "MONTHLY",
  "regions": ["us-east-1"],
  "costs": [
    {
      "Service": "CostExplorer",
      "Issue": "Amazon Elastic Compute Cloud - Compute - monthly cost analysis",
      "Details": {
        "aws_service": "Amazon Elastic Compute Cloud - Compute",
        "total_cost": 465.00,
        "period": "MONTHLY",
        "trend": "stable",
        "trend_percentage": -2.5,
        "data_points": [...]
      },
      "monthly_cost": 465.00
    }
  ],
  "total_services": 7
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/api/costs \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345",
    "regions": ["us-east-1"],
    "period": "MONTHLY"
  }'
```

---

### 2. Cost Trends Analysis

Get cost trends over time to identify spending patterns.

**Endpoint:** `POST /api/costs/trends`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id",
  "days": 30
}
```

**Response:**
```json
{
  "days": 30,
  "trends": [
    {
      "Service": "CostExplorer",
      "Details": {
        "aws_service": "Amazon EC2",
        "total_cost": 108.50,
        "trend": "increasing",
        "trend_percentage": 15.3,
        "data_points": [
          {"date": "2024-01-01", "cost": 14.20},
          {"date": "2024-01-02", "cost": 15.80}
        ]
      }
    }
  ]
}
```

---

### 3. Cost Anomaly Detection

Detect unusual spending patterns automatically.

**Endpoint:** `POST /api/costs/anomalies`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id"
}
```

**Response:**
```json
{
  "anomalies": [
    {
      "Issue": "Cost anomaly detected",
      "Details": {
        "anomaly_id": "abc-123",
        "anomaly_score": 85.5,
        "impact": 125.50,
        "dimension_value": "Amazon S3",
        "start_date": "2024-01-15",
        "end_date": "2024-01-16"
      },
      "severity": "high",
      "monthly_cost_impact": 125.50
    }
  ],
  "total_anomalies": 1
}
```

**Notes:**
- If Cost Anomaly Detection is not enabled, the API will suggest enabling it
- If Cost Explorer is not available (requires opt-in), the API returns mock data for testing

---

### 4. Budget Threshold Monitoring

Check if AWS Budgets are approaching or exceeding thresholds.

**Endpoint:** `POST /api/budgets`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id"
}
```

**Response:**
```json
{
  "budget_alerts": [
    {
      "Issue": "Budget threshold alert: Monthly AWS Budget",
      "Details": {
        "budget_name": "Monthly AWS Budget",
        "budget_limit": 1000.00,
        "actual_spend": 850.00,
        "forecasted_spend": 1050.00,
        "usage_percentage": 85.0,
        "forecast_percentage": 105.0,
        "time_period": "MONTHLY"
      },
      "severity": "high",
      "Recommendation": "Review spending for Monthly AWS Budget. Current: $850.00 / $1000.00 (85.0%)"
    }
  ],
  "total_alerts": 1
}
```

---

### 5. GuardDuty Security Monitoring

Check GuardDuty status and retrieve high-severity security findings.

**Endpoint:** `POST /api/guardduty`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id",
  "regions": ["us-east-1", "eu-west-1"],
  "days": 30
}
```

**Parameters:**
- `days`: Number of days to look back for findings (default: 30)

**Response:**
```json
{
  "regions": ["us-east-1", "eu-west-1"],
  "status": [
    {
      "Issue": "GuardDuty is active",
      "Details": {
        "detector_id": "abc123",
        "status": "ENABLED",
        "finding_publishing_frequency": "FIFTEEN_MINUTES"
      },
      "severity": "info"
    }
  ],
  "findings": [
    {
      "Issue": "Security threat: Unusual API call from unusual location",
      "Details": {
        "finding_type": "Recon:IAMUser/UserPermissions",
        "severity_score": 8.5,
        "description": "IAM credentials used for reconnaissance",
        "first_seen": "2024-01-15T10:30:00Z",
        "count": 5
      },
      "severity": "high",
      "Recommendation": "IAM credentials used for reconnaissance. This may indicate account compromise. Rotate credentials and review recent API calls.",
      "Action": "IAM credentials used for reconnaissance. This may indicate account compromise. Rotate credentials and review recent API calls."
    }
  ],
  "total_findings": 1
}
```

**GuardDuty Finding Types:**

The API translates GuardDuty findings into clear, action-oriented recommendations:

- **Backdoor:EC2** → Isolate instance, investigate network traffic
- **CryptoCurrency:EC2** → EC2 mining cryptocurrency, stop instance
- **UnauthorizedAccess:EC2** → Unauthorized access detected, review security groups
- **UnauthorizedAccess:IAM** → Suspicious login, enable MFA and rotate credentials
- **Recon:IAM** → Account reconnaissance, rotate credentials
- **Stealth:IAM** → CloudTrail disabled, re-enable immediately
- **Exfiltration:S3** → Data exfiltration, review bucket policies

---

### 6. Alert Feed (Unified)

Get aggregated alerts from all sources in a single feed.

**Endpoint:** `POST /api/alerts/feed`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id",
  "regions": ["us-east-1"],
  "feed_type": "daily",
  "alert_types": ["cost_spike", "security_high", "budget_threshold"],
  "severity_min": "medium"
}
```

**Parameters:**
- `feed_type`: `daily` or `realtime` (default: `daily`)
- `alert_types`: Optional filter by alert types:
  - `cost_spike` - High-cost items (>$100/month)
  - `idle_resource` - Unused/idle resources
  - `security_high` - High-severity security issues
  - `budget_threshold` - Budget exceeded
  - `cost_anomaly` - Cost anomalies detected
  - `combined` - Combined cost & security alerts
- `severity_min`: Minimum severity (`low`, `medium`, `high`, `critical`)

**Response:**
```json
{
  "feed_date": "2024-01-15",
  "feed_type": "daily",
  "generated_at": "2024-01-15T12:00:00",
  "summary": {
    "total_alerts": 25,
    "by_type": {
      "cost_spike": 8,
      "idle_resource": 12,
      "security_high": 3,
      "budget_threshold": 2
    },
    "by_severity": {
      "critical": 2,
      "high": 8,
      "medium": 10,
      "low": 5
    },
    "by_service": {
      "EC2": 10,
      "S3": 5,
      "RDS": 4,
      "GuardDuty": 3
    },
    "total_monthly_cost_impact": 1250.50,
    "top_alerts": [...]
  },
  "alerts": [...],
  "recommendations": [
    "💰 Potential savings: $1250.50/month by addressing 8 high-cost items",
    "🔒 Security: 3 high-severity security issues require immediate attention",
    "♻️ Resource optimization: 12 idle/unused resources can be removed"
  ]
}
```

---

### 7. Alert Summary Statistics

Get high-level statistics about alerts without full details.

**Endpoint:** `POST /api/alerts/summary`

**Request:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "external_id": "your-unique-id",
  "regions": ["us-east-1"]
}
```

**Response:**
```json
{
  "total_alerts": 25,
  "by_type": {
    "cost_spike": 8,
    "idle_resource": 12,
    "security_high": 3
  },
  "by_severity": {
    "high": 11,
    "medium": 10,
    "low": 4
  },
  "total_monthly_cost_impact": 1250.50,
  "top_alerts": [...]
}
```

---

### 8. Configure Alert Thresholds

Configure custom thresholds for alert generation.

**Endpoint:** `POST /api/alerts/configure`

**Request:**
```json
{
  "budget_threshold_percentage": 80,
  "cost_spike_threshold": 100,
  "idle_days_threshold": 7
}
```

**Response:**
```json
{
  "message": "Alert thresholds configured",
  "configuration": {
    "budget_threshold_percentage": 80,
    "cost_spike_threshold": 100,
    "idle_days_threshold": 7,
    "configured_at": "2024-01-15T12:00:00"
  }
}
```

**Note:** In the current version, thresholds are stored in memory. For production use, consider persisting to a database.

---

## Mock Data for Testing

When AWS Cost Explorer is not enabled or you don't have active services, the API automatically returns realistic mock data. This allows you to:

1. **Test API integration** without AWS resources
2. **Develop dashboards** with realistic sample data
3. **Demo features** to stakeholders

**Mock data includes:**
- Cost data for 7 AWS services (EC2, S3, Lambda, RDS, CloudFront, API Gateway, DynamoDB)
- Realistic cost trends (daily/weekly/monthly)
- Sample anomalies and budget alerts
- All data clearly marked as "MOCK DATA"

**How to identify mock data:**
```json
{
  "Issue": "Amazon EC2 - monthly cost analysis (MOCK DATA)",
  "Details": {
    "note": "This is mock data for testing purposes"
  }
}
```

---

## Multi-Account Support

All endpoints support multi-account monitoring:

1. **Use organization-wide scans** with the `/api/audit` endpoint
2. **Configure cross-account roles** for GuardDuty and Cost Explorer
3. **Aggregate costs and alerts** across all accounts

**Example:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "organization": true,
  "cross_account_role": "OrganizationAccountAccessRole",
  "regions": ["us-east-1"]
}
```

---

## Tag-Based Filtering

Filter resources by environment tags (prod/staging/dev):

**Supported in comprehensive audit:**
```json
{
  "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
  "regions": ["us-east-1"]
}
```

The system recognizes common tag keys:
- `Environment`, `Env`, `Stage`, `Tier`

Common values:
- `prod`, `production`, `staging`, `stage`, `dev`, `development`, `test`

Configure tag exclusions in `kosty.yaml`:
```yaml
exclude:
  tags:
    - key: Environment
      value: production
```

---

## Complete Usage Example

Here's a complete workflow using the new APIs:

```bash
# 1. Check GuardDuty status
curl -X POST http://localhost:5000/api/guardduty \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345",
    "regions": ["us-east-1"]
  }'

# 2. Get cost analysis
curl -X POST http://localhost:5000/api/costs \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345",
    "period": "MONTHLY"
  }'

# 3. Check for cost anomalies
curl -X POST http://localhost:5000/api/costs/anomalies \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345"
  }'

# 4. Check budget thresholds
curl -X POST http://localhost:5000/api/budgets \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345"
  }'

# 5. Get unified alert feed
curl -X POST http://localhost:5000/api/alerts/feed \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345",
    "regions": ["us-east-1"],
    "feed_type": "daily",
    "severity_min": "medium"
  }'

# 6. Get alert summary only
curl -X POST http://localhost:5000/api/alerts/summary \
  -H "Content-Type: application/json" \
  -d '{
    "user_role_arn": "arn:aws:iam::123456789012:role/KostyAuditRole",
    "external_id": "user-12345",
    "regions": ["us-east-1"]
  }'
```

---

## Error Handling

All endpoints return standard error responses:

**Success:** HTTP 200
```json
{
  "costs": [...],
  "total_services": 7
}
```

**Error:** HTTP 500
```json
{
  "error": "Failed to assume role in user's account: AccessDenied",
  "type": "ClientError"
}
```

**With DEBUG=true:**
```json
{
  "error": "Error message",
  "type": "ExceptionType",
  "traceback": "Detailed stack trace..."
}
```

---

## Required IAM Permissions

For the new features, ensure your IAM role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetAnomalies",
        "ce:GetAnomalyMonitors",
        "budgets:DescribeBudgets",
        "guardduty:ListDetectors",
        "guardduty:GetDetector",
        "guardduty:ListFindings",
        "guardduty:GetFindings"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Integration with Existing Features

The new endpoints integrate seamlessly with existing Kosty features:

1. **Comprehensive Audit** (`/api/audit`) now includes Cost Explorer and GuardDuty
2. **Alert Feed** aggregates findings from all 18 services (16 existing + 2 new)
3. **Multi-account support** works across all new endpoints
4. **Tag filtering** applies to all resource checks

---

## Next Steps

1. **Enable Cost Explorer** in your AWS account (if not already enabled)
2. **Set up AWS Budgets** for threshold monitoring
3. **Enable GuardDuty** for threat detection
4. **Configure Cost Anomaly Detection** for automatic alerts
5. **Test with mock data** before connecting to production AWS

For questions or issues, refer to the main [API Documentation](API_README.md).
