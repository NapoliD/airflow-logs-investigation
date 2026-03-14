# Checklist: Investigación de Logs de Airflow en AWS

> Usá este checklist durante tu investigación. Marcá cada item al completarlo.

## Fase 1: Identificación del Entorno

- [ ] Identificar si Airflow corre en **MWAA**
- [ ] Identificar si Airflow corre en **ECS**
- [ ] Identificar si Airflow corre en **EKS**
- [ ] Identificar si Airflow corre en **EC2**
- [ ] Anotar: región, cuenta AWS, nombre del entorno
- [ ] Confirmar acceso al entorno

## Fase 2: MWAA (si aplica)

- [ ] Acceder a MWAA en consola AWS
- [ ] Revisar nombre del environment
- [ ] Revisar versión de Airflow
- [ ] Revisar bucket S3 asociado
- [ ] Revisar **logging configuration**
- [ ] Identificar qué tipos de log están habilitados:
  - [ ] Task
  - [ ] Scheduler
  - [ ] Worker
  - [ ] WebServer
  - [ ] DAGProcessing

## Fase 3: CloudWatch Logs

- [ ] Acceder a CloudWatch → Log groups
- [ ] Buscar log groups relacionados con Airflow
- [ ] Identificar log groups de Task logs
- [ ] Validar que hay logs recientes
- [ ] Verificar que aparece `dag_id`, `task_id`, `run_id`
- [ ] Verificar que contiene stacktrace útil
- [ ] Anotar retención de logs
- [ ] Confirmar permisos de lectura

## Fase 4: S3 Logging

- [ ] Revisar si existe `remote_logging` configurado
- [ ] Identificar bucket y prefix de logs
- [ ] Buscar prefijos típicos: `airflow-logs/`, `logs/`, `mwaa/`
- [ ] Validar estructura de carpetas por DAG/task
- [ ] Verificar contenido de archivos de log
- [ ] Anotar antigüedad y tamaño de archivos

## Fase 5: Configuración de Airflow

- [ ] Obtener acceso a configuración (airflow.cfg / env vars)
- [ ] Revisar `base_log_folder`
- [ ] Revisar `remote_logging`
- [ ] Revisar `remote_base_log_folder`
- [ ] Revisar `remote_log_conn_id`
- [ ] Revisar `logging_config_class`
- [ ] Documentar valores encontrados

## Fase 6: REST API

- [ ] Verificar si REST API está habilitada
- [ ] Identificar endpoint base
- [ ] Identificar método de autenticación
- [ ] Probar acceso a endpoints de DAG runs
- [ ] Probar acceso a endpoints de task instances
- [ ] Evaluar si sirve para logs o solo metadata

## Fase 7: Permisos IAM

- [ ] Verificar acceso a CloudWatch Logs
- [ ] Verificar acceso a S3 (si aplica)
- [ ] Verificar acceso a MWAA details
- [ ] Verificar acceso a InvokeRestApi (si aplica)
- [ ] Documentar permisos faltantes
- [ ] Solicitar permisos necesarios

## Fase 8: Runtime Alternativo (si no es MWAA)

### EKS
- [ ] Identificar namespace de Airflow
- [ ] Revisar pods y sidecars
- [ ] Verificar shipping de logs

### ECS
- [ ] Revisar task definitions
- [ ] Verificar configuración de awslogs driver

### EC2
- [ ] Identificar instancias
- [ ] Revisar filesystem local
- [ ] Verificar agentes de logging

## Fase 9: Filesystem Local (si hay acceso)

- [ ] Acceder a host/contenedor
- [ ] Ubicar `$AIRFLOW_HOME/logs/`
- [ ] Verificar estructura por dag_id/task_id
- [ ] Verificar archivos por intento
- [ ] Validar contenido con traceback completo

## Fase 10: Inspección de UI

- [ ] Abrir un task fallido en UI
- [ ] Observar si log carga rápido o lento
- [ ] Verificar si muestra texto directo
- [ ] Buscar links externos a otras fuentes
- [ ] Buscar hints del origen del log
- [ ] Evaluar si scraping es necesario

## Fase 11: Pruebas de Acceso

- [ ] Recuperar 1 log real desde **CloudWatch**
- [ ] Recuperar 1 log real desde **S3** (si aplica)
- [ ] Recuperar 1 log real desde **API** (si aplica)
- [ ] Recuperar 1 log real desde **filesystem** (si aplica)
- [ ] Comparar calidad y completitud

## Fase 12: Documentación

- [ ] Completar template de investigation report
- [ ] Definir fuente primaria
- [ ] Definir fuente secundaria
- [ ] Definir fallback
- [ ] Documentar action items pendientes
- [ ] Compartir hallazgos con el equipo

---

## Resultado Final

| Decisión | Valor |
|----------|-------|
| Fuente primaria | |
| Fuente secundaria | |
| Fallback | |
| Scraping necesario | Sí / No |
| Permisos pendientes | |

---

## Notas

```
[Agregar notas durante la investigación]
```
