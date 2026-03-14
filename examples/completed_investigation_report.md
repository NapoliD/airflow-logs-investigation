# Airflow Logs Investigation Report

> Investigation of task failure in `etl_sales_daily` DAG on January 15, 2024.

## Environment

| Field | Value |
|-------|-------|
| AWS Account | `123456789012` |
| Region | `us-east-1` |
| Airflow Deployment Type | Amazon MWAA |
| Environment Name | `prod-data-pipeline` |
| Airflow Version | `2.8.1` |
| Investigation Date | 2024-01-15 |
| Investigator | Data Engineering Team |

---

## Incident Summary

| Field | Value |
|-------|-------|
| DAG ID | `etl_sales_daily` |
| Task ID | `extract_data` |
| Run ID | `scheduled__2024-01-15T10:00:00+00:00` |
| First Failure | 2024-01-15 10:00:32 UTC |
| Resolution | 2024-01-15 10:05:55 UTC |
| Total Downtime | ~6 minutes (automatic retry) |

---

## Sources Reviewed

### 1. CloudWatch

| Field | Value |
|-------|-------|
| Status | Found |
| Log Groups | `airflow-prod-data-pipeline-Task` |
| Contains Task Logs | Yes |
| Log Retention | 30 days |
| Sample Stream Path | `etl_sales_daily/extract_data/2024-01-15T10:00:00+00:00/1` |
| Automation Feasibility | High |

**Notes:**

CloudWatch is the primary log source for this MWAA environment. Task logs are automatically shipped to dedicated log groups. Full stack traces and timestamps are preserved.

```
Log Group: airflow-prod-data-pipeline-Task
Streams found: 3
Error events: 2
```

---

### 2. S3

| Field | Value |
|-------|-------|
| Status | Found |
| Bucket(s) | `acme-corp-airflow-prod` |
| Prefix(es) | `logs/` |
| Contains Task Logs | Yes |
| File Structure | `logs/{dag_id}/{task_id}/{run_id}/{attempt}.log` |
| Automation Feasibility | High |

**Notes:**

Remote logging is enabled via `remote_logging=True` in Airflow configuration. Logs are persisted to S3 as backup and for long-term retention.

```
s3://acme-corp-airflow-prod/logs/etl_sales_daily/extract_data/2024-01-15T10:00:00+00:00/
├── 1.log (27 lines - failed attempt)
└── 2.log (12 lines - successful retry)
```

---

### 3. Airflow REST API

| Field | Value |
|-------|-------|
| Status | Enabled |
| Endpoint Base | `https://a1b2c3d4-e5f6-7890-abcd-ef1234567890.c1.us-east-1.airflow.amazonaws.com/api/v1` |
| Auth Method | AWS IAM + Session Token |
| Available Endpoints | `/dags`, `/dagRuns`, `/taskInstances`, `/logs` |
| Useful for Logs | Partial (truncated in API response) |
| Useful for Metadata | Yes |

**Notes:**

REST API provides task instance metadata including state, duration, attempt count, and execution timestamps. Log content via API is useful for quick checks but CloudWatch/S3 are better for full logs.

---

### 4. Local Filesystem

| Field | Value |
|-------|-------|
| Status | Not directly accessible |
| Path | N/A (managed service) |
| Access Method | N/A |
| Contains Task Logs | N/A |
| Log Rotation | N/A |

**Notes:**

MWAA is a managed service. Direct filesystem access is not available. Logs are shipped to CloudWatch and S3 automatically.

---

### 5. UI Scraping

| Field | Value |
|-------|-------|
| Needed | No |
| Reason | CloudWatch and S3 provide programmatic access |
| Complexity | N/A |
| Stability Risk | N/A |

**Notes:**

UI scraping is not required. CloudWatch Logs API and S3 GetObject provide stable, automatable access to all task logs.

---

## Airflow Configuration

### Logging Settings Found

```ini
base_log_folder = /usr/local/airflow/logs
remote_logging = True
remote_base_log_folder = s3://acme-corp-airflow-prod/logs
remote_log_conn_id = aws_default
logging_config_class = (MWAA default)
```

### Source of Configuration

- [x] MWAA UI Configuration
- [x] Environment variables (via MWAA)
- [ ] airflow.cfg (not directly editable in MWAA)
- [ ] Helm values

---

## IAM Permissions

### Current Access

