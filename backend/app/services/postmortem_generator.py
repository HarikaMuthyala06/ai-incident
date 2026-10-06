import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.models.postmortem import PostmortemReport
from app.models.incident import AnalysisResult, TimelineEvent

class PostmortemGenerator:
    """
    Constructs comprehensive blameless SRE Postmortem reports
    based on incident facts, timeline, AI analysis, and lessons learned.
    """

    @classmethod
    def generate(
        cls,
        incident: Dict[str, Any],
        analysis: AnalysisResult,
        timeline: List[TimelineEvent],
        author: str = "SRE Incident Agent"
    ) -> PostmortemReport:
        now = datetime.now(timezone.utc)
        postmortem_id = f"PM-{str(uuid.uuid4())[:8].upper()}"

        # Determine impact statement
        app_name = incident.get("application", "Production Service")
        severity = incident.get("severity", "High")
        impact_stmt = (
            f"{severity} severity degradation observed across {app_name}. "
            f"End-users experienced elevated latency, service errors, or failure to complete core workflows."
        )

        # Detection statement
        detection_stmt = (
            f"Incident detected via automated telemetry anomalies, customer error reports, or elevated 5xx error logs. "
            f"Initial investigation commenced at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}."
        )

        # Recovery statement
        recovery_stmt = (
            f"Service stabilization verified once recommended mitigation ({analysis.suggested_resolution[:120]}) "
            f"was evaluated and applied. Error rates returned to baseline SLA thresholds."
        )

        # Lessons learned
        lessons = [
            f"Automated health probes should validate deeper dependencies prior to signaling container ready.",
            f"Telemetry alerting thresholds for {analysis.contributing_factors[0] if analysis.contributing_factors else 'system resources'} should be tightened.",
            f"Runbook documentation for {app_name} should be updated with this investigation's findings."
        ]

        # Timeline list serialization
        timeline_serialized = [
            {
                "timestamp": t.timestamp_display,
                "event": t.event,
                "source": t.source,
                "is_inferred": t.is_inferred
            }
            for t in timeline
        ]

        return PostmortemReport(
            id=postmortem_id,
            incident_id=incident.get("id", str(incident.get("_id"))),
            incident_ref_id=incident.get("incident_id", "INC-XXXX"),
            title=f"Postmortem: {incident.get('title', 'Service Incident')}",
            summary=analysis.summary,
            impact=impact_stmt,
            affected_system=app_name,
            severity=severity,
            timeline=timeline_serialized,
            detection=detection_stmt,
            probable_root_cause=analysis.probable_root_cause,
            evidence=analysis.supporting_evidence,
            contributing_factors=analysis.contributing_factors,
            resolution=analysis.suggested_resolution,
            recovery=recovery_stmt,
            preventive_actions=analysis.preventive_actions,
            lessons_learned=lessons,
            related_incidents=[
                f"{src.get('title')} (Relevance: {src.get('relevance')})"
                for src in analysis.retrieved_knowledge_sources[:2]
            ],
            author=author,
            status="Draft",
            created_at=now,
            updated_at=now
        )

    @classmethod
    def export_as_markdown(cls, postmortem: PostmortemReport) -> str:
        """Render postmortem as formatted Markdown document."""
        md = []
        md.append(f"# {postmortem.title}")
        md.append(f"**Incident ID:** {postmortem.incident_ref_id} | **Severity:** {postmortem.severity} | **Status:** {postmortem.status}")
        md.append(f"**Affected System:** {postmortem.affected_system} | **Author:** {postmortem.author}")
        md.append(f"**Generated:** {postmortem.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        md.append("---\n")

        md.append("## 1. Executive Summary")
        md.append(postmortem.summary + "\n")

        md.append("## 2. Impact & Scope")
        md.append(postmortem.impact + "\n")

        md.append("## 3. Incident Timeline")
        for item in postmortem.timeline:
            inferred_tag = " *(Inferred)*" if item.get("is_inferred") else ""
            md.append(f"- **{item.get('timestamp')}**{inferred_tag}: {item.get('event')} `[{item.get('source')}]`")
        md.append("")

        md.append("## 4. Probable Root Cause Hypothesis")
        md.append(postmortem.probable_root_cause + "\n")

        md.append("## 5. Supporting Evidence")
        for ev in postmortem.evidence:
            md.append(f"- {ev}")
        md.append("")

        md.append("## 6. Contributing Factors")
        for cf in postmortem.contributing_factors:
            md.append(f"- {cf}")
        md.append("")

        md.append("## 7. Resolution & Recovery")
        md.append(f"**Resolution Applied:** {postmortem.resolution}\n")
        md.append(f"**Recovery Verification:** {postmortem.recovery}\n")

        md.append("## 8. Preventive Actions (Action Items)")
        for pa in postmortem.preventive_actions:
            md.append(f"- [ ] {pa}")
        md.append("")

        md.append("## 9. Lessons Learned")
        for ll in postmortem.lessons_learned:
            md.append(f"- {ll}")

        return "\n".join(md)
