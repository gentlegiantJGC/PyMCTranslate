import unittest
import re
import PyMCTranslate

ResourceID = re.compile(r"[a-z1-9_]*:[a-z1-9_]*")


class SubSetTest(unittest.TestCase):
    def setUp(self) -> None:
        self._translator = PyMCTranslate.new_translation_manager()

    def test_biomes(self):
        universal_biomes = self._translator.universal_format.biome.biome_ids
        for biome in universal_biomes:
            # validate the universal biomes
            self.assertTrue(biome.startswith("universal_minecraft:"))
            self.assertIsNotNone(
                ResourceID.fullmatch(biome),
                f"Biome {biome} does not match the valid character set. Universal",
            )
        universal_biomes_set = set(universal_biomes)

        for platform in self._translator.platforms():
            if platform == "universal":
                continue
            for version_number in self._translator.version_numbers(platform):
                version = self._translator.get_version(platform, version_number)
                universal_biomes_found = set()
                for biome in version.biome.biome_ids:
                    # check that the character set of the biome is valid
                    self.assertIsNotNone(
                        ResourceID.fullmatch(biome),
                        f"Biome {biome} does not match the valid character set. {platform} {version_number}",
                    )
                    # convert the biome to the universal format
                    universal_biome = version.biome.to_universal(biome)
                    # check that the universal biome has the correct namespace
                    self.assertTrue(
                        universal_biome.startswith("universal_minecraft:"),
                        msg=f"Universal biome does not start with universal_minecraft:  {universal_biome} {platform} {version_number}",
                    )
                    # check that the universal biome is a known universal biome
                    self.assertIn(
                        universal_biome,
                        universal_biomes_set,
                        msg=f"Biome {universal_biome} is not a registered universal biome. {platform} {version_number}",
                    )
                    # store it so we don't need to translate it again later
                    universal_biomes_found.add(universal_biome)
                    # translate it back to the version format
                    version_biome = version.biome.from_universal(universal_biome)
                    # check that it is the same as the input
                    self.assertEqual(
                        biome,
                        version_biome,
                        f"Biome does not equal the input when converted back. {platform} {version_number}",
                    )

                # check that all universal biomes can be converted to a valid biome in this version
                for universal_biome in universal_biomes:
                    version_biome = version.biome.from_universal(universal_biome)
                    self.assertTrue(
                        version_biome.startswith("minecraft:"),
                        msg=f"No translation from universal for biome {universal_biome} in {platform} {version_number}",
                    )


if __name__ == "__main__":
    unittest.main()