| Resource | Permission | Status |
|----------|------------|--------|
| CloudWatch Logs | `logs:GetLogEvents` | OK |
| CloudWatch Logs | `logs:DescribeLogGroups` | OK |
| CloudWatch Logs | `logs:FilterLogEvents` | OK |
| S3 | `s3:GetObject` | OK |
| S3 | `s3:ListBucket` | OK |
| MWAA | `airflow:GetEnvironment` | OK |
| MWAA | `airflow:CreateWebLoginToken` | OK |

### Permissions Needed

None. All required permissions are available.

---

## Root Cause Analysis

### Error Details

```
psycopg2.OperationalError: connection timed out
server closed the connection unexpectedly
This probably means the server terminated abnormally
before or while processing the request.
```

### Timeline

| Time (UTC) | Event |
|------------|-------|
| 10:00:00 | Task `extract_data` started (attempt 1/2) |
| 10:00:01 | Connecting to database `salesdb.acme-corp.internal:5432` |
| 10:00:02 | Query execution started |
| 10:00:32 | Connection timeout after 30 seconds |
| 10:00:33 | Task marked as FAILED |
| 10:00:45 | Retry scheduled (5 minute delay) |
| 10:05:00 | Task `extract_data` started (attempt 2/2) |
| 10:05:03 | Connection established successfully |
| 10:05:45 | Query completed (15,234 rows) |
| 10:05:55 | Task marked as SUCCESS |
| 10:06:40 | Downstream task `load_to_warehouse` started |
| 10:07:50 | DAG run completed successfully |

### Root Cause

**Transient database connection timeout** - The source database (`salesdb.acme-corp.internal`) experienced a temporary connectivity issue during the first attempt. This could be caused by:

1. Network latency spike
2. Database connection pool exhaustion
3. Temporary DNS resolution delay
4. Database server load spike

### Why It Resolved

The Airflow task is configured with `retries=1` and `retry_delay=300s`. After the 5-minute wait, the second attempt connected successfully, suggesting the issue was transient.

---

## Test Results

### Sample Task Log Retrieved

| Source | Success | Log Quality | Automation Ready |
|--------|---------|-------------|------------------|
| CloudWatch | Yes | Full | Yes |
| S3 | Yes | Full | Yes |
| API | Yes | Truncated | Partial |
| Filesystem | N/A | N/A | N/A |
| UI | Not tested | N/A | No |

---

## Final Recommendation

### Primary Source

| Field | Value |
|-------|-------|
| Source | CloudWatch Logs |
| Access Method | `boto3` / `aws logs get-log-events` |
| Justification | Native integration with MWAA, real-time streaming, Logs Insights queries |

### Secondary Source

| Field | Value |
|-------|-------|
| Source | S3 |
| Access Method | `boto3` / `aws s3 cp` |
| Justification | Long-term retention, batch processing, cost-effective storage |

### Fallback

| Field | Value |
|-------|-------|
| Source | REST API |
| Access Method | HTTP requests with IAM auth |
| When to Use | Quick status checks, metadata retrieval, when CloudWatch/S3 unavailable |

---

## Action Items

- [x] Verify CloudWatch log access
- [x] Verify S3 log access
- [x] Document logging configuration
- [x] Identify root cause of failure
- [ ] Add CloudWatch alarm for repeated connection timeouts
- [ ] Review database connection pool settings
- [ ] Consider increasing query timeout for large datasets

---

## Conclusion

The investigation confirmed that:

1. **MWAA logging is properly configured** - Both CloudWatch and S3 receive task logs
2. **The failure was transient** - Database connection timeout resolved on retry
3. **No scraping required** - Programmatic access via CloudWatch/S3 is stable and sufficient
4. **Automation is viable** - Python scripts using boto3 can reliably retrieve logs

**Recommended automation approach:** Use CloudWatch Logs as primary source with S3 as backup for historical analysis.

---

## Appendix

### A. Relevant ARNs

```
arn:aws:airflow:us-east-1:123456789012:environment/prod-data-pipeline
arn:aws:logs:us-east-1:123456789012:log-group:airflow-prod-data-pipeline-Task
arn:aws:s3:::acme-corp-airflow-prod
```

### B. Code Snippets

```python
# Retrieve CloudWatch logs
import boto3

client = boto3.client('logs', region_name='us-east-1')

response = client.get_log_events(
    logGroupName='airflow-prod-data-pipeline-Task',
    logStreamName='etl_sales_daily/extract_data/2024-01-15T10:00:00+00:00/1',
    startFromHead=True
)

for event in response['events']:
    print(event['message'])
```

### C. Additional Notes

This investigation used the methodology from the [Airflow Logs Investigation Guide](../docs/investigate_airflow_logs.md). The checklist was completed in approximately 45 minutes.
