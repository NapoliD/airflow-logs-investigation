# Guía Completa: Investigar Logs de Airflow en AWS

Esta guía te lleva paso a paso para identificar dónde están los logs de Airflow en tu entorno AWS y elegir la mejor fuente para automatización.

## Paso 0: Definir Qué Buscás

Antes de tocar AWS, dejá claro qué necesitás:

1. **Task logs completos** - El output de cada task
2. **Errores y stacktrace** - Para diagnóstico de fallos
3. **Metadata de ejecución** - `dag_id`, `task_id`, `run_id`, estado, intento
4. **Una fuente estable y automatizable** - No depender de UI

Tu fuente ideal es donde tengas el **texto crudo del log** + contexto del task run.

---

## Paso 1: Identificar el Tipo de Despliegue

Primero necesitás saber **dónde corre Airflow**. Las opciones en AWS son:

- **Amazon MWAA** (Managed Workflows for Apache Airflow)
- **EKS** (Elastic Kubernetes Service)
- **ECS** (Elastic Container Service)
- **EC2** (instancias directas)
- Entornos mixtos

### Cómo Investigar

En la consola AWS, buscá:

- **MWAA** - Buscar "MWAA" o "Managed Workflows"
- **ECS clusters** - Buscar clusters con nombre "airflow"
- **EKS clusters** - Revisar namespaces con workloads Airflow
- **EC2 instances** - Buscar tags con "airflow"

### Qué Anotar

| Campo | Valor |
|-------|-------|
| Servicio | |
| Nombre del entorno | |
| Región | |
| Cuenta AWS | |
| Equipo responsable | |
| Acceso disponible | Sí / No |

### Decisión

- Si encontrás **MWAA** → seguí por CloudWatch + MWAA config
- Si no es MWAA → revisá CloudWatch, S3, filesystem según el runtime

---

## Paso 2: Revisar Entorno MWAA

Si usan **Amazon MWAA**, este es el camino más directo.

### En Consola

`AWS Console → Amazon MWAA → Environments`

### Qué Revisar

- Nombre del environment
- Versión de Airflow
- Bucket S3 asociado
- Execution role
- **Logging configuration** ← Clave

MWAA crea log groups separados en CloudWatch por tipo:
- `NombreEntorno-Task`
- `NombreEntorno-Scheduler`
- `NombreEntorno-Worker`
- `NombreEntorno-WebServer`
- `NombreEntorno-DAGProcessing`

### Resultado

Si ves logs habilitados → **CloudWatch es tu candidato principal**.

---

## Paso 3: Revisar CloudWatch Logs

### En Consola

`AWS Console → CloudWatch → Logs → Log groups`

### Qué Buscar

Probá búsquedas por:
- Nombre del environment
- `airflow`
- `mwaa`
- `task`
- `scheduler`
- `worker`

### Qué Validar

Abrí el log group y verificá:

- [ ] Hay logs recientes
- [ ] Aparecen `dag_id`, `task_id`, `run_id`
- [ ] Contiene stacktrace útil
- [ ] Sirve para diagnóstico automático

### Qué Anotar

| Log Group | Retención | Tiene Task Logs | Permisos OK |
|-----------|-----------|-----------------|-------------|
| | | Sí/No | Sí/No |

### Criterio de Éxito

Si podés recuperar: mensaje de error, traceback, nombre de DAG/task, timestamp → **ya no necesitás scrapear UI**.

---

## Paso 4: Revisar Logging Remoto a S3

Airflow soporta logging remoto con `remote_logging=True` y `remote_base_log_folder=s3://...`.

### Dónde Buscar

#### A. Configuración de Airflow

Buscá en:
- `airflow.cfg`
- Variables de entorno
- Configuración del environment MWAA

Claves importantes:
```ini
base_log_folder = /path/to/local/logs
remote_logging = True
remote_base_log_folder = s3://bucket/prefix
remote_log_conn_id = aws_default
logging_config_class = airflow.config_templates.airflow_local_settings.DEFAULT_LOGGING_CONFIG
```

#### B. Bucket S3 Asociado

Si usan MWAA, cada environment tiene un bucket S3 para DAGs.
Revisá si también tiene logs.

#### C. Buscar Buckets Obvios

Prefijos típicos:
- `airflow-logs/`
- `logs/`
- `mwaa/`
- `task-logs/`

### Qué Validar

- Estructura por DAG/task/run
- Contenido con log de ejecución real
- Tamaño y antigüedad de archivos

---

## Paso 5: Revisar Configuración de Airflow

Este paso es clave porque revela **la verdad de la instalación**.

### Qué Conseguir

- `airflow.cfg`
- Environment variables del deployment
- Helm values (si es Kubernetes)
- Configuración del container
- Airflow Configurations en MWAA UI

### Parámetros a Inspeccionar

```
base_log_folder
remote_logging
remote_base_log_folder
remote_log_conn_id
logging_config_class
```

