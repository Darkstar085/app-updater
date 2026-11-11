import unittest

from release_config import platform_specs


class PlatformConfigTests(unittest.TestCase):
    def test_infers_default_platform_from_asset_extension(self):
        self.assertEqual(platform_specs({"name": "Demo", "pattern": "*.apk"})[0]["platform"], "Android")
        self.assertEqual(platform_specs({"name": "Demo", "pattern": "*.exe"})[0]["platform"], "Windows")

    def test_keeps_additional_platform_patterns(self):
        result = platform_specs({
            "name": "Demo", "pattern": "*.apk",
            "patterns": ["*.apk", "*.apks"],
            "additional_platforms": [{"platform": "Linux", "patterns": ["*.AppImage", "*.deb"]}],
        })
        self.assertEqual(result[0]["patterns"], ["*.apk", "*.apks"])
        self.assertEqual(result[1], {"platform": "Linux", "patterns": ["*.AppImage", "*.deb"]})

    def test_rejects_duplicate_platforms(self):
        with self.assertRaises(ValueError):
            platform_specs({
                "name": "Demo", "pattern": "*.apk",
                "additional_platforms": [{"platform": "Android", "patterns": ["*.apks"]}],
            })

    def test_rejects_empty_patterns(self):
        with self.assertRaises(ValueError):
            platform_specs({"name": "Demo", "pattern": "*.apk", "additional_platforms": [
                {"platform": "Linux", "patterns": []},
            ]})


if __name__ == "__main__":
    unittest.main()
