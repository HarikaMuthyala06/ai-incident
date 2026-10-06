from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()

class SimulationRequest(BaseModel):
    application: str  # E-commerce, Ride Booking, College Portal, Banking, Chat Application, Delivery Application
    incident_type: str  # Database Failure, API Failure, Authentication Failure, Performance Issue, Deployment Failure, Microservice Failure

class SimulatedScenario(BaseModel):
    title: str
    application: str
    incident_type: str
    severity: str
    description: str
    logs: str
    error_messages: str
    recent_deployment: str
    metrics: str
    configuration_changes: str

# 6 Applications x 6 Incident Scenarios Knowledge Bank
SIMULATION_MATRIX = {
    # 1. E-COMMERCE
    ("E-commerce", "Database Failure"): {
        "title": "Checkout DB Connection Pool Exhaustion during Flash Sale",
        "severity": "Critical",
        "description": "During peak checkout traffic, users are unable to complete payment. Orders table queries are timing out, and customer carts are failing to checkout.",
        "logs": """2026-10-05 10:14:02 [checkout-service] WARN: Database connection pool utilization at 98% (98/100 active).
2026-10-05 10:14:15 [checkout-service] ERROR: Timeout waiting for database connection from pool after 10000ms.
2026-10-05 10:14:22 [checkout-service] ERROR: sqlalchemy.exc.TimeoutError: QueuePool limit of size 50 overflow 50 reached, connection timed out, timeout 10.00
2026-10-05 10:15:00 [payment-worker] FATAL: Failed to acquire database transaction lock for order_id=ORD-99824.""",
        "error_messages": "sqlalchemy.exc.TimeoutError: QueuePool limit reached. Connection pool exhausted after 10000ms. Server closed connection.",
        "recent_deployment": "Commit a7f21e0: 'Feature: Add loyalty points calculation during order placement' deployed 25 minutes ago.",
        "metrics": "PostgreSQL Active Connections: 100/100. Connection wait time: 14,200ms. Database CPU: 96%. API 5xx rate: 42%.",
        "configuration_changes": "POOL_SIZE was maintained at 50 with max_overflow=50; statement_timeout disabled."
    },
    ("E-commerce", "API Failure"): {
        "title": "Payment Gateway API Returning Cascading 500 & 504 Timeouts",
        "severity": "Critical",
        "description": "Payment API starts returning 500 errors. Customers cannot charge credit cards; transactions fail at the gateway processing step.",
        "logs": """2026-10-05 11:20:01 [payment-api] INFO: Forwarding charge request to Stripe Gateway v3 endpoint...
2026-10-05 11:20:31 [payment-api] ERROR: requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out. (read timeout=30.0)
2026-10-05 11:20:32 [payment-api] ERROR: HTTP 504 Gateway Timeout returned to checkout client.
2026-10-05 11:21:05 [payment-api] WARN: Circuit breaker 'stripe_gateway' status: HALF_OPEN, failure rate: 82%.""",
        "error_messages": "GatewayTimeoutException: Upstream payment processor did not respond within 30000ms. HTTP 504 returned.",
        "recent_deployment": "Release v2.14.0: 'Updated payment client headers and idempotency key algorithm' deployed 40 minutes ago.",
        "metrics": "Payment API error rate: 64% 5xx responses. p99 latency: 31,400ms. Upstream connection dropped count: 184.",
        "configuration_changes": "Timeout setting changed from 5000ms to 30000ms without enabling circuit-breaker shedding."
    },
    ("E-commerce", "Authentication Failure"): {
        "title": "Customer Checkout Session Expired & Login Loop",
        "severity": "High",
        "description": "Customers attempting to checkout are redirected to login repeatedly. Cart items are lost upon authentication redirect.",
        "logs": """2026-10-05 09:05:10 [auth-gateway] WARN: JWT signature verification failed for cookie 'sess_token'.
2026-10-05 09:05:11 [auth-gateway] ERROR: jwt.exceptions.InvalidSignatureError: Signature verification failed. Key ID 'auth-key-2026' not in keyring.
2026-10-05 09:05:15 [auth-gateway] INFO: Redirecting user to /login?redirect=/checkout.""",
        "error_messages": "jwt.exceptions.InvalidSignatureError: Signature verification failed. Token signing key mismatch.",
        "recent_deployment": "Release v1.8.2: 'Key rotation for cookie session storage' deployed 15 minutes ago.",
        "metrics": "401 Unauthorized rate: +310%. Cart abandonments: +180%. Auth service CPU: Normal (14%).",
        "configuration_changes": "Rotated SESSION_SECRET key without keeping previous public key in grace period."
    },
    ("E-commerce", "Performance Issue"): {
        "title": "Product Catalog Search Latency Spike during Search Index Rebuild",
        "severity": "Medium",
        "description": "Product search and category browsing latency surged to 8 seconds. Users report slow loading wheels.",
        "logs": """2026-10-05 14:10:00 [search-service] INFO: Starting background Elasticsearch reindexing task for index 'catalog_products_v2'.
2026-10-05 14:12:30 [search-service] WARN: Search query execution took 7820ms for term 'wireless headphones'.
2026-10-05 14:15:00 [search-service] ERROR: High heap memory utilization on Elasticsearch data node 02 (94%).""",
        "error_messages": "ElasticsearchClusterDegradedException: Search queue capacity exceeded. Query execution latency 7.8s.",
        "recent_deployment": "No application code deployment. Scheduled Elasticsearch index maintenance cron triggered at 14:00.",
        "metrics": "Catalog search p99 latency: 7,850ms (baseline 120ms). ES Node Heap: 94%. Ingress throughput: -25%.",
        "configuration_changes": "Index refresh interval altered to 1s with bulk index thread pool at 16 workers."
    },
    ("E-commerce", "Deployment Failure"): {
        "title": "Checkout Pod CrashLoopBackOff: Missing STRIPE_WEBHOOK_SECRET",
        "severity": "Critical",
        "description": "Application works perfectly locally in docker-compose, but immediately crashes in Kubernetes production upon rolling update.",
        "logs": """2026-10-05 16:30:10 [k8s-kubelet] Started container checkout-service-7c8bb5df84-9r2x1.
2026-10-05 16:30:11 [checkout-service] FATAL: KeyError: 'STRIPE_WEBHOOK_SECRET' environment variable not found in configuration.
2026-10-05 16:30:12 [checkout-service] Process exited with exit code 1.
2026-10-05 16:30:20 [k8s-kubelet] Back-off restarting failed container checkout-service in pod checkout-service-7c8bb5df84-9r2x1.""",
        "error_messages": "KeyError: 'STRIPE_WEBHOOK_SECRET'. Container exited with code 1. Pod state: CrashLoopBackOff.",
        "recent_deployment": "Helm release checkout-service v3.4.1 deployed 10 minutes ago.",
        "metrics": "Healthy pods: 0/6. Ingress 503 Service Unavailable: 100%. CrashLoop backoff restart count: 5.",
        "configuration_changes": "New config field STRIPE_WEBHOOK_SECRET added to code, but omitted from production Kubernetes Secret manifest."
    },
    ("E-commerce", "Microservice Failure"): {
        "title": "Inventory Reservation Service gRPC Timeout Blocking Order Placement",
        "severity": "High",
        "description": "Order orchestration workflow is blocked waiting for Inventory Reservation microservice response.",
        "logs": """2026-10-05 13:00:12 [order-service] INFO: Calling InventoryService.ReserveStock via gRPC for order ORD-1102.
2026-10-05 13:00:27 [order-service] ERROR: grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
    status = StatusCode.DEADLINE_EXCEEDED
    details = "Deadline exceeded after 15.000s waiting for downstream inventory lock"
>""",
        "error_messages": "grpc.StatusCode.DEADLINE_EXCEEDED: Deadline exceeded after 15.000s in inventory-service.",
        "recent_deployment": "Inventory service updated with multi-warehouse locking logic 2 hours ago.",
        "metrics": "Order placement latency: 15.2s. gRPC error rate: 38%. Inventory service active threads: 200/200 (saturated).",
        "configuration_changes": "Default gRPC deadline timeout raised to 15s."
    },

    # 2. RIDE BOOKING
    ("Ride Booking", "API Failure"): {
        "title": "Driver Matching Service 503 & Redis Geospatial Connection Failure",
        "severity": "Critical",
        "description": "Riders in metropolitan areas cannot find nearby drivers. The map shows 'Searching for drivers...' before displaying 'No drivers available'.",
        "logs": """2026-10-05 18:45:10 [dispatch-service] INFO: Querying nearby available drivers in geohash 'dr5ru6'...
2026-10-05 18:45:12 [dispatch-service] ERROR: redis.exceptions.ConnectionError: Error 111 connecting to redis-geo-cluster:6379. Connection refused.
2026-10-05 18:45:15 [dispatch-service] ERROR: Driver matching service returned HTTP 503 Service Unavailable.
2026-10-05 18:45:20 [driver-matching] FATAL: GeoRadius search failed. Redis cluster master node 03 unreachable.""",
        "error_messages": "redis.exceptions.ConnectionError: Connection refused on redis-geo-cluster. Driver dispatch service 503.",
        "recent_deployment": "Deployment dispatch-service-v4.1.0 rolled out 15 minutes ago.",
        "metrics": "Match completion rate: 3% (baseline 92%). Redis cluster node 3 memory: 100% OOM. HTTP 503 count: 2,400/min.",
        "configuration_changes": "Redis maxmemory-policy changed from 'allkeys-lru' to 'noeviction'."
    },
    ("Ride Booking", "Database Failure"): {
        "title": "Ride History & Receipts DB Write Lock Contention",
        "severity": "High",
        "description": "Completed rides are unable to finalize billing receipts; trip completion transactions hanging.",
        "logs": """2026-10-05 19:10:02 [billing-db] ERROR: deadlock detected between process 4921 and process 5104.
2026-10-05 19:10:03 [billing-db] DETAIL: Process 4921 waits for ExclusiveLock on tuple of relation 'trips'; Process 5104 waits for ExclusiveLock on relation 'driver_wallets'.
2026-10-05 19:10:04 [trip-service] ERROR: DatabaseTransactionAborted: transaction aborted due to deadlock.""",
        "error_messages": "Postgres DeadlockDetected: Process 4921 and 5104 deadlocked on tables 'trips' and 'driver_wallets'.",
        "recent_deployment": "Commit 99d81a: 'Refactored driver wallet payout calculation during trip end' deployed 1 hour ago.",
        "metrics": "Deadlocks per minute: 48 (baseline 0). Completed ride finalization backlog: 1,840 trips.",
        "configuration_changes": "Lock acquisition order inverted between trips and driver_wallets in new wallet service."
    },
    ("Ride Booking", "Performance Issue"): {
        "title": "Real-time Vehicle GPS Tracking WebSockets Degradation",
        "severity": "Medium",
        "description": "Rider apps show stale driver car positions on the map; car markers jump sporadically by 500 meters.",
        "logs": """2026-10-05 17:30:00 [ws-gateway] WARN: Client ping/pong heartbeat latency exceeded 4500ms on shard-04.
2026-10-05 17:30:15 [ws-gateway] ERROR: High event loop lag detected (1850ms). Telemetry packet queue length: 42,000.
2026-10-05 17:31:00 [ws-gateway] INFO: Dropping outdated driver GPS coordinate frames to preserve gateway memory.""",
        "error_messages": "NodeEventLoopLagWarning: Event loop lag > 1800ms. WebSocket push packet queue saturated.",
        "recent_deployment": "Increased GPS ping frequency from drivers to 1000ms from 3000ms.",
        "metrics": "Connected WebSocket clients: 120,000. Socket broadcast latency: 4,800ms. Dropped telemetry packets: 18%.",
        "configuration_changes": "GPS client heartbeat interval tightened without scaling WebSocket gateway pods."
    },

    # 3. COLLEGE / STUDENT PORTAL
    ("College Portal", "Performance Issue"): {
        "title": "Hall-Ticket & Exam Portal Extreme Slowdown during Hall-Ticket Download",
        "severity": "Critical",
        "description": "The college website becomes completely unresponsive during hall-ticket download window. 20,000 students trying to log in simultaneously.",
        "logs": """2026-10-05 08:30:10 [portal-web] WARN: Student portal response time exceeded 25,000ms on /api/v1/hallticket/download.
2026-10-05 08:30:22 [portal-db] ERROR: Query execution time 18.4s: SELECT * FROM student_records JOIN exam_registrations ON student_records.id = exam_registrations.student_id WHERE exam_registrations.exam_code = 'CS2026';
2026-10-05 08:30:30 [portal-db] WARN: Sequential scan on table 'student_records' (rows: 150,000) - Missing index on 'student_id'.
2026-10-05 08:31:00 [portal-web] ERROR: Gunicorn worker timeout (pid: 14022) killed after 30 seconds.""",
        "error_messages": "Gunicorn WorkerTimeout: Worker timed out after 30000ms. DB Seq Scan took 18.4s on unindexed student_id.",
        "recent_deployment": "New examination portal release deployed yesterday evening ahead of hall-ticket download.",
        "metrics": "Web Server CPU: 99%. DB CPU: 100%. Concurrent Requests: 8,400 req/sec. Error rate: 58% 504 Gateway Timeout.",
        "configuration_changes": "Database migration script created tables but missed creating index on exam_registrations(student_id)."
    },
    ("College Portal", "Authentication Failure"): {
        "title": "Student Single Sign-On (SSO) LDAP Directory Connection Timeout",
        "severity": "High",
        "description": "Students and faculty unable to log in to university portal via institutional credentials.",
        "logs": """2026-10-05 09:12:00 [sso-service] INFO: Authenticating roll_number '22CS104' against campus Active Directory...
2026-10-05 09:12:15 [sso-service] ERROR: ldap3.core.exceptions.LDAPSocketOpenError: unable to open socket with ldap://ldap.univ.ac.in:389. Connection timed out.
2026-10-05 09:12:16 [sso-service] ERROR: Authentication failed: institutional identity provider unreachable.""",
        "error_messages": "ldap.LDAPSocketOpenError: unable to open socket with ldap.univ.ac.in. Port 389 connection timed out.",
        "recent_deployment": "Campus perimeter firewall rules updated at 08:00 AM.",
        "metrics": "Login success rate: 0%. SSO latency: 15,000ms. Active login queue: 1,200 pending users.",
        "configuration_changes": "Campus network team blocked outbound port 389 traffic in favor of LDAPS (port 636)."
    },

    # 4. BANKING
    ("Banking", "Authentication Failure"): {
        "title": "Core Banking JWT Validation Failure & Expired Public Signing Cert",
        "severity": "Critical",
        "description": "Customers cannot log in to mobile banking app or net banking. All customer authentication attempts fail with 401 Unauthorized.",
        "logs": """2026-10-05 06:00:01 [auth-service] INFO: Validating JWT token header alg='RS256', kid='bank-root-2025-cert'.
2026-10-05 06:00:02 [auth-service] ERROR: cryptography.x509.CertificateExpired: Signing certificate 'bank-root-2025-cert' expired on 2026-10-05 05:59:59 UTC.
2026-10-05 06:00:03 [auth-service] ERROR: jwt.exceptions.InvalidKeyError: Unable to verify signature: certificate expired.
2026-10-05 06:00:10 [api-gateway] WARN: Rejecting customer request with HTTP 401 Unauthorized.""",
        "error_messages": "CertificateExpired: RSA Public Signing Certificate expired at 2026-10-05 05:59:59. JWT verification rejected.",
        "recent_deployment": "No application deployment. Annual TLS/Signing certificate rollover scheduled for today.",
        "metrics": "Mobile Banking Login Failure Rate: 99.8%. Active sessions dropped: 45,000. Customer support call queue: Saturated.",
        "configuration_changes": "New 2026 certificate was created in secret vault, but auth-service JWKS cache was not invalidated."
    },
    ("Banking", "Database Failure"): {
        "title": "Account Balance Ledger Isolation Failure during High-Value Settlement",
        "severity": "Critical",
        "description": "Core ledger database rejecting credit transfers due to transaction isolation serializable conflicts.",
        "logs": """2026-10-05 11:40:02 [ledger-service] INFO: Initiating NEFT transfer batch batch_id=NEFT-4091.
2026-10-05 11:40:05 [ledger-db] ERROR: could not serialize access due to concurrent update on table 'account_balances'.
2026-10-05 11:40:06 [ledger-service] ERROR: Postgres error code 40001: serialization_failure. Transaction aborted.
2026-10-05 11:40:10 [ledger-service] WARN: Batch retry attempt 1 failed with concurrent conflict.""",
        "error_messages": "psycopg2.errors.SerializationFailure: could not serialize access due to concurrent update (SQLSTATE 40001).",
        "recent_deployment": "Patch release ledger-engine-v5.2 deployed 35 minutes ago.",
        "metrics": "Failed settlement transactions: 1,420. Rollback count: +480%. Ledger latency: 4,200ms.",
        "configuration_changes": "Transaction isolation level elevated from READ COMMITTED to SERIALIZABLE without optimistic retry backoff."
    },

    # 5. CHAT APPLICATION
    ("Chat Application", "Microservice Failure"): {
        "title": "Messages Stuck in 'Sending' Status: RabbitMQ Queue Backlog & Worker Outage",
        "severity": "High",
        "description": "Users across web and mobile platforms report messages remaining in 'sending' status with spinning clock indicator. Messages not delivering to recipients.",
        "logs": """2026-10-05 15:10:02 [chat-api] INFO: Message MSG-99120 accepted from user_id=4021. Enqueuing to 'chat.delivery.queue'...
2026-10-05 15:10:15 [rabbitmq] WARN: Queue 'chat.delivery.queue' memory alarm raised! Messages in queue: 850,000.
2026-10-05 15:10:20 [rabbitmq] ERROR: Connection blocked: memory high watermark (0.40) exceeded on rabbitmq-node-01.
2026-10-05 15:11:00 [chat-worker] FATAL: Worker process worker-03 terminated unexpectedly with MemoryError. Active consumer count: 0.""",
        "error_messages": "RabbitMQ memory alarm: queue 'chat.delivery.queue' unacknowledged messages > 850,000. Consumers died.",
        "recent_deployment": "Commit c189a2: 'Add image preview generation inside chat delivery worker' deployed 50 minutes ago.",
        "metrics": "Queue backlog: 850,000 messages. Delivery delay: 18 minutes. Active workers: 0/12. RabbitMQ RAM: 94%.",
        "configuration_changes": "Worker concurrency elevated to 32 per pod, causing Python worker pods to exceed cgroup memory limits."
    },

    # 6. DELIVERY APPLICATION
    ("Delivery Application", "Deployment Failure"): {
        "title": "Order Dispatcher Fails Startup: GeoIP Library Version Mismatch",
        "severity": "Critical",
        "description": "Dispatch service builds and runs in staging, but crashes on startup in production container cluster.",
        "logs": """2026-10-05 12:00:10 [container-init] Starting delivery-dispatch-service:v2.9.0...
2026-10-05 12:00:12 [delivery-dispatch] ERROR: ImportError: libgeos_c.so.1: cannot open shared object file: No such file or directory.
2026-10-05 12:00:13 [delivery-dispatch] FATAL: Shapely/GeoIP native C extension library could not be loaded.
2026-10-05 12:00:15 [k8s-pod] Container exited with exit code 127.""",
        "error_messages": "ImportError: libgeos_c.so.1: cannot open shared object file. Container exit code 127.",
        "recent_deployment": "Base Docker image changed from ubuntu:22.04 to python:3.11-alpine in production Dockerfile.",
        "metrics": "Dispatch Pod Ready Count: 0/4. Pending orders awaiting driver assignment: 620.",
        "configuration_changes": "Switched Docker base image to Alpine without compiling native C geospatial libraries (GEOS)."
    }
}

