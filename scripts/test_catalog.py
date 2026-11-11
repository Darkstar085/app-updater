import unittest

from catalog import build_catalog


class CatalogTests(unittest.TestCase):
    def test_catalog_links_to_the_cumulative_release_asset(self):
        apps = [{"name": "Demo", "repo": "owner/demo", "pattern": "*.apk"}]
        result = build_catalog(apps, {"Demo": "1.2.3"})[0]
        self.assertEqual(result["version"], "1.2.3")
        self.assertEqual(result["platform"], "Android")
        self.assertEqual(result["download_url"], "https://github.com/Darkstar085/app-updater/releases/download/prebuilts/Demo_v1.2.3.apk")

    def test_apps_without_a_published_version_have_no_download_link(self):
        apps = [{"name": "Demo", "repo": "owner/demo", "pattern": "*.apk"}]
        result = build_catalog(apps, {})[0]
        self.assertEqual(result["download_url"], "")

    def test_duplicate_names_are_rejected(self):
        apps = [{"name": "Demo", "repo": "owner/demo"}, {"name": "Demo", "repo": "owner/other"}]
        with self.assertRaises(ValueError):
            build_catalog(apps, {})


if __name__ == "__main__":
    unittest.main()
