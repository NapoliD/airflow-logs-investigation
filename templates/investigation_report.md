# Airflow Logs Investigation Report

> Completar este template durante la investigación de logs de Airflow.

## Environment

| Campo | Valor |
|-------|-------|
| AWS Account | |
| Region | |
| Airflow Deployment Type | MWAA / EKS / ECS / EC2 / Otro |
| Environment Name | |
| Airflow Version | |
| Investigation Date | |
| Investigator | |

---

## Sources Reviewed

### 1. CloudWatch

| Campo | Valor |
|-------|-------|
| Status | Encontrado / No encontrado / Sin acceso |
| Log Groups | |
| Contains Task Logs | Sí / No / Parcial |
| Log Retention | |
| Sample Stream Path | |
| Automation Feasibility | Alta / Media / Baja |

**Notas:**

```
[Agregar observaciones]
```

---

### 2. S3

| Campo | Valor |
|-------|-------|
| Status | Encontrado / No encontrado / Sin acceso |
| Bucket(s) | |
| Prefix(es) | |
| Contains Task Logs | Sí / No / Parcial |
| File Structure | |
| Automation Feasibility | Alta / Media / Baja |

**Notas:**

```
[Agregar observaciones]
```

---

### 3. Airflow REST API

| Campo | Valor |
|-------|-------|
| Status | Habilitada / Deshabilitada / Sin acceso |
| Endpoint Base | |
| Auth Method | |
| Available Endpoints | |
| Useful for Logs | Sí / No / Parcial |
| Useful for Metadata | Sí / No / Parcial |

**Notas:**

```
[Agregar observaciones]
```

---

### 4. Local Filesystem

| Campo | Valor |
|-------|-------|
| Status | Accesible / No accesible |
| Path | |
| Access Method | SSH / kubectl exec / Otro |
| Contains Task Logs | Sí / No |
| Log Rotation | |

**Notas:**

```
[Agregar observaciones]
```

---

### 5. UI Scraping

| Campo | Valor |
|-------|-------|
| Needed | Sí / No |
| Reason | |
| Complexity | Alta / Media / Baja |
| Stability Risk | Alto / Medio / Bajo |

**Notas:**

```
[Agregar observaciones]
```

---

## Airflow Configuration

### Logging Settings Found

```ini
base_log_folder =
remote_logging =
remote_base_log_folder =
remote_log_conn_id =
logging_config_class =
```

### Source of Configuration

- [ ] airflow.cfg
- [ ] Environment variables
- [ ] MWAA UI Configuration
- [ ] Helm values
- [ ] Other: _______________

---

## IAM Permissions

### Current Access

| Resource | Permission | Status |
|----------|------------|--------|
| CloudWatch Logs | `logs:GetLogEvents` | OK / Denied / N/A |
| CloudWatch Logs | `logs:DescribeLogGroups` | OK / Denied / N/A |
| S3 | `s3:GetObject` | OK / Denied / N/A |
| S3 | `s3:ListBucket` | OK / Denied / N/A |
| MWAA | `airflow:GetEnvironment` | OK / Denied / N/A |
| MWAA | `airflow:InvokeRestApi` | OK / Denied / N/A |

### Permissions Needed

```
[Listar permisos que faltan solicitar]
```

---

## Test Results

### Sample Task Log Retrieved

| Source | Success | Log Quality | Automation Ready |
|--------|---------|-------------|------------------|
| CloudWatch | | | |
| S3 | | | |
| API | | | |
| Filesystem | | | |
| UI | | | |

### Sample Log Content

```
[Pegar ejemplo de log recuperado - redactar info sensible]
```

---

## Final Recommendation

### Primary Source

| Campo | Valor |
|-------|-------|
| Source | |
| Access Method | |
| Justification | |

### Secondary Source

| Campo | Valor |
|-------|-------|
| Source | |
| Access Method | |
| Justification | |

### Fallback

| Campo | Valor |
|-------|-------|
| Source | |
| Access Method | |
| When to Use | |

---

## Action Items

- [ ]
- [ ]
- [ ]

---

## Appendix

### A. Relevant ARNs

```
[Listar ARNs de recursos relevantes]
```

### B. Code Snippets

```python
# Ejemplo de acceso a logs
```

### C. Additional Notes

```
[Notas adicionales]
```
