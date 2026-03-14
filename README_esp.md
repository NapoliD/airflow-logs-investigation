# Airflow Logs Investigation Guide - AWS

Guía paso a paso para investigar dónde están los logs de Apache Airflow en entornos AWS y definir la mejor fuente para proyectos de automatización.

## Objetivo

Esta guía te ayuda a determinar:

- **Fuente real de logs** - Dónde se almacenan los task logs
- **Método de acceso** - Cómo recuperarlos programáticamente
- **Viabilidad para automatización** - Si la fuente es estable y automatizable
- **Necesidad de scraping** - Si se requiere scraping de UI o hay alternativas mejores

## Estructura del Repositorio

```
.
├── README.md                           # Este archivo
├── docs/
│   └── investigate_airflow_logs.md     # Guía completa paso a paso
├── templates/
│   └── investigation_report.md         # Plantilla para documentar hallazgos
└── checklists/
    └── airflow_logs_checklist.md       # Checklist ejecutable
```

## Inicio Rápido

1. Lee la [guía completa](docs/investigate_airflow_logs.md)
2. Usa el [checklist](checklists/airflow_logs_checklist.md) durante tu investigación
3. Documenta tus hallazgos con la [plantilla](templates/investigation_report.md)

## Prioridad de Fuentes Recomendada

| Prioridad | Fuente | Cuándo Usarla |
|-----------|--------|---------------|
| 1 | CloudWatch | MWAA o runtime que publica logs ahí |
| 2 | S3 | `remote_logging=True` configurado a `s3://...` |
| 3 | REST API | Para metadata, estados y orquestación |
| 4 | Filesystem | Acceso directo a host/contenedor |
| 5 | UI Scraping | Solo como fallback |

## Tipos de Despliegue AWS

- **Amazon MWAA** - Servicio gestionado, logs en CloudWatch
- **EKS** - Kubernetes, revisar pods y shipping de logs
- **ECS** - Containers, revisar task definitions
- **EC2** - VMs, revisar filesystem y agentes

## Referencias Oficiales

- [AWS MWAA - Accessing Airflow logs](https://docs.aws.amazon.com/mwaa/latest/userguide/monitoring-airflow.html)
- [Airflow - Writing logs to S3](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/logging/s3-task-handler.html)
- [Airflow - Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html)
- [AWS MWAA - REST API](https://docs.aws.amazon.com/mwaa/latest/userguide/access-mwaa-apache-airflow-rest-api.html)

## Licencia

MIT
