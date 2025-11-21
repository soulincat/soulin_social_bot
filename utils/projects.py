"""
Helpers for working with multi-project client configs.
"""
from __future__ import annotations

from typing import Any, Dict, List


def extract_projects(client: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns a normalized list of project definitions for the client.

    Each project dict contains:
      - project_id
      - project_name
      - funnel_structure
      - report_settings
      - custom_benchmarks
      - connected_accounts
      - stripe_customer_id (optional)
      - scope_id (unique identifier for history/manual metrics)
    """
    client_id = client.get("client_id", "client")
    base_name = client.get("name", "Project")

    def build_project(project: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
        project_id = project.get("project_id") or f"{client_id}_proj_{index}"
        project_name = project.get("project_name") or (
            base_name if index == 0 else f"{base_name} #{index + 1}"
        )

        return {
            "project_id": project_id,
            "project_name": project_name,
            "funnel_structure": project.get("funnel_structure", client.get("funnel_structure", {})),
            "report_settings": project.get("report_settings", client.get("report_settings", {})),
            "custom_benchmarks": project.get("custom_benchmarks", client.get("custom_benchmarks", {})),
            "connected_accounts": project.get("connected_accounts", client.get("connected_accounts", {})),
            "stripe_customer_id": project.get("stripe_customer_id") or client.get("stripe_customer_id"),
            "scope_id": f"{client_id}:{project_id}",
        }

    projects = client.get("projects")
    if projects and isinstance(projects, list):
        normalized = []
        for idx, project in enumerate(projects):
            normalized.append(build_project(project or {}, idx))
        return normalized

    # Legacy single-project clients
    return [
        build_project(
            {
                "project_id": f"{client_id}_default",
                "project_name": base_name,
            },
            0,
        )
    ]

