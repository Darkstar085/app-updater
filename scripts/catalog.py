#!/usr/bin/env python3
"""Build the platform-aware app catalog for GitHub Pages."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from release_config import PLATFORM_RELEASES, platform_specs

ROOT = Path(__file__).resolve().parents[1]
APPS_FILE = ROOT / "apps.json"
VERSIONS_FILE = ROOT / "latest-versions.json"
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


def build_catalog(apps: list[dict], versions: dict) -> list[dict]:
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
        for spec in platform_specs(app):
            platform = spec["platform"]
            entry = versions.get(app["name"], {}).get(platform, {})
            version = entry.get("version", "Unknown")
            tag = PLATFORM_RELEASES[platform]["tag"]
            downloads = [
                {
                    "name": filename,
                    "url": (
                        "https://github.com/Darkstar085/app-updater/"
                        f"releases/download/{tag}/{quote(filename)}"
                    ),
                }
                for filename in entry.get("assets", [])
            ]
            catalog.append({
                "name": app["name"],
                "description": app.get("description", ""),
                "emoji": app.get("emoji", "📦"),
                "category": CATEGORIES.get(app["name"], "Utilities"),
                "platform": platform,
                "version": version,
                "repository": repo,
                "downloads": downloads,
            })
    return sorted(catalog, key=lambda item: (item["name"].casefold(), item["platform"]))


def main() -> None:
    apps = json.loads(APPS_FILE.read_text(encoding="utf-8"))
    apps = [app for app in apps if app.get("enabled", True)]
    versions = json.loads(VERSIONS_FILE.read_text(encoding="utf-8")) if VERSIONS_FILE.exists() else {}
    catalog = build_catalog(apps, versions)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)} with {len(catalog)} app/platform entries")


if __name__ == "__main__":
    main()
