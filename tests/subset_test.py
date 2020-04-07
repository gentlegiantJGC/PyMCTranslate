import unittest
import itertools
from typing import Generator, Tuple, Any

from amulet.api.block import Block
import amulet_nbt
import PyMCTranslate
from PyMCTranslate.py3 import log as pymct_log


class SubSetTest(unittest.TestCase):
    def test_sub_set(self):
        translator = PyMCTranslate.new_translation_manager()
        universal_version = translator.get_version('universal', (1, 0, 0))
        for platform in translator.platforms():
            for version_number in translator.version_numbers(platform):
                version = translator.get_version(platform, version_number)
                blocks = version.block
                for force_blockstate in [False, True] if version.has_abstract_format else [False]:
                    pymct_log.enable_console_log(force_blockstate)
                    print(version, force_blockstate)
                    for namespace in blocks.namespaces(force_blockstate):
                        for base_name in blocks.base_names(namespace, force_blockstate):
                            for block in self._blockstates(
                                version.block.get_specification(namespace, base_name, force_blockstate),
                                namespace,
                                base_name
                            ):
                                universal_obj = version.block.to_universal(block, force_blockstate=force_blockstate)[0]
                                if isinstance(universal_obj, Block):
                                    if universal_obj.namespace == 'universal_minecraft':
                                        self._is_sub_set(
                                            universal_obj,
                                            universal_version.block.get_specification(universal_obj.namespace, universal_obj.base_name),
                                            (version, force_blockstate)
                                        )

    def _is_sub_set(self, obj: Block, spec: dict, info: Tuple[Any, ...]):
        spec_properties = spec.get('properties', {})
        for prop_name, prop_value in obj.properties.items():
            self.assertIn(prop_name, spec_properties, (*info, obj))
            self.assertIn(prop_value.to_snbt(), spec_properties[prop_name], (prop_name, *info, obj))

    @staticmethod
    def _blockstates(specification: dict, namespace_str: str, base_name: str) -> Generator[Block, None, None]:
        properties = specification.get('properties', {})
        if properties:
            keys, values = zip(*properties.items())
        else:
            keys, values = (), ()
        values = tuple([amulet_nbt.from_snbt(val) for val in prop] for prop in values)

        for spec_ in itertools.product(*values):
            spec = dict(zip(keys, spec_))
            yield Block(namespace=namespace_str, base_name=base_name, properties=spec)


if __name__ == '__main__':
    unittest.main()