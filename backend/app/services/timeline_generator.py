import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.incident import TimelineEvent

class TimelineGenerator:
    """
    Constructs an incident timeline from logs, deployment notes, metrics, and error traces.
    Adheres strictly to the safety rule:
    'If exact timestamps are unavailable, clearly indicate that the timeline is inferred or approximate.
    Do not invent real timestamps.'
    """

    @classmethod
    def generate_timeline(
        cls,
        logs: str = "",
        recent_deployment: str = "",
        metrics: str = "",
        error_messages: str = "",
        incident_description: str = ""
    ) -> List[TimelineEvent]:
        events: List[TimelineEvent] = []

        # 1. Look for explicit ISO or standard log timestamps: e.g. "2026-10-05 10:14:22", "10:15:00", "[14:22:10]"
        timestamp_regex = re.compile(
            r"(\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?|\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|UTC)?\b|\[\d{2}:\d{2}:\d{2}\])",
            re.IGNORECASE
        )

        # Scan log lines for real timestamps
        if logs:
            lines = logs.strip().split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean:
                    continue
                match = timestamp_regex.search(line_clean)
                if match:
                    ts = match.group(1).strip("[]")
                    # Clean remainder of line for event text
                    event_text = line_clean.replace(match.group(0), "").strip(" -:[]")
                    if len(event_text) > 5:
                        events.append(TimelineEvent(
                            timestamp_display=ts,
                            event=event_text[:120],
                            source="Application Logs",
                            is_inferred=False
                        ))

        # Scan deployment information
        if recent_deployment:
            match = timestamp_regex.search(recent_deployment)
            if match:
                events.append(TimelineEvent(
                    timestamp_display=match.group(1).strip("[]"),
                    event=f"Deployment event: {recent_deployment[:100]}",
                    source="Deployment Record",
                    is_inferred=False
                ))
            else:
                events.append(TimelineEvent(
                    timestamp_display="T-30m (Inferred)",
                    event=f"Recent change/release: {recent_deployment[:100]}",
                    source="Deployment Record",
                    is_inferred=True
                ))

        # Scan metrics
        if metrics:
            match = timestamp_regex.search(metrics)
            if match:
                events.append(TimelineEvent(
                    timestamp_display=match.group(1).strip("[]"),
                    event=f"Metric anomaly recorded: {metrics[:100]}",
                    source="System Metrics",
                    is_inferred=False
                ))
            else:
                events.append(TimelineEvent(
                    timestamp_display="T-15m (Inferred)",
                    event=f"Telemetry anomaly detected: {metrics[:100]}",
                    source="System Metrics",
                    is_inferred=True
                ))

        # Scan error traces
        if error_messages:
            match = timestamp_regex.search(error_messages)
            if match:
                events.append(TimelineEvent(
                    timestamp_display=match.group(1).strip("[]"),
                    event=f"Exception raised: {error_messages.splitlines()[0][:100]}",
                    source="Error Trace",
                    is_inferred=False
                ))
            else:
                events.append(TimelineEvent(
                    timestamp_display="T-5m (Inferred)",
                    event=f"Failure manifested: {error_messages.splitlines()[0][:100]}",
                    source="Error Trace",
                    is_inferred=True
                ))

        # Incident Reported / Investigation Commenced
        events.append(TimelineEvent(
            timestamp_display="T+0m (Investigation Triggered)",
            event="Incident created and investigation initialized in AI Agent.",
            source="Investigation Platform",
            is_inferred=False
        ))

        # Deduplicate and sort
        seen = set()
        unique_events = []
        for e in events:
            key = (e.timestamp_display, e.event[:30])
            if key not in seen:
                seen.add(key)
                unique_events.append(e)

        return unique_events[:8]