@router.get("/domains")
def get_supported_domains():
    """List supported applications and failure types."""
    return {
        "applications": [
            "E-commerce",
            "Ride Booking",
            "College Portal",
            "Banking",
            "Chat Application",
            "Delivery Application"
        ],
        "incident_types": [
            "Database Failure",
            "API Failure",
            "Authentication Failure",
            "Performance Issue",
            "Deployment Failure",
            "Microservice Failure"
        ]
    }

@router.post("/generate", response_model=SimulatedScenario)
def generate_simulated_incident(req: SimulationRequest):
    """
    Generate realistic simulated incident evidence based on user selection.
    Guarantees rich logs, error messages, recent deployment info, and metrics.
    """
    key = (req.application, req.incident_type)
    
    # Check if exact key exists in matrix
    if key in SIMULATION_MATRIX:
        data = SIMULATION_MATRIX[key]
        return SimulatedScenario(
            title=f"[SIMULATED] {data['title']}",
            application=req.application,
            incident_type=req.incident_type,
            severity=data["severity"],
            description=data["description"],
            logs=data["logs"],
            error_messages=data["error_messages"],
            recent_deployment=data["recent_deployment"],
            metrics=data["metrics"],
            configuration_changes=data["configuration_changes"]
        )
        
    # Dynamic fallback generator for any combination
    title = f"[SIMULATED] {req.application} {req.incident_type} Incident"
    logs = f"""2026-10-05 10:00:01 [{req.application.lower().replace(' ', '-')}-core] WARN: Anomaly detected in {req.incident_type}.
2026-10-05 10:00:15 [{req.application.lower().replace(' ', '-')}-core] ERROR: Downstream subsystem failed to respond within threshold.
2026-10-05 10:00:22 [{req.application.lower().replace(' ', '-')}-core] FATAL: HTTP 500 Internal Server Error returned to ingress."""
    
    err = f"SubsystemFailureException: {req.incident_type} in {req.application}. Operation timed out or crashed."
    deploy = "Recent release deployed 30 minutes prior to failure manifestation."
    metrics = f"Service latency: 5,400ms (baseline 120ms). 5xx Error rate: 38%. Telemetry alert active."
    configs = "Configuration values modified during recent release maintenance window."

    return SimulatedScenario(
        title=title,
        application=req.application,
        incident_type=req.incident_type,
        severity="High",
        description=f"Simulated {req.incident_type} affecting {req.application}. End-users experiencing elevated failure rates and degraded performance.",
        logs=logs,
        error_messages=err,
        recent_deployment=deploy,
        metrics=metrics,
        configuration_changes=configs
    )
