#!/usr/bin/env python3
"""Discover upstream app assets and publish cumulative platform releases."""

from __future__ import annotations

import fnmatch
import glob
import html
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from release_config import PLATFORM_RELEASES, platform_specs

ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = ROOT / "dl"
APPS_FILE = ROOT / "apps.json"
VERSIONS_FILE = ROOT / "latest-versions.json"
CAPTIONS_FILE = ROOT / "captions.txt"
UPDATES_FILE = ROOT / "updated-apps.txt"
REPOSITORY = os.getenv("GITHUB_REPOSITORY", "Darkstar085/app-updater")
VERSION_RE = re.compile(r"(?<!\d)v?(\d+(?:\.\d+){1,3})(?!\d)", re.I)
PLATFORM_ORDER = ("Windows", "Android", "iOS", "macOS", "Linux")


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, text=True, capture_output=True)


def gh_api(endpoint: str):
    result = run(["gh", "api", endpoint])
    return json.loads(result.stdout)


def load_tracks() -> list[dict]:
    apps = json.loads(APPS_FILE.read_text(encoding="utf-8"))
    tracks = []
    names = set()
    for app in apps:
        if not app.get("enabled", True):
            continue
        name, repo = app.get("name"), app.get("repo")
        if not isinstance(name, str) or not name.strip() or not isinstance(repo, str) or "/" not in repo:
            raise ValueError(f"Invalid app entry: {app!r}")
        if name in names:
            raise ValueError(f"Duplicate app name: {name}")
        names.add(name)
        for spec in platform_specs(app):
            tracks.append({
                "name": name,
                "repo": repo,
                "platform": spec["platform"],
                "patterns": spec["patterns"],
                "description": app.get("description", ""),
                "emoji": app.get("emoji", "📦"),
                "rename": app.get("rename"),
            })
    return tracks


TRACKS = load_tracks()


def release_tag(platform: str) -> str:
    return PLATFORM_RELEASES[platform]["tag"]


def latest_release(repo: str, patterns: list[str]) -> dict:
    """Find the newest stable release containing one of the requested assets."""
    releases = gh_api(f"repos/{repo}/releases?per_page=30")
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        if any(
            fnmatch.fnmatch(asset.get("name", ""), pattern)
            for asset in release.get("assets", [])
            for pattern in patterns
        ):
            return release
    raise RuntimeError(f"no release assets matching {patterns!r} found in {repo}")


def asset_version(release: dict, assets: list[dict]) -> str | None:
    versions = {
        match.group(1)
        for asset in assets
        if (match := VERSION_RE.search(asset.get("name", "")))
    }
    if len(versions) == 1:
        return versions.pop()
    tag = release.get("tag_name", "")
    match = VERSION_RE.search(tag)
    return match.group(1) if match else None


def matching_asset_metadata(release: dict, patterns: list[str]) -> list[dict]:
    return [
        asset for asset in release.get("assets", [])
        if any(fnmatch.fnmatch(asset.get("name", ""), pattern) for pattern in patterns)
    ]


def download_track(track: dict) -> tuple[dict, Path] | None:
    name, repo, patterns = track["name"], track["repo"], track["patterns"]
    destination = DOWNLOAD_DIR / track["platform"].lower() / name
    shutil.rmtree(destination, ignore_errors=True)
    try:
        release = latest_release(repo, patterns)
        matched = matching_asset_metadata(release, patterns)
        if not matched:
            return None
        destination.mkdir(parents=True, exist_ok=True)
        downloaded = set()
        for pattern in patterns:
            if not any(fnmatch.fnmatch(asset["name"], pattern) for asset in matched):
                continue
            run([
                "gh", "release", "download", release["tag_name"],
                "--repo", repo, "--pattern", pattern,
                "--dir", str(destination), "--clobber",
            ])
            downloaded.update(
                asset["name"] for asset in matched
                if fnmatch.fnmatch(asset["name"], pattern)
            )
        files = [destination / filename for filename in sorted(downloaded)]
        files = [path for path in files if path.is_file()]
        if not files:
            print(f"⚠️ {name} ({track['platform']}): no matching assets downloaded")
            shutil.rmtree(destination, ignore_errors=True)
            return None
        return ({"release": release, "assets": matched, "files": files}, destination)
    except Exception as exc:
        print(f"⚠️ {name} ({track['platform']}): could not fetch release: {exc}")
        shutil.rmtree(destination, ignore_errors=True)
        return None


