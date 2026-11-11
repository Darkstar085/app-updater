# Android App Updater

An automated release aggregation and distribution system for Android applications and other configured software.

Android App Updater monitors selected GitHub repositories, detects new releases, downloads the required APK/EXE assets, and publishes updated applications through a centralized GitHub Release and Telegram channel. 🚀

## ✨ Features

- **Automatic release tracking**
  - Monitors configured upstream GitHub repositories
  - Detects newly available versions
- **Smart asset handling**
  - Matches APK/EXE release assets
  - Supports repositories with non-standard asset names
  - Applies explicit rename rules where required
- **Version tracking**
  - Compares upstream versions with previously published versions
  - Republishes only applications that have changed
- **Centralized release**
  - Maintains one cumulative GitHub Release containing the latest APK/EXE for every successfully tracked app
  - Replaces only an app's previous asset when that app is updated; unchanged app assets remain
  - Uses a consistent naming format: `AppName_vVERSION.apk` or `AppName_vVERSION.exe`
- **Telegram notifications**
  - Sends an update list only when apps change
  - Includes the GitHub Pages download catalog link; APK/EXE files are not uploaded to Telegram

## 🔄 Update Pipeline

```text
              Upstream GitHub Releases
                        │
                        ▼
                 Release Discovery
                        │
                        ▼
                   Asset Download
                        │
                        ▼
                 Asset Processing
                        │
                        ▼
                Version Comparison
                        │
                 ┌──────┴──────┐
                 │             │
              Unchanged      Changed
                 │             │
                Skip           ▼
                       Prepare Release
                              │
                              ▼
                         Deploy Pages
                              │
                              ▼
                       Telegram Notice
```

## 📱 Supported Applications

The updater currently manages a collection of applications, including:

- ABDownloadManager
- Acode
- Aegis
- BreezyWeather
- Cromite
- DuckDuckGo
- Florisboard
- Fossify applications
- ImageToolbox
- LibreTube
- LocalSend
- Magisk
- Shizuku
- Termux
- Thunderbird Android
- YTDLnis
- Morphe applications
- And more

The complete application configuration is maintained in [`apps.json`](apps.json).

## 🌐 Web Dashboard

A searchable GitHub Pages catalog lists configured applications, their tracked versions, categories, platforms, and centralized download links. It is deployed automatically after every successful weekly or manual build.

Enable GitHub Pages with **GitHub Actions** as the build and deployment source in repository Settings → Pages. The dashboard URL is `https://darkstar085.github.io/android-app-updater/`.

## 📦 Releases

The repository maintains one release with the fixed tag `prebuilts`. Every run adds or replaces APK/EXE assets for changed apps while preserving the latest assets for unchanged apps. The release notes list the latest published version of every tracked app.

## ⏰ Automation

- **Build & Release:** Every Sunday at **10:00 AM Asia/Kolkata**, or manually. It updates the cumulative release, deploys Pages, then notifies Telegram.
- **Cleanup:** Monthly on the 1st at **10:00 AM Asia/Kolkata**, or manually. It removes older Actions runs, caches, and inactive Pages deployments. The latest Pages deployment is preserved; releases and their assets are untouched.

## 📲 Telegram

When one or more apps change, the workflow sends a text-only update list to the configured Telegram channel after the Pages deployment succeeds. The message links to the Pages catalog for downloads. No app files are uploaded to Telegram.

## ⚙️ Reliability

- Handles special asset naming and explicit rename cases
- Continues when an upstream repository has no matching asset
- Tracks versions to avoid republishing unchanged applications
- Retries transient Telegram notification request failures
- Uses concurrency controls to prevent overlapping build or delivery runs

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

Third-party applications and their distributed APK/EXE files remain subject to their respective licenses and copyright ownership.