### Cómo Interpretar

| Configuración | Significado |
|---------------|-------------|
| `remote_logging=False` | Logs locales o enviados por otro mecanismo |
| `remote_logging=True` + `s3://...` | Logs en S3 |
| `remote_logging=True` + otro | Otro backend remoto |

---

## Paso 6: Revisar REST API de Airflow

En MWAA, la REST API permite acceso programático sin depender de UI.

### Qué Investigar

- [ ] REST API habilitada
- [ ] Método de autenticación
- [ ] Endpoints disponibles
- [ ] Si permite obtener: DAG runs, task instances, estados, logs

### Por Qué Importa

La API puede darte:
- Lista de runs fallidos
- Estado de cada task
- Contexto del task instance

### Qué Anotar

| Campo | Valor |
|-------|-------|
| Endpoint base | |
| Auth method | |
| Endpoints útiles | |
| Log retrieval | Suficiente / Parcial / No |

---

## Paso 7: Revisar IAM y Permisos

Muchas veces los logs existen pero no los ves por falta de permisos.

### Permisos Necesarios

- **CloudWatch Logs**: `logs:GetLogEvents`, `logs:DescribeLogGroups`
- **S3**: `s3:GetObject`, `s3:ListBucket`
- **MWAA**: `airflow:GetEnvironment`, `airflow:InvokeRestApi`

### Cómo Verificar

Si ves "Access denied", anotá:
- Servicio
- Acción bloqueada
- Recurso
- Qué permiso falta

---

## Paso 8: Si No es MWAA

Si Airflow no corre en MWAA, ubicá el runtime:

### EKS
- Revisar pods y sidecars
- Verificar shipping de logs a CloudWatch

### ECS
- Revisar task definitions
- Verificar `awslogs` driver

### EC2
- Revisar filesystem local
- Verificar agentes (CloudWatch Agent, Fluentd, etc.)

### Foco

No importa todo el logging del sistema. Importa encontrar el **task execution log**.

---

## Paso 9: Revisar Filesystem Local

Si tenés acceso al host o contenedor:

```bash
# Ubicación por defecto
$AIRFLOW_HOME/logs/

# O el valor de base_log_folder en airflow.cfg
```

### Estructura Típica

```
logs/
├── dag_id_1/
│   ├── task_id_1/
│   │   ├── 2024-01-15T10:00:00+00:00/
│   │   │   ├── 1.log
│   │   │   └── 2.log  # segundo intento
│   │   └── ...
```

### Qué Validar

- [ ] Estructura por dag_id/task_id/run_id
- [ ] Archivos por intento
- [ ] Traceback completo en contenido

---

## Paso 10: Inspeccionar UI (Sin Scrapear)

Antes de implementar scraping, usá la UI solo para inspección.

### Qué Mirar en un Task Fallido

- [ ] Log carga rápido o lento
- [ ] Muestra texto directo o link externo
- [ ] Menciona CloudWatch / S3 / external log
- [ ] Hay hints del origen del log

### Qué Te Dice

- Si la UI renderiza algo que viene de otro backend
- Si hay "link out" a una fuente real
- Si el scraping sería innecesario

---

## Paso 11: Pruebas de Acceso

Validá recuperando **un caso real** de task fallido desde cada fuente:

### Para Cada Fuente

| Fuente | Accedo | Logs Completos | Automatizable | Estable | Contexto |
|--------|--------|----------------|---------------|---------|----------|
| CloudWatch | | | | | |
| S3 | | | | | |
| API | | | | | |
| Filesystem | | | | | |
| UI | | | | | |

### Regla Práctica

Elegí la fuente con mejor combinación de:
- Estabilidad
- Automatización
- Riqueza del log
- Menor dependencia de UI

---

## Paso 12: Documentar Hallazgos

Usá la [plantilla de reporte](../templates/investigation_report.md) para documentar.

---

## Orden de Prioridad Recomendado

1. **CloudWatch** - Si MWAA o runtime publica logs ahí
2. **S3** - Si `remote_logging=True` con `s3://...`
3. **REST API** - Para metadata y orquestación
4. **Filesystem** - Si hay acceso directo
5. **UI Scraping** - Solo como fallback

---

## Referencias

- [AWS - Accessing Airflow logs in CloudWatch](https://docs.aws.amazon.com/mwaa/latest/userguide/monitoring-airflow.html)
- [Airflow - Writing logs to S3](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/logging/s3-task-handler.html)
- [Airflow - Configuration Reference](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html)
- [AWS - What is MWAA](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html)
- [AWS - Using Apache Airflow REST API](https://docs.aws.amazon.com/mwaa/latest/userguide/access-mwaa-apache-airflow-rest-api.html)
- [AWS - MWAA Execution Role](https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-create-role.html)
- [Airflow - Logging for Tasks](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/logging-tasks.html)