def apk_metadata(path: Path) -> tuple[str | None, str | None]:
    result = run(["aapt", "dump", "badging", str(path)], check=False)
    if result.returncode != 0:
        return None, None
    package = re.search(r"package: name='([^']+)'", result.stdout)
    version = re.search(r"versionName='([^']+)'", result.stdout)
    return (package.group(1) if package else None, version.group(1) if version else None)


def asset_priority(path: Path) -> tuple[int, int, int, str]:
    name = path.name.lower()
    return (
        0 if "universal" in name else 1 if "arm64-v8a" in name else 2,
        0 if "release" in name else 1 if "stable" in name else 2,
        0 if "foss" not in name else 1,
        name,
    )


def choose_apk(files: list[Path], app: str) -> tuple[Path, str] | None:
    candidates = [path for path in files if path.suffix.lower() == ".apk"]
    inspected = []
    for candidate in candidates:
        _package, version = apk_metadata(candidate)
        if version:
            inspected.append((candidate, version))
    if not inspected:
        print(f"⚠️ {app}: could not read Android APK version; skipping")
        return None
    versions = {version for _path, version in inspected}
    if len(versions) > 1:
        universal = [item for item in inspected if "universal" in item[0].name.lower()]
        arm64 = [item for item in inspected if "arm64-v8a" in item[0].name.lower()]
        preferred = universal or arm64 or inspected
        preferred_versions = {version for _path, version in preferred}
        if len(preferred_versions) > 1:
            details = ", ".join(f"{path.name}: {version}" for path, version in preferred)
            print(f"⚠️ {app}: multiple APK versions remain; skipping: {details}")
            return None
        inspected = preferred
    return sorted(inspected, key=lambda item: asset_priority(item[0]))[0]


def old_track_state(old: dict, track: dict) -> dict:
    return old.get(track["name"], {}).get(track["platform"], {})


def process_track(track: dict, old: dict, force: bool) -> dict | None:
    downloaded = download_track(track)
    if not downloaded:
        return None
    info, _directory = downloaded
    release, source_files = info["release"], info["files"]
    version = asset_version(release, info["assets"])
    if track["platform"] == "Android":
        chosen = choose_apk(source_files, track["name"])
        if not chosen:
            return None
        source, apk_version = chosen
        version = apk_version or version
        selected = [source]
    else:
        selected = source_files

    if not version:
        print(f"⚠️ {track['name']} ({track['platform']}): no version found; skipping")
        return None

    previous = old_track_state(old, track)
    final_paths = []
    for source in selected:
        if track["platform"] == "Android":
            filename = f"{track['name']}_v{version}.apk"
        else:
            filename = f"{track['name']}_v{version}_{source.name}"
        final = ROOT / filename
        if source.resolve() != final.resolve():
            shutil.copy2(source, final)
        final_paths.append(final)

    asset_names = [path.name for path in final_paths]
    if not force and previous.get("version") == version and previous.get("assets") == asset_names:
        for path in final_paths:
            path.unlink(missing_ok=True)
        print(f"{track['name']} ({track['platform']}) unchanged (v{version})")
        return None

    print(f"Will update {track['name']} ({track['platform']}) → v{version}")
    return {"track": track, "version": version, "files": final_paths, "assets": asset_names}


def write_state(state: dict) -> None:
    VERSIONS_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def grouped_platform_versions(
    state: dict, platform_filter: str | None = None
) -> dict[str, list[str]]:
    """Group platforms sharing a version, optionally for one release channel."""
    grouped = {}
    for app, platforms in state.items():
        versions = {}
        ordered = [name for name in PLATFORM_ORDER if name in platforms]
        ordered.extend(name for name in platforms if name not in PLATFORM_ORDER)
        for platform in ordered:
            version = platforms[platform].get("version")
            if version and (platform_filter is None or platform == platform_filter):
                versions.setdefault(version, []).append(platform)
        if versions:
            grouped[app] = [
                f"{', '.join(names)} v{version}"
                for version, names in versions.items()
            ]
    return grouped


