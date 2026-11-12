# App Updater

An automated release aggregation and distribution system for Android, Windows, Linux, macOS and iOS applications.

App Updater monitors selected GitHub repositories, detects new releases, downloads configured assets, and publishes the latest builds through separate platform-specific GitHub Releases and a searchable catalog. 🚀

## ✨ Features

- **Automatic release tracking**
  - Monitors configured upstream GitHub repositories
  - Detects new versions and selects matching release assets
- **Multi-platform distribution**
  - Publishes independent Android, Windows, Linux, macOS and iOS release channels
  - Keeps multiple installers and architecture variants for supported apps
  - Updates only changed apps while preserving other apps in each platform release
- **Version tracking**
  - Stores version and asset metadata separately for every app/platform pair
  - Avoids republishing unchanged builds
- **Web catalog**
  - Search and filter tracked apps by category and platform
  - Shows every available installer for each app/platform
- **Telegram notifications**
  - Sends an update list only when tracked apps change
  - Links to the catalog; app files are not uploaded to Telegram

## 🔄 Update Pipeline

```text
              Upstream GitHub Releases
                        │
                        ▼
                 Release Discovery
                        │
                        ▼
              Platform Asset Matching
                        │
                        ▼
                   Downloads
                        │
                        ▼
              Version / Asset Comparison
                        │
                        ▼
             Platform-specific Releases
                        │
                        ▼
                 Deploy Pages
                        │
                        ▼
                Telegram Notice
```

## 🌐 Platform release channels

| Platform | Release |
|---|---|
| Android | [Android App Updates](https://github.com/Darkstar085/app-updater/releases/tag/android) |
| Windows | [Windows App Updates](https://github.com/Darkstar085/app-updater/releases/tag/windows) |
| Linux | [Linux App Updates](https://github.com/Darkstar085/app-updater/releases/tag/linux) |
| macOS | [macOS App Updates](https://github.com/Darkstar085/app-updater/releases/tag/macos) |
| iOS | [iOS App Updates](https://github.com/Darkstar085/app-updater/releases/tag/ios) |

The old `prebuilts` release is retained as a legacy archive. New updates are published to the platform channels above.

## 🌐 Web Dashboard

The searchable GitHub Pages catalog lists app versions, categories, platforms, and all published download links.

Dashboard: https://darkstar085.github.io/app-updater/

GitHub Pages must use **GitHub Actions** as its build and deployment source in repository Settings → Pages.

## ⏰ Automation

- **Build & Release:** Every Sunday at **10:00 AM Asia/Kolkata**, or manually through Actions → Build and Release → Run workflow. It updates platform releases, deploys Pages, then notifies Telegram.
- **Cleanup:** Monthly on the 1st at **10:00 AM Asia/Kolkata**, or manually. It removes older Actions runs, caches, and inactive Pages deployments. Releases and their assets are untouched.

## 📲 Telegram

When one or more app/platform builds change, the workflow sends a text-only update list after the Pages deployment succeeds. Each entry includes the app and platform and links to the catalog.

## ⚙️ Reliability

- Handles special asset naming and explicit rename cases
- Continues when an upstream repository has no matching asset
- Tracks versions and asset names independently for each platform
- Retries transient Telegram notification request failures
- Uses concurrency controls to prevent overlapping build or delivery runs
- Runs the unit tests before each build

## 🔐 Required Secrets

The following GitHub Actions secrets are required:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

GitHub authentication uses the built-in `GITHUB_TOKEN` provided by GitHub Actions.

Keep all credentials and session data private and never commit them directly to the repository.

## 🤝 Requests & Support

Want an application added or found an issue?

- Open an issue in this repository
- Use the project's configured Telegram support channels

## 📜 License

The workflow and automation code in this repository is licensed under the MIT License.

Third-party applications and their distributed installers remain subject to their respective licenses and copyright ownership. The project does not claim ownership of upstream software or distribution rights.
