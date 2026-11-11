#!/usr/bin/env python3
"""Remove old workflow runs, Actions caches, and inactive Pages deployments."""

from __future__ import annotations

import json
import os
import subprocess

REPO = os.environ.get("GITHUB_REPOSITORY", "Darkstar085/app-updater")


def gh_api(endpoint: str, *args: str):
    command = ["gh", "api", endpoint, *args]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def delete(endpoint: str) -> None:
    subprocess.run(["gh", "api", "--method", "DELETE", endpoint], check=True)


def paginated(endpoint: str, key: str | None = None) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        batch = gh_api(f"{endpoint}?per_page=100&page={page}") or []
        values = batch.get(key, []) if isinstance(batch, dict) and key else batch
        if not values:
            break
        items.extend(values)
        if len(values) < 100:
            break
        page += 1
    return items


def cleanup_runs() -> int:
    runs = paginated(f"repos/{REPO}/actions/runs", "workflow_runs")
    runs_sorted = sorted(runs, key=lambda run: run.get("created_at", ""), reverse=True)
    removed = 0
    for run in runs_sorted[1:]:
        delete(f"repos/{REPO}/actions/runs/{run['id']}")
        removed += 1
    return removed


def cleanup_caches() -> int:
    caches = paginated(f"repos/{REPO}/actions/caches", "actions_caches")
    for cache in caches:
        delete(f"repos/{REPO}/actions/caches/{cache['id']}")
    return len(caches)


def cleanup_deployments() -> int:
    deployments = paginated(f"repos/{REPO}/deployments")
    pages_deployments = [
        deployment for deployment in deployments
        if deployment.get("environment") == "github-pages"
    ]
    pages_deployments.sort(
        key=lambda deployment: deployment.get("created_at", ""), reverse=True
    )

    removed = 0
    for deployment in pages_deployments[1:]:
        deployment_id = deployment["id"]
        endpoint = f"repos/{REPO}/deployments/{deployment_id}"
        statuses = gh_api(f"{endpoint}/statuses?per_page=1") or []
        latest_status = statuses[0] if statuses else None

        if not latest_status or latest_status.get("state") != "inactive":
            gh_api(
                f"{endpoint}/statuses",
                "--method", "POST",
                "-f", "state=inactive",
            )

        delete(endpoint)
        removed += 1

    return removed


def main() -> None:
    removed_runs = cleanup_runs()
    removed_caches = cleanup_caches()
    removed_deployments = cleanup_deployments()
    print(
        f"Cleanup completed: removed {removed_runs} old workflow runs, "
        f"{removed_caches} caches, and {removed_deployments} old Pages deployments."
    )


if __name__ == "__main__":
    main()
