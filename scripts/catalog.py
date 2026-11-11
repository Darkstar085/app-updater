#!/usr/bin/env python3
"""Build the static app catalog consumed by the GitHub Pages dashboard."""

from __future__ import annotations

import json
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS_FILE = ROOT / "apps.json"
VERSIONS_FILE = ROOT / "latest-apk-versions.txt"
OUTPUT_FILE = ROOT / "site" / "data" / "apps.json"

CATEGORIES = {
    "ABDownloadManager": "Downloads", "Quantum_Download_Manager": "Downloads",
    "Ytdlnis": "Downloads", "LocalSend": "File sharing",
    "Acode": "Development", "CpuInfo": "System", "Magisk": "System",
    "Shizuku": "System", "Termux": "Development", "VisualCodeSpace": "Development",
    "XedEditor": "Development", "Bitwarden": "Security", "Aegis": "Security",
    "DuckDuckGo": "Browsers", "Cromite": "Browsers", "IceravenBrowser": "Browsers",
    "ThunderbirdAndroid": "Communication", "NopeRemote": "Utilities",
    "ConverterNOW": "Utilities", "WeatherMaster": "Weather", "BreezyWeather": "Weather",
    "OrganicMaps": "Maps", "ImageToolbox": "Photos", "ReFra": "Photos",
    "GooglePhotos": "Photos", "Arcticons": "Personalization", "DeltaIcons": "Personalization",
    "Fossify_Calculator": "Utilities", "Fossify_Keyboard": "Utilities",
    "Fossify_MusicPlayer": "Music", "Fossify_Notes": "Productivity",
    "Fossify_VoiceRecorder": "Audio", "Gramophone": "Music", "OuterTune": "Music",
    "Pixelplay": "Music", "PhonographPlus": "Music", "RetroMusicPlayer": "Music",
    "SpotiFLAC": "Music", "SimpMusic": "Music", "Symphony": "Music",
    "LibreTube": "Video", "Morphe_YouTube": "Video", "Morphe_YTMusic": "Music",
}


def read_versions(path: Path = VERSIONS_FILE) -> dict[str, str]:
    versions = {}
    if not path.exists():
        return versions
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        separator = ":" if ":" in line else "=" if "=" in line else None
        if separator:
            name, version = (part.strip() for part in line.split(separator, 1))
            if name and version:
                versions[name] = version
    return versions


def build_catalog(apps: list[dict], versions: dict[str, str]) -> list[dict]:
    names = [app.get("name") for app in apps]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        raise ValueError("Every app must have a non-empty name")
    if len(names) != len(set(names)):
        raise ValueError("apps.json contains duplicate app names")

    catalog = []
    for app in apps:
        repo = app.get("repo", "")
        if "/" not in repo:
            raise ValueError(f"Invalid repository for {app['name']}: {repo!r}")
        pattern = app.get("pattern", "")
        platform = "Windows" if pattern.lower().endswith(".exe") else "Android"
        version = versions.get(app["name"], "Unknown")
        extension = "exe" if platform == "Windows" else "apk"
        filename = f"{app['name']}_v{version}.{extension}"
        catalog.append({
            "name": app["name"],
            "description": app.get("description", ""),
            "emoji": app.get("emoji", "📦"),
            "category": CATEGORIES.get(app["name"], "Utilities"),
            "platform": platform,
            "version": version,
            "repository": repo,
            "download_url": (
                "https://github.com/Darkstar085/app-updater/"
                f"releases/download/prebuilts/{quote(filename)}"
                if version != "Unknown" else ""
            ),
        })
    return sorted(catalog, key=lambda item: item["name"].casefold())


def main() -> None:
    apps = json.loads(APPS_FILE.read_text(encoding="utf-8"))
    apps = [app for app in apps if app.get("enabled", True)]
    catalog = build_catalog(apps, read_versions())
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)} with {len(catalog)} apps")


if __name__ == "__main__":
    main()
