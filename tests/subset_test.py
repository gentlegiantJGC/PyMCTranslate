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
        universal_blocks = universal_version.block
        for platform in translator.platforms():
            for version_number in translator.version_numbers(platform):
                version = translator.get_version(platform, version_number)
                blocks = version.block
                for force_blockstate in [False, True] if version.has_abstract_format else [False]:
                    pymct_log.enable_console_log(force_blockstate)
                    print('To Universal', version, force_blockstate)
                    for namespace in blocks.namespaces(force_blockstate):
                        for base_name in blocks.base_names(namespace, force_blockstate):
                            for block in self._blockstates(
                                blocks.get_specification(namespace, base_name, force_blockstate),
                                namespace,
                                base_name
                            ):
                                universal_obj = blocks.to_universal(block, force_blockstate=force_blockstate)[0]
                                if isinstance(universal_obj, Block):
                                    if force_blockstate:
                                        self.assertEqual(universal_obj.namespace, 'universal_minecraft', (version, force_blockstate, block, universal_obj))
                                    if universal_obj.namespace == 'universal_minecraft':
                                        self._is_sub_set(
                                            universal_obj,
                                            universal_version.block.get_specification(universal_obj.namespace, universal_obj.base_name),
                                            (version, force_blockstate, block)
                                        )

                    print('From Universal', version, force_blockstate)
                    for namespace in universal_blocks.namespaces():
                        for base_name in universal_blocks.base_names(namespace):
                            for block in self._blockstates(
                                universal_blocks.get_specification(namespace, base_name),
                                namespace,
                                base_name
                            ):
                                version_obj = blocks.from_universal(block, force_blockstate=force_blockstate)[0]
                                if isinstance(version_obj, Block):
                                    self.assertEqual(version_obj.namespace, 'minecraft', (version, force_blockstate, block, version_obj))
                                    self._is_sub_set(
                                        version_obj,
                                        blocks.get_specification(version_obj.namespace, version_obj.base_name, force_blockstate=force_blockstate),
                                        (version, force_blockstate, block)
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