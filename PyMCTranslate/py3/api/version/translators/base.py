from typing import List, Tuple, Union, Callable, TYPE_CHECKING
import copy

from PyMCTranslate.py3.meta import minified, json_atlas
from PyMCTranslate.py3.api import Block, BlockEntity, Entity
from PyMCTranslate.py3.log import log
from PyMCTranslate.py3.api.version.translate import translate

if TYPE_CHECKING:
    from ..version import Version

BlockCoordinates = Tuple[int, int, int]


class BaseTranslator:
    def __init__(
        self,
        parent_version: "Version",
        universal_format: "Version",
        database: dict,
        mode: str,
    ):
        self._parent_version = parent_version
        self._universal_format = universal_format
        self._database = database
        self._mode = mode

    def _format_key(self, force_blockstate):
        return (
            "numerical"
            if not force_blockstate and self._parent_version.has_abstract_format
            else "blockstate"
        )

    def _translate(
        self,
        object_input: Union[Block, Entity],
        input_spec: dict,
        mappings: List[dict],
        output_version: "Version",
        force_blockstate: bool,
        translation_direction: str,
        get_block_callback: Callable[
            [Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]
        ] = None,
        extra_input: BlockEntity = None,
        block_location: BlockCoordinates = (0, 0, 0),
        pre_populate_defaults: bool = True,
    ) -> Union[
        Tuple[Block, None, bool, bool],
        Tuple[Block, BlockEntity, bool, bool],
        Tuple[Entity, None, bool, bool],
    ]:
        try:
            output, extra_output, extra_needed, cacheable = translate(
                object_input,
                input_spec,
                mappings,
                output_version,
                force_blockstate,
                get_block_callback,
                extra_input,
                pre_populate_defaults,
                block_location,
            )
            return output, extra_output, extra_needed, cacheable
        except Exception as e:
            log.error(
                f"Error converting {self._mode} {object_input} {translation_direction} in {self._parent_version}."
            )
            # traceback.print_stack()
            log.error(f'Error and traceback from the above "{e}"', exc_info=True)
            return object_input, extra_input, True, False

    def namespaces(self, force_blockstate: bool = False) -> List[str]:
        """
        A list of all the valid namespaces for this object type.

        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A list of all the namespaces
        """
        return list(
            self._database.get(self._format_key(force_blockstate), {})
            .get("specification", {})
            .keys()
        )

    def base_names(self, namespace: str, force_blockstate: bool = False) -> List[str]:
        """
        A list of all the valid base names present in a given namespace for this object type.

        :param namespace: A namespace string as found using the ``namespaces`` method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A list of base names
        """
        return list(
            self._database.get(self._format_key(force_blockstate), {})
            .get("specification", {}).get(namespace, {})
            .keys()
        )

    @staticmethod
    def _get_data(data):
        if minified:
            return copy.deepcopy(json_atlas[data])
        else:
            return copy.deepcopy(data)

    def get_specification(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> dict:
        """
        Get the specification file for the requested object.

        :param namespace: A namespace string as found using the ``namespaces`` method
        :param base_name: A base name string as found using the ``base_name`` method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A dictionary containing the specification for the object
        """
        try:
            data = self._database.get(self._format_key(force_blockstate), {}).get(
                "specification", {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(
                f"Specification for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}"
            )

    def get_mapping_to_universal(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> List[dict]:
        """
        Get the mapping file for the requested object from this version format to the universal format.

        :param namespace: A namespace string as found using the ``namespaces`` method
        :param base_name: A base name string as found using the ``base_name`` method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A list of mapping functions to apply to the object
        """
        try:
            data = self._database.get(self._format_key(force_blockstate), {}).get(
                "to_universal", {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(
                f"Mapping to universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}"
            )

    def get_mapping_from_universal(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> List[dict]:
        """
        Get the mapping file for the requested object from the universal format to this version format.

        :param namespace: A namespace string as found using the ``namespaces`` method
        :param base_name: A base name string as found using the ``base_name`` method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A list of mapping functions to apply to the object
        """
        try:
            data = self._database.get(self._format_key(force_blockstate), {}).get(
                "from_universal", {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(
                f"Mapping from universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}"
            )

    def to_universal(self, *args, **kwargs):
        raise NotImplementedError

    def from_universal(self, *args, **kwargs):
        raise NotImplementedError
