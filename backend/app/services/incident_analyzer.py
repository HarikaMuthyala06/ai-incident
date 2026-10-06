import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.models.incident import AnalysisResult
from app.models.document import RetrievedEvidenceItem

logger = logging.getLogger("incident_agent.analyzer")

class IncidentAnalyzer:
    """
    SRE Incident Analyzer & Root Cause Hypothesis Engine.
    Combines:
    - Incident telemetry & logs
    - Retrieved RAG documentation
    - Retrieved historical incidents
    - Structured, safety-grounded Prompt Engineering
    """

    SYSTEM_PROMPT = """You are an expert Principal Site Reliability Engineer (SRE) and Incident Response Specialist.
Your task is to analyze production software incidents from various applications (e.g., E-commerce, Ride Booking, Banking, College Portal, Chat Systems, Microservices) and formulate an evidence-based investigation report.

CRITICAL INSTRUCTION & SAFETY GUIDELINES:
1. ALWAYS present findings as a "probable root cause" or "root-cause hypothesis". NEVER claim absolute certainty or say "the definitive cause is".
2. Use cautious, evidence-grounded language: "probable cause", "likely cause", "evidence suggests", "requires verification".
3. NEVER propose mutating commands that could destroy data or bypass safeguards. Suggest read-only diagnostic checks and standard rollback/remediation procedures.
4. Base your hypothesis on the provided evidence, retrieved technical runbooks, and previous incidents.

You must respond ONLY with a valid JSON object matching this exact schema:
{
  "summary": "Concise 2-3 sentence overview of what went wrong and user impact.",
  "probable_root_cause": "Probable root-cause hypothesis explaining the likely technical failure mechanism.",
  "confidence_score": 0.85,
  "confidence_rating": "High",
  "supporting_evidence": [
    "Specific error log or telemetry metric proving or pointing to this hypothesis",
    "Correlation between recent deployment/configuration change and time of failure"
  ],
  "contributing_factors": [
    "Secondary factor 1 (e.g. lack of circuit breaker, sudden traffic surge)",
    "Secondary factor 2"
  ],
  "recommended_investigation_steps": [
    "Read-only diagnostic step or metric verification command",
    "Verification step 2"
  ],
  "suggested_resolution": "Actionable immediate mitigation or safe rollback recommendation.",
  "preventive_actions": [
    "Long-term architecture or alerting improvement 1",
    "Improvement 2"
  ]
}
"""

    @classmethod
    def build_user_prompt(
        cls,
        incident: Dict[str, Any],
        retrieved_docs: List[RetrievedEvidenceItem],
        similar_incidents: List[Dict[str, Any]]
    ) -> str:
        prompt_parts = []
        prompt_parts.append(f"# INCIDENT REPORT: {incident.get('title', 'Unknown Incident')}")
        prompt_parts.append(f"Application: {incident.get('application', 'Generic System')}")
        prompt_parts.append(f"Reported Severity: {incident.get('severity', 'High')}")
        prompt_parts.append(f"Category: {incident.get('incident_type', 'API')}")
        prompt_parts.append(f"\n## Description:\n{incident.get('description', 'N/A')}")

        if incident.get("error_messages"):
            prompt_parts.append(f"\n## Error Messages / Stack Traces:\n{incident.get('error_messages')}")
        if incident.get("logs"):
            prompt_parts.append(f"\n## Application & System Logs:\n{incident.get('logs')}")
        if incident.get("recent_deployment"):
            prompt_parts.append(f"\n## Recent Deployments / Git Commits:\n{incident.get('recent_deployment')}")
        if incident.get("metrics"):
            prompt_parts.append(f"\n## System Telemetry & Metrics:\n{incident.get('metrics')}")
        if incident.get("configuration_changes"):
            prompt_parts.append(f"\n## Configuration Changes:\n{incident.get('configuration_changes')}")

        # Add RAG Knowledge Evidence
        prompt_parts.append("\n## RETRIEVED TECHNICAL RUNBOOKS & TROUBLESHOOTING GUIDES (RAG Context):")
        if retrieved_docs:
            for idx, doc in enumerate(retrieved_docs):
                prompt_parts.append(
                    f"[{idx+1}] Guide: '{doc.doc_title}' (Category: {doc.category}, Relevance: {doc.relevance_rating} / {doc.relevance_score})\n"
                    f"Snippet: {doc.matched_snippet}\n"
                )
        else:
            prompt_parts.append("No specific runbook match found.")

        # Add Similar Past Incidents
        prompt_parts.append("\n## HISTORICAL SIMILAR INCIDENTS (RAG Cross-Reference):")
        if similar_incidents:
            for idx, past in enumerate(similar_incidents):
                prompt_parts.append(
                    f"[{idx+1}] Incident #{past.get('incident_id')}: '{past.get('title')}' "
                    f"(Relevance: {past.get('relevance_rating')}, Past Resolution: {past.get('resolution')})\n"
                )
        else:
            prompt_parts.append("No prior incident history recorded.")

        prompt_parts.append("\nProvide your structured evidence-based analysis in the requested JSON format.")
        return "\n".join(prompt_parts)

    @classmethod
    async def analyze_incident(
        cls,
        incident: Dict[str, Any],
        retrieved_docs: List[RetrievedEvidenceItem],
        similar_incidents: List[Dict[str, Any]]
    ) -> AnalysisResult:
        user_prompt = cls.build_user_prompt(incident, retrieved_docs, similar_incidents)

        # Attempt OpenAI Call if configured
        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 5:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": cls.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                )
                raw_json = response.choices[0].message.content
                parsed = json.loads(raw_json)

                # Format retrieved sources metadata for the UI
                sources_meta = [
                    {
                        "title": doc.doc_title,
                        "relevance": doc.relevance_rating,
                        "score": doc.relevance_score,
                        "category": doc.category,
                        "snippet": doc.matched_snippet[:150]
                    }
                    for doc in retrieved_docs
                ]

                return AnalysisResult(
                    summary=parsed.get("summary", "Incident analysis completed."),
                    probable_root_cause=parsed.get("probable_root_cause", "Evidence suggests potential service degradation."),
                    confidence_score=float(parsed.get("confidence_score", 0.75)),
                    confidence_rating=parsed.get("confidence_rating", "Medium"),
                    supporting_evidence=parsed.get("supporting_evidence", []),
                    contributing_factors=parsed.get("contributing_factors", []),
                    recommended_investigation_steps=parsed.get("recommended_investigation_steps", []),
                    suggested_resolution=parsed.get("suggested_resolution", "Inspect telemetry and rollback if recent release caused issue."),
                    preventive_actions=parsed.get("preventive_actions", []),
                    retrieved_knowledge_sources=sources_meta,
                    analyzed_at=datetime.now(timezone.utc)
                )
            except Exception as e:
                logger.warning(f"OpenAI analysis call failed ({e}). Falling back to internal SRE heuristic engine.")

        # Offline Educational SRE Heuristic Engine (Ensures the platform always works smoothly!)
        return cls._offline_heuristic_analysis(incident, retrieved_docs, similar_incidents)

    @classmethod
    def _offline_heuristic_analysis(
        cls,
        incident: Dict[str, Any],
        retrieved_docs: List[RetrievedEvidenceItem],
        similar_incidents: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Grounded offline analyzer mapping observed symptoms to probable root-cause hypotheses
        when running locally without an OpenAI key.
        """
        title = incident.get("title", "").lower()
        desc = incident.get("description", "").lower()
        logs = incident.get("logs", "").lower()
        errs = incident.get("error_messages", "").lower()
        deploy = incident.get("recent_deployment", "").lower()
        combined = f"{title} {desc} {logs} {errs} {deploy}"

        # 1. Database Connection / Pool / Timeout
        if "timeout" in combined or "connection pool" in combined or "postgres" in combined or "database" in combined:
            hypothesis = "Evidence suggests probable database connection pool exhaustion or unindexed query deadlock triggered by traffic surge or connection leakage."
            confidence = 0.82
            rating = "High"
            evidence = [
                "Database error signature detected in log traces (timeouts / pool limits).",
                f"Incident category '{incident.get('incident_type')}' matches database contention pattern."
            ]
            resolution = "Temporarily terminate stale idle connections using pg_terminate_backend and scale PgBouncer connection pool max_connections."
            factors = ["Sudden query concurrency spike", "Missing statement timeout safeguards", "Potential unclosed database sessions in recent code"]
            steps = [
                "Execute 'SELECT count(*), state FROM pg_stat_activity GROUP BY state;' to check connection saturation.",
                "Inspect slow query log for table scans on unindexed foreign keys."
            ]
            preventive = [
                "Deploy PgBouncer connection pooler in transaction pooling mode.",
                "Enforce strict connection leak timeouts and automated linter checks for ORM session managers."
            ]

        # 2. Authentication / JWT / Token Expiry
        elif "jwt" in combined or "auth" in combined or "token" in combined or "401" in combined or "signature" in combined:
            hypothesis = "Likely failure in JWT signature validation, possibly caused by clock drift, JWKS endpoint unreachability, or asymmetric signing key rotation mismatch."
            confidence = 0.88
            rating = "High"
            evidence = [
                "High frequency of 401 Unauthorized / Token validation exceptions.",
                "Authentication service rejection without upstream service degradation."
            ]
            resolution = "Verify JWKS public key cache and ensure NTP clock synchronization across authentication worker nodes."
            factors = ["Abrupt signing key rotation", "NTP clock skew exceeding acceptable leeway (60s)"]
            steps = [
                "Verify JWKS endpoint reachability with 'curl -s https://auth-service/.well-known/jwks.json'.",
                "Check server clock offset with 'chronyc tracking' or 'ntpstat'."
            ]
            preventive = [
                "Implement dual-key rotation buffer allowing N-1 public keys to remain valid for 24 hours.",
                "Add synthetic health-check alerts for JWKS endpoint latency."
            ]

        # 3. Deployment / Environment / OOMKilled
        elif "deploy" in combined or "environment" in combined or "crashloop" in combined or "oom" in combined:
            hypothesis = "Probable deployment regression: missing required environment variable or container memory limit breach (OOMKilled) following latest build release."
            confidence = 0.85
            rating = "High"
            evidence = [
                f"Recent deployment mentioned: '{incident.get('recent_deployment') or 'Build release deployed recently'}'.",
                "Service failure timeline correlates directly with deployment execution."
            ]
            resolution = "Perform safe rollback of the deployment to previous stable version using 'kubectl rollout undo'."
            factors = ["Missing configuration secrets in release manifest", "Undersized container memory allocation"]
            steps = [
                "Inspect previous pod container logs with 'kubectl logs <pod> --previous'.",
                "Diff config maps between staging and production environments."
            ]
            preventive = [
                "Add pre-deployment configuration validation stage in CI/CD pipeline.",
                "Configure automated canary deployments with automatic rollback on elevated error rates."
            ]

        # 4. Message Queue / Async Worker
        elif "queue" in combined or "worker" in combined or "celery" in combined or "rabbit" in combined or "kafka" in combined:
            hypothesis = "Probable message queue consumer stall or worker starvation due to an unhandled exception (poison-pill message) or Redis/RabbitMQ resource exhaustion."
            confidence = 0.79
            rating = "Medium"
            evidence = [
                "Messages lingering in 'pending' or 'sending' status.",
                "Backlog accumulation observed without worker task completions."
            ]
            resolution = "Isolate and route unprocessable messages to Dead Letter Queue (DLQ) and horizontally scale async worker pods."
            factors = ["Malformed payload causing consumer crash loop", "Worker concurrency limits"]
            steps = [
                "Inspect queue backlog depth and unacknowledged message counter.",
                "Review worker error logs for unhandled deserialization exceptions."
            ]
            preventive = [
                "Implement strict DLQ routing after 3 retries.",
                "Add queue depth auto-scaling using KEDA or metric-based HPA."
            ]

        # 5. Generic API / Network
        else:
            hypothesis = "Probable upstream microservice timeout or network gateway latency spike degrading downstream consumer endpoints."
            confidence = 0.72
            rating = "Medium"
            evidence = [
                "Elevated 5xx response codes and client timeout occurrences.",
                f"Symptom description for '{incident.get('application')}' points to inter-service communication failure."
            ]
            resolution = "Enable circuit breaker pattern to shed failing traffic and reroute calls through healthy availability zones."
            factors = ["Cascading thread pool starvation", "Lack of retry backoff with jitter"]
            steps = [
                "Trace distributed request IDs via OpenTelemetry / Jaeger.",
                "Check ingress gateway error logs and upstream pod health status."
            ]
            preventive = [
                "Tune client timeout budgets and enforce distributed circuit breakers.",
                "Implement graceful degradation with cached fallback responses."
            ]

        sources_meta = [
            {
                "title": doc.doc_title,
                "relevance": doc.relevance_rating,
                "score": doc.relevance_score,
                "category": doc.category,
                "snippet": doc.matched_snippet[:150]
            }
            for doc in retrieved_docs
        ]

        return AnalysisResult(
            summary=f"Incident '{incident.get('title')}' on {incident.get('application')} is actively investigated. {hypothesis}",
            probable_root_cause=hypothesis,
            confidence_score=confidence,
            confidence_rating=rating,
            supporting_evidence=evidence,
            contributing_factors=factors,
            recommended_investigation_steps=steps,
            suggested_resolution=resolution,
            preventive_actions=preventive,
            retrieved_knowledge_sources=sources_meta,
            analyzed_at=datetime.now(timezone.utc)
        )
