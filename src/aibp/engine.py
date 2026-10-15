"""Architecture validation and report generation."""

from __future__ import annotations

from typing import Any


LAYER_LABELS = {
    "data_ingestion": "Data ingestion",
    "storage_processing": "Storage and processing",
    "retrieval": "Vector search and retrieval",
    "models": "Models and evaluation",
    "orchestration": "Agents and orchestration",
    "application_api": "Application and API",
    "integrations": "Integrations",
    "security_governance": "Security and governance",
    "infrastructure_observability": "Infrastructure and observability",
}

REQUIRED_CONTROLS = {
    "authentication": "Authentication",
    "authorization": "Authorization",
    "secrets_management": "Secrets management",
    "encryption_at_rest": "Encryption at rest",
    "encryption_in_transit": "Encryption in transit",
    "audit_logging": "Audit logging",
    "backups": "Backups",
    "ci_cd": "CI/CD",
}


def _is_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def validate_spec(spec: Any) -> list[str]:
    """Return structural errors found in an architecture specification."""
    errors: list[str] = []

    if not isinstance(spec, dict):
        return ["The specification root must be a JSON object."]

    project = spec.get("project")
    if not isinstance(project, dict):
        errors.append("'project' must be an object.")
    else:
        for key in ("name", "goal"):
            if not isinstance(project.get(key), str) or not project[key].strip():
                errors.append(f"'project.{key}' is required and must be a non-empty string.")

    layers = spec.get("layers")
    if not isinstance(layers, dict):
        errors.append("'layers' must be an object.")
        return errors

    for key, label in LAYER_LABELS.items():
        components = layers.get(key)
        if not _is_string_list(components) or not components:
            errors.append(
                f"Layer '{key}' ({label}) must contain a non-empty list of strings."
            )

    controls = spec.get("controls", {})
    if not isinstance(controls, dict):
        errors.append("'controls' must be an object when provided.")

    return errors


def assess_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Evaluate structural validity and recommended production controls."""
    errors = validate_spec(spec)
    warnings: list[str] = []
    passed: list[str] = []

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "passed": passed}

    controls = spec.get("controls", {})

    for key, label in REQUIRED_CONTROLS.items():
        if controls.get(key) is True:
            passed.append(f"{label} is marked as planned.")
        else:
            warnings.append(f"{label} is not marked as planned.")

    observability = controls.get("observability", [])
    if not isinstance(observability, list):
        observability = []

    for signal in ("logs", "metrics", "traces"):
        if signal in observability:
            passed.append(f"{signal.capitalize()} are included in observability.")
        else:
            warnings.append(f"Observability does not list {signal}.")

    orchestration = spec["layers"]["orchestration"]
    agentic_terms = ("agent", "tool calling", "tool-calling", "autonomous")
    appears_agentic = any(
        term in component.lower()
        for component in orchestration
        for term in agentic_terms
    )

    if appears_agentic:
        if controls.get("human_approval_for_high_impact_actions") is True:
            passed.append("Human approval is planned for high-impact actions.")
        else:
            warnings.append(
                "Agentic workflows are listed, but human approval for high-impact "
                "actions is not marked as planned."
            )

    requirements = spec.get("requirements", {})
    if isinstance(requirements, dict):
        availability = requirements.get("availability_target")
        if availability and not controls.get("backups"):
            warnings.append(
                f"Availability target '{availability}' is specified, but backups "
                "are not marked as planned."
            )

    return {
        "valid": True,
        "errors": errors,
        "warnings": warnings,
        "passed": passed,
    }


def _markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def render_markdown(spec: dict[str, Any], assessment: dict[str, Any]) -> str:
    """Render a human-readable architecture review."""
    project = spec["project"]
    requirements = spec.get("requirements", {})
    lines = [
        f"# Architecture review: {project['name']}",
        "",
        f"**Goal:** {project['goal']}",
        "",
    ]

    if isinstance(requirements, dict) and requirements:
        lines.extend(["## Requirements", ""])
        for key, value in requirements.items():
            label = key.replace("_", " ").capitalize()
            lines.append(f"- **{label}:** {value}")
        lines.append("")

    lines.extend(["## Nine-layer architecture", ""])
    for key, label in LAYER_LABELS.items():
        lines.append(f"### {label}")
        for component in spec["layers"][key]:
            lines.append(f"- {component}")
        lines.append("")

    lines.extend(
        [
            "## Review results",
            "",
            f"**Specification valid:** {'Yes' if assessment['valid'] else 'No'}",
            "",
            "### Recommended controls present",
            _markdown_list(assessment["passed"]),
            "",
            "### Risks and follow-up items",
            _markdown_list(assessment["errors"] + assessment["warnings"]),
            "",
            "## Deployment note",
            "",
            "This review is a planning aid. Validate security, compliance, reliability, "
            "capacity, and cost against the actual workload before production deployment.",
            "",
        ]
    )
    return "\n".join(lines)
