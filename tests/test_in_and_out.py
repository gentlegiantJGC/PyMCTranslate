import logging
import os
from unittest import TestCase
import itertools
from typing import Any, List

import PyMCTranslate
import amulet_nbt as nbt
from PyMCTranslate.py3.api import Block
from is_invalid_state import is_invalid_state

log = logging.getLogger("PyMCTranslate")

print_extra_needed = False


def in_and_out(
    platform_name: str,
    version_number: Any,
    version: PyMCTranslate.Version,
    input_blockstate: Block,
) -> List[str]:
    msg = []
    if is_invalid_state(platform_name, version_number, version, input_blockstate):
        return msg
    # blockstate to universal
    try:
        universal_output, extra_output, extra_needed = version.block.to_universal(
            input_blockstate, force_blockstate=True
        )
    except:
        msg += [
            "=" * 150,
            f"error to universal {platform_name} {version_number}",
            f"Blockstate input: {input_blockstate}",
        ]
        for e in msg:
            log.error(e)
        return msg
    if extra_needed or extra_output is not None:
        if print_extra_needed:
            msg.append(
                f"skipping {platform_name} {version_number} {input_blockstate}. Needs more data"
            )
            log.error(msg[-1])
        return msg

    if not universal_output.namespace.startswith("universal_"):
        msg += [
            "=" * 150,
            f'Universal is not "universal_" {platform_name} {version_number}',
            f"Blockstate input: {input_blockstate}",
            f"Universal output: {universal_output}",
        ]

    if version.has_abstract_format:
        # universal to numerical
        try:
            numerical_output, extra_output, extra_needed = version.block.from_universal(
                universal_output
            )
        except:
            msg += [
                "=" * 150,
                f"error from universal to numerical {platform_name} {version_number}",
                f"Blockstate input: {input_blockstate}",
                f"Universal output: {universal_output}",
            ]
            for e in msg:
                log.error(e)
            return msg
        if extra_needed or extra_output is not None:
            if print_extra_needed:
                msg.append(
                    f"skipping {platform_name} {version_number} {input_blockstate}. Needs more data"
                )
                log.error(msg[-1])
            return msg

        # numerical to universal
        try:
            universal_output2, extra_output, extra_needed = version.block.to_universal(
                numerical_output
            )
        except:
            msg += [
                "=" * 150,
                f"error from universal to blockstate {platform_name} {version_number}",
                f"Blockstate input: {input_blockstate}",
                f"Universal output: {universal_output}",
                f"Numerical output: {numerical_output}",
            ]
            for e in msg:
                log.error(e)
            return msg
        if extra_needed or extra_output is not None:
            if print_extra_needed:
                msg.append(
                    f"skipping {platform_name} {version_number} {input_blockstate}. Needs more data"
                )
                log.error(msg[-1])
            return msg
    else:
        numerical_output = None
        universal_output2 = universal_output

    if not universal_output2.namespace.startswith("universal_"):
        msg += [
            "=" * 150,
            f"Universal is not universal_ {platform_name} {version_number}",
            f"Blockstate input: {input_blockstate}",
            f"Universal output: {universal_output}",
            f"Numerical output: {numerical_output}",
            f"Universal output 2: {universal_output2}",
        ]
        for e in msg:
            log.error(e)

    # universal to blockstate
    try:
        back_out, extra_output, extra_needed = version.block.from_universal(
            universal_output2, force_blockstate=True
        )
    except:
        msg += [
            "=" * 150,
            f"error from universal {platform_name} {version_number}",
            f"Blockstate input: {input_blockstate}",
            f"Universal output: {universal_output}",
            f"Numerical output: {numerical_output}",
            f"Universal output 2: {universal_output2}",
        ]
        for e in msg:
            log.error(e)
        return msg
    if str(input_blockstate) != str(back_out):
        if version.platform == "java" and version.version_number[1] >= 13:
            props1 = input_blockstate.properties
            props2 = back_out.properties
            if "waterlogged" in props1:
                del props1["waterlogged"]
            if "waterlogged" in props2:
                del props2["waterlogged"]
            if str(
                Block(
                    namespace=input_blockstate.namespace,
                    base_name=input_blockstate.base_name,
                    properties=props1,
                )
            ) == str(
                Block(
                    namespace=back_out.namespace,
                    base_name=back_out.base_name,
                    properties=props2,
                )
            ):
                return msg

        msg += [
            "=" * 150,
            f"Conversion error: {input_blockstate} != {back_out} {platform_name} {version_number}",
            f"Universal output: {universal_output}",
            f"Numerical output: {numerical_output}",
            f"Universal output 2: {universal_output2}",
            f"Blockstate: {back_out}",
        ]
        for e in msg:
            log.error(e)
        return msg
    return msg


def get_blockstates(version, namespace_str, base_name):
    block_specification = version.block.get_specification(
        namespace_str, base_name, True
    )
    properties = block_specification.get("properties", {})
    if len(properties) > 0:
        keys, values = zip(*properties.items())
    else:
        keys, values = (), ()
    values = tuple([nbt.from_snbt(val) for val in prop] for prop in values)

    for spec_ in itertools.product(*values):
        spec = dict(zip(keys, spec_))
        yield Block(namespace=namespace_str, base_name=base_name, properties=spec)


class InOutTestCase(TestCase):
    def test_in_and_out(self) -> None:
        translations = PyMCTranslate.new_translation_manager()

        for platform_name in translations.platforms():
            for version_number in translations.version_numbers(platform_name):
                with self.subTest(platform_name=platform_name, version_number=version_number):
                    errors = []
                    version = translations.get_version(platform_name, version_number)
                    log.info(f"Checking version {platform_name} {version_number}")

                    for namespace_str in version.block.namespaces(True):
                        for base_name in version.block.base_names(namespace_str, True):
                            for input_blockstate in get_blockstates(
                                version, namespace_str, base_name
                            ):
                                errors += in_and_out(
                                    platform_name,
                                    version_number,
                                    version,
                                    input_blockstate,
                                )
                    errors_path = os.path.join(
                        "in_out_test", f"{platform_name}_{version_number}.txt"
                    )
                    if errors:
                        with open(
                            errors_path,
                            "w",
                        ) as errors_file:
                            errors_file.write("\n".join(errors) + "\n")
                    elif os.path.isfile(errors_path):
                        os.remove(errors_path)
                    self.assertEqual([], errors)
