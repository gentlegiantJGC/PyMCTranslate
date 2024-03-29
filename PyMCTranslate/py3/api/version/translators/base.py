from typing import List, Tuple, Union, Callable, TYPE_CHECKING
import copy
import logging

from PyMCTranslate.py3.meta import minified, json_atlas
from PyMCTranslate.py3.api import Block, BlockEntity, Entity
from PyMCTranslate.py3.api.version.translate import translate

if TYPE_CHECKING:
    from ..version import Version
    from PyMCTranslate import TranslationManager

log = logging.getLogger(__name__)

BlockCoordinates = Tuple[int, int, int]


class BaseSpecification(dict):
    pass


class BaseTranslator:
    def __init__(
        self,
        translation_manager: "TranslationManager",
        parent_version: "Version",
        database: dict,
        mode: str,
    ):
        self._translation_manager = translation_manager
        self._parent_version = parent_version
        self._universal_format = translation_manager.universal_format
        self._database = database
        self._mode = mode

        self._error_cache = set()

    def _format_key(self, force_blockstate):
        return (
            "numerical"
            if not force_blockstate and self._parent_version.has_abstract_format
            else "blockstate"
        )

    def _error_once(self, unique, msg_fmt, *args):
        if unique not in self._error_cache:
            log.error(msg_fmt.format(*args), exc_info=True)
            self._error_cache.add(unique)

    def _warn_once(self, unique, msg_fmt, *args):
        if unique not in self._error_cache:
            log.warning(msg_fmt.format(*args))
            self._error_cache.add(unique)

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
            self._error_once(
                (object_input, str(e)),
                "Error converting {} {} {} in {}.",
                self._mode,
                object_input,
                translation_direction,
                self._parent_version,
            )
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
            .get("specification", {})
            .get(namespace, {})
            .keys()
        )

    @staticmethod
    def _get_data(data):
        if minified:
            return copy.deepcopy(json_atlas[data])
        else:
            return copy.deepcopy(data)

    def _get_raw_specification(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> dict:
        try:
            data = self._database.get(self._format_key(force_blockstate), {}).get(
                "specification", {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(
                f"Specification for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}"
            )

    def get_specification(
        self, namespace: str, base_name: str, force_blockstate: bool = False
    ) -> BaseSpecification:
        """
        Get the specification file for the requested object.

        :param namespace: A namespace string as found using the ``namespaces`` method
        :param base_name: A base name string as found using the ``base_name`` method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same)
        :return: A custom dictionary with a better documented API.
        """
        raise NotImplementedError

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
