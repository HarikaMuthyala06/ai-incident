import logging
from app.core.database import get_db_collection
from app.services.rag_pipeline import ManualRAGPipeline

logger = logging.getLogger("incident_agent.seed")

DEFAULT_RUNBOOKS = [
    {
        "title": "PostgreSQL & Database Connection Pool Troubleshooting Runbook",
        "category": "Database",
        "source_filename": "runbook_db_connection_pool.md",
        "content": """# Database Connection Pool Exhaustion Runbook

### Symptoms
- Application logs show: `timeout: connection pool exhausted`, `psycopg2.OperationalError: server closed the connection unexpectedly`, or `500 Internal Server Error` on data-access endpoints.
- Database metrics reveal active connections reaching `max_connections` limit.
- Database CPU spikes to 100% or transaction lock wait time increases exponentially.

### Diagnostic Steps
1. Verify active connection count: `SELECT count(*), state FROM pg_stat_activity GROUP BY state;`.
2. Check for long-running blocking queries or deadlocks: `SELECT pid, query, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE state != 'idle' ORDER BY age DESC;`.
3. Check application connection pool configuration (`max_overflow`, `pool_size`, `pool_timeout`).
4. Inspect recent deployments for unclosed database sessions (missing `try...finally session.close()` or missing ORM context managers).

### Mitigation & Resolution
1. Temporary mitigation: Terminate idle or blocking backend connections: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND query_start < NOW() - INTERVAL '5 minutes';`.
2. Increase PgBouncer or connection pool limit temporarily if DB memory permits.
3. Permanent fix: Fix connection leaks in the application code, enforce connection timeouts (e.g. `statement_timeout = 5000ms`), and configure connection pool pooling with PgBouncer.
"""
    },
    {
        "title": "Payment API Gateway & Third-Party HTTP 500/504 Failure Runbook",
        "category": "API",
        "source_filename": "runbook_payment_api_timeouts.md",
        "content": """# Payment API & Third-Party Service Failure Runbook

### Symptoms
- Payment checkout endpoints return `502 Bad Gateway`, `503 Service Unavailable`, or `504 Gateway Timeout`.
- Worker queues backlog with pending checkout orders.
- Error logs: `requests.exceptions.ReadTimeout`, `GatewayTimeoutException: upstream connection timed out after 30000ms`.

### Diagnostic Steps
1. Determine if the failure originates internally or at the upstream payment provider (e.g., Stripe, PayPal, Razorpay).
2. Check payment gateway status page and latency metrics.
3. Check DNS resolution and outbound firewall/NAT gateway throughput on application nodes.
4. Verify if recent deployments altered the API timeout configuration or updated the payment SDK library.

### Mitigation & Resolution
1. Enable exponential backoff and circuit breaking: trip the circuit breaker after 5 consecutive failures to prevent cascading thread pool starvation.
2. Route transactions to secondary/fallback payment gateway if multi-gateway failover is enabled.
3. Increase idempotent client retries with jitter for transient 504 timeouts.
4. Notify customers via status banner if upstream processor is facing global downtime.
"""
    },
    {
        "title": "JWT Validation, Token Expiry, and Auth Service Outage Runbook",
        "category": "Authentication",
        "source_filename": "runbook_auth_jwt_failures.md",
        "content": """# Authentication & JWT Validation Failure Runbook

### Symptoms
- Massive surge in `401 Unauthorized` or `403 Forbidden` responses across mobile and web clients.
- Users forcibly logged out and unable to log back in.
- Error logs: `jwt.exceptions.InvalidSignatureError`, `JWKSetFetchError: Unable to fetch public keys from identity provider`, or `TokenExpiredError`.

### Diagnostic Steps
1. Verify if JSON Web Key Set (JWKS) endpoint is reachable by downstream services.
2. Check clock skew: verify NTP synchronization across backend servers (`chronyd` or `ntpd`). Clock drift > 60 seconds causes immediate token rejection.
3. Check if secrets or private signing keys were rotated recently without maintaining previous public keys in the JWKS rotation buffer.
4. Verify environment variables (`JWT_SECRET`, `AUTH_SERVICE_URL`, `TOKEN_AUDIENCE`).

### Mitigation & Resolution
1. If key rotation was performed abruptly, temporarily restore previous public verification key to JWKS whitelist.
2. If clock drift is detected, resync system clocks via NTP.
3. If identity provider is degraded, configure cached JWKS keys with fallback grace period.
"""
    },
    {
        "title": "Application Deployment & Container CrashLoopBackOff Runbook",
        "category": "Deployment",
        "source_filename": "runbook_deployment_crashloop.md",
        "content": """# Container Deployment & Startup Failure Runbook

### Symptoms
- New release deployed to production; Kubernetes pods enter `CrashLoopBackOff` or `Error`.
- Health checks (`/healthz` or `/livez`) fail continuously.
- Error logs: `KeyError: 'DATABASE_PASSWORD' missing environment variable`, `ModuleNotFoundError`, or `Exit Code 137 (OOMKilled)`.

### Diagnostic Steps
1. Inspect container logs: `kubectl logs <pod-name> --previous`.
2. Inspect pod event history: `kubectl describe pod <pod-name>` looking for OOMKilled or failed probes.
3. Compare environment variables between staging and production secrets.
4. Verify database migration scripts ran and schema migrations succeeded prior to container boot.

### Mitigation & Resolution
1. Immediately roll back deployment: `kubectl rollout undo deployment/<service-name>`.
2. If due to missing environment variable, patch the Secret/ConfigMap and re-trigger deployment.
3. If due to OOMKilled (Exit Code 137), increase container memory limit in pod deployment spec.
"""
    },
    {
        "title": "High Traffic & Missing Index Database Latency Runbook",
        "category": "Performance",
        "source_filename": "runbook_database_index_performance.md",
        "content": """# High Traffic Latency & Missing Index Troubleshooting

### Symptoms
- Sudden spike in p99 and p95 API response times (from 80ms to 4500ms).
- Database CPU reaches 95-100% during peak events (e.g. ticket booking, flash sales, student portal exam result release).
- Application thread pool exhaustion due to slow query execution.

### Diagnostic Steps
1. Identify top slow queries using `pg_stat_statements` or MySQL slow query log: queries with high `total_exec_time` and high `calls`.
2. Run `EXPLAIN ANALYZE` on the offending query to check for `Seq Scan` (Sequential Table Scan) instead of `Index Scan`.
3. Check table row count and memory cache hit ratio (`SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) FROM pg_statio_user_tables;`).

### Mitigation & Resolution
1. Create missing composite index concurrently: `CREATE INDEX CONCURRENTLY idx_student_hallticket ON exam_records(student_id, semester_id);`.
2. Enable Redis or CDN read caching for read-heavy static result payloads with short TTL (e.g. 60 seconds).
3. Implement traffic rate-limiting or queuing (virtual waiting room) to smooth traffic peaks.
"""
    },
    {
        "title": "Message Queue Congestion & Worker Starvation Runbook",
        "category": "Microservice",
        "source_filename": "runbook_queue_worker_backlog.md",
        "content": """# Message Queue & Async Worker Starvation Runbook

### Symptoms
- Messages stuck in 'pending' or 'sending' status for minutes or hours.
- RabbitMQ / Kafka / Redis Celery queue length grows continuously.
- End users report delayed push notifications, unsent emails, or background order processing stalls.

### Diagnostic Steps
1. Check queue backlog depth and unacknowledged message count.
2. Check worker consumer health: are Celery / Kafka worker processes alive and consuming messages?
3. Look for poison-pill messages (unhandled exception causing consumer process to crash repeatedly without acknowledging message).
4. Check downstream API rate limits that the worker depends on.

### Mitigation & Resolution
1. Route unparseable poison-pill messages to a Dead Letter Queue (DLQ) after 3 failed retries.
2. Scale up worker replica pods horizontally to process the queue backlog.
3. Check worker resource limits (CPU/Memory throttling).
"""
    }
]

async def seed_default_knowledge_base():
    """Seed default runbooks if collection is empty."""
    docs_col = get_db_collection("knowledge_documents")
    count = await docs_col.count_documents({})
    if count == 0:
        logger.info("Seeding default SRE troubleshooting runbooks into knowledge base...")
        for book in DEFAULT_RUNBOOKS:
            await ManualRAGPipeline.index_document(
                title=book["title"],
                category=book["category"],
                content=book["content"],
                source_filename=book["source_filename"]
            )
        logger.info(f"Successfully seeded {len(DEFAULT_RUNBOOKS)} technical troubleshooting runbooks!")