def generate_metadata(updates: list[dict], old: dict) -> None:
    changed = {}
    captions = []
    for update in updates:
        track, version = update["track"], update["version"]
        name, platform = track["name"], track["platform"]
        previous = old_track_state(old, track).get("version")
        changed.setdefault(name, {})[platform] = {"version": version}
        transition = f"🚀 Version: {previous} → {version}" if previous else f"🆕 Version: {version}"
        for path in update["files"]:
            filename = html.escape(path.name)
            caption = (
                f"📦 <b>File name</b> – {filename}\n"
                f"    {track['emoji']} {html.escape(track['description'])} ({platform})\n"
                f"{transition}\n\n"
                f"Changelog: <a href='https://github.com/{track['repo']}/releases/latest'>Open</a>\n"
                f"    ----"
            )
            captions.append(caption)
    grouped = grouped_platform_versions(changed)
    lines = [
        f"{name}: " + " | ".join(grouped[name])
        for name in sorted(grouped, key=str.casefold)
    ]
    UPDATES_FILE.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    CAPTIONS_FILE.write_text("\n".join(captions) + ("\n" if captions else ""), encoding="utf-8")

def publish(updates: list[dict], old: dict, state: dict, existing_releases: dict[str, bool]) -> None:
    by_platform = {}
    for update in updates:
        by_platform.setdefault(update["track"]["platform"], []).append(update)

    for platform, config in PLATFORM_RELEASES.items():
        tag = release_tag(platform)
        platform_updates = by_platform.get(platform, [])
        if not existing_releases.get(platform, False):
            if not platform_updates:
                continue
            run([
                "gh", "release", "create", tag,
                "--title", config["title"],
                "--notes", f"Latest published versions for {platform}.",
            ])

        if platform_updates:
            paths = [str(path) for update in platform_updates for path in update["files"]]
            run(["gh", "release", "upload", tag, *paths, "--clobber"])

            release = gh_api(f"repos/{REPOSITORY}/releases/tags/{tag}")
            for update in platform_updates:
                track = update["track"]
                previous_names = old_track_state(old, track).get("assets", [])
                current_names = set(update["assets"])
                for asset in release.get("assets", []):
                    if asset.get("name") in previous_names and asset.get("name") not in current_names:
                        run([
                            "gh", "api", "--method", "DELETE",
                            f"repos/{REPOSITORY}/releases/assets/{asset['id']}",
                        ])

        notes = ["Latest published versions:", ""]
        grouped = grouped_platform_versions(state, platform_filter=platform)
        for name in sorted(grouped, key=str.casefold):
            notes.append(f"- {name} | " + " | ".join(grouped[name]))
        run(["gh", "release", "edit", tag, "--title", config["title"], "--notes", "\n".join(notes)])
        print(f"Updated {platform} release ({tag})")


def main() -> None:
    print(f"Build started: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    old = json.loads(VERSIONS_FILE.read_text(encoding="utf-8")) if VERSIONS_FILE.exists() else {}

    existing_releases = {}
    for platform, config in PLATFORM_RELEASES.items():
        check = run(["gh", "release", "view", config["tag"]], check=False)
        existing_releases[platform] = check.returncode == 0

    updates = []
    state = json.loads(json.dumps(old))
    for track in TRACKS:
        platform_exists = existing_releases[track["platform"]]
        update = process_track(track, old, force=not platform_exists)
        if not update:
            continue
        state.setdefault(track["name"], {})[track["platform"]] = {
            "version": update["version"],
            "assets": update["assets"],
        }
        updates.append(update)

    write_state(state)
    generate_metadata(updates, old)
    publish(updates, old, state, existing_releases)
    print(f"Build completed: {len(updates)} app/platform update(s)")


if __name__ == "__main__":
    main()
