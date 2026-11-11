import unittest

from build import grouped_platform_versions
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

    def test_groups_platforms_with_the_same_version(self):
        grouped = grouped_platform_versions({
            "Demo": {
                "Android": {"version": "1.2.0"},
                "Windows": {"version": "1.2.0"},
                "iOS": {"version": "2.0.0"},
            }
        })
        self.assertEqual(
            grouped["Demo"],
            ["Windows, Android v1.2.0", "iOS v2.0.0"],
        )

    def test_filters_versions_for_the_release_platform(self):
        grouped = grouped_platform_versions({
            "Demo": {
                "Android": {"version": "1.2.0"},
                "Windows": {"version": "1.2.0"},
                "iOS": {"version": "2.0.0"},
            }
        }, platform_filter="iOS")
        self.assertEqual(grouped, {"Demo": ["iOS v2.0.0"]})

    def test_skips_missing_platform_versions(self):
        grouped = grouped_platform_versions({
            "Demo": {"Android": {"version": "1.2.0"}},
            "Empty": {"Windows": {}},
        })
        self.assertEqual(grouped, {"Demo": ["Android v1.2.0"]})


if __name__ == "__main__":
    unittest.main()
