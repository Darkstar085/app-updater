import unittest

from catalog import build_catalog


class CatalogTests(unittest.TestCase):
    def test_catalog_creates_platform_rows_and_links_each_asset(self):
        apps = [{
            "name": "Demo", "repo": "owner/demo", "pattern": "*.apk",
            "additional_platforms": [{"platform": "Linux", "patterns": ["*.AppImage", "*.deb"]}],
        }]
        versions = {
            "Demo": {
                "Android": {"version": "1.2.3", "assets": ["Demo_v1.2.3.apk"]},
                "Linux": {"version": "1.2.3", "assets": ["Demo.AppImage", "Demo.deb"]},
            }
        }
        result = build_catalog(apps, versions)
        self.assertEqual([item["platform"] for item in result], ["Android", "Linux"])
        self.assertTrue(result[0]["downloads"][0]["url"].endswith("/android/Demo_v1.2.3.apk"))
        self.assertEqual(len(result[1]["downloads"]), 2)
        self.assertTrue(result[1]["downloads"][0]["url"].endswith("/linux/Demo.AppImage"))

    def test_apps_without_a_published_version_have_no_downloads(self):
        result = build_catalog([{"name": "Demo", "repo": "owner/demo", "pattern": "*.apk"}], {})[0]
        self.assertEqual(result["version"], "Unknown")
        self.assertEqual(result["downloads"], [])

    def test_duplicate_names_are_rejected(self):
        apps = [{"name": "Demo", "repo": "owner/demo"}, {"name": "Demo", "repo": "owner/other"}]
        with self.assertRaises(ValueError):
            build_catalog(apps, {})


if __name__ == "__main__":
    unittest.main()
