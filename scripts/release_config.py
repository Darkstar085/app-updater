"""Shared app-to-platform release configuration."""

from __future__ import annotations

from pathlib import PurePosixPath

PLATFORM_RELEASES = {
    "Android": {"tag": "android", "title": "Android App Updates"},
    "Windows": {"tag": "windows", "title": "Windows App Updates"},
    "Linux": {"tag": "linux", "title": "Linux App Updates"},
    "macOS": {"tag": "macos", "title": "macOS App Updates"},
    "iOS": {"tag": "ios", "title": "iOS App Updates"},
}

EXTENSION_PLATFORMS = {
    ".apk": "Android",
    ".exe": "Windows",
    ".msi": "Windows",
    ".msix": "Windows",
    ".appimage": "Linux",
    ".deb": "Linux",
    ".rpm": "Linux",
    ".dmg": "macOS",
    ".ipa": "iOS",
}


def platform_specs(app: dict) -> list[dict]:
    """Return validated platform/pattern groups for one configured app."""
    pattern = app.get("pattern", "")
    platform = app.get("platform") or EXTENSION_PLATFORMS.get(
        PurePosixPath(pattern).suffix.lower()
    )
    if platform not in PLATFORM_RELEASES:
        raise ValueError(f"Unknown platform for {app.get('name', 'app')}: {platform!r}")

    primary = app.get("patterns") or [pattern]
    groups = [{"platform": platform, "patterns": primary}, *app.get("additional_platforms", [])]
    seen = set()
    normalized = []
    for group in groups:
        name = group.get("platform")
        patterns = group.get("patterns")
        if name not in PLATFORM_RELEASES:
            raise ValueError(f"Unknown platform for {app.get('name', 'app')}: {name!r}")
        if name in seen:
            raise ValueError(f"Duplicate {name} platform for {app.get('name', 'app')}")
        if not isinstance(patterns, list) or not patterns or any(
            not isinstance(value, str) or not value.strip() for value in patterns
        ):
            raise ValueError(f"{app.get('name', 'app')} has invalid patterns for {name}")
        seen.add(name)
        normalized.append({"platform": name, "patterns": patterns})
    return normalized
