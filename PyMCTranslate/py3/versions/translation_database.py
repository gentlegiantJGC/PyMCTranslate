from typing import List, Tuple, Union, Callable, Optional, TYPE_CHECKING
import copy
import traceback

from PyMCTranslate import Block, BlockEntity, Entity
from PyMCTranslate.py3.log import info, log_level
from ..versions.translate import translate

if TYPE_CHECKING:
    from ..versions import Version


class BaseTranslator:
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict, mode: str):
        self._parent_version = parent_version
        self._universal_format = universal_format
        self._database = database
        self._mode = mode

        # TODO: implement this
        self._cache = {  # only blocks without a block entity can be cached
            'to_universal': {

            },
            'from_universal': {

            }
        }

    def _format_key(self, force_blockstate: bool = False):
        return 'numerical' if not force_blockstate and self._parent_version.has_abstract_format else 'blockstate'

    @staticmethod
    def _translate(
            object_input: Union[Block, Entity],
            input_spec: dict,
            mappings: List[dict],
            output_version: 'Version',
            translation_direction: str,
            get_block_callback: Callable[[Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]] = None,
            extra_input: BlockEntity = None,
            pre_populate_defaults: bool = True
    ) -> Union[
        Tuple[Block, None, bool, bool],
        Tuple[Block, BlockEntity, bool, bool],
        Tuple[Entity, None, bool, bool]
    ]:
        try:
            output, extra_output, extra_needed, cacheable = translate(
                object_input,
                input_spec,
                mappings,
                output_version,
                get_block_callback,
                extra_input,
                pre_populate_defaults
            )
            return output, extra_output, extra_needed, cacheable
        except Exception as e:
            info(f'Error while converting {object_input} {translation_direction}\n{e}')
            if log_level >= 3:
                traceback.print_stack()
                traceback.print_exc()
            return object_input, None, True, False

    def namespaces(self, force_blockstate: bool = False) -> List[str]:
        """
        A list of all the namespaces.
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: A list of all the namespaces
        """
        return list(
            self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'specification', {}
            ).keys()
        )

    def base_names(self, namespace: str, force_blockstate: bool = False) -> List[str]:
        """
        A list of all the base names present in a given mode and namespace.
        :param namespace: A namespace string as found using the namespaces method
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: A list of base names
        """
        return list(
            self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'specification', {}
            )[namespace].keys()
        )

    def get_specification(self, namespace: str, base_name: str, force_blockstate: bool = False) -> dict:
        """
        Get the specification file for the requested object.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: A dictionary containing the specification for the object
        """
        try:
            return copy.deepcopy(self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'specification', {}
            )[namespace][base_name])
        except KeyError:
            raise KeyError(f'Specification for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist')

    def get_mapping_to_universal(self, namespace: str, base_name: str, force_blockstate: bool = False) -> List[dict]:
        """
        Get the mapping file for the requested object from this version format to the universal format.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: A list of mapping functions to apply to the object
        """
        try:
            return copy.deepcopy(self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'to_universal', {}
            )[namespace][base_name])
        except KeyError:
            raise KeyError(f'Mapping to universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist')

    def get_mapping_from_universal(self, namespace: str, base_name: str, force_blockstate: bool = False) -> List[dict]:
        """
        Get the mapping file for the requested object from the universal format to this version format.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return: A list of mapping functions to apply to the object
        """
        try:
            return copy.deepcopy(self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'from_universal', {}
            )[namespace][base_name])
        except KeyError:
            raise KeyError(f'Mapping from universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist')

    def to_universal(self, object_input, force_blockstate: bool = False):
        """
        A method to translate a given object to the Universal format.
        :param object_input: The object to translate
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return:
        """
        raise NotImplementedError

    def from_universal(self, object_input, force_blockstate: bool = False):
        """
        A method to translate a given object from the Universal format to the format of this class instance.
        :param object_input: The object to translate
        :param force_blockstate: True to return the blockstate sub-version. False to return the native sub-version (these are sometimes the same thing)
        :return:
        """
        raise NotImplementedError


class BlockTranslator(BaseTranslator):
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict):
        super(BlockTranslator, self).__init__(parent_version, universal_format, database, 'block')

    def to_universal(
            self,
            object_input: 'Block',
            get_block_callback: Callable[[Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]] = None,
            extra_input: 'BlockEntity' = None
    ) -> Union[
        Tuple[Block, None, bool],
        Tuple[Block, BlockEntity, bool],
        Tuple[Entity, None, bool]
    ]:
        """
        A method to translate a given Block object to the Universal format.
        :param object_input: The object to translate
        :param get_block_callback: see get_block_at function at the top of _translate for a template
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Block), 'Input object must be a block'
        if extra_input is None:
            if object_input in self._cache['to_universal']:
                return self._cache['to_universal'][object_input]
        else:
            assert isinstance(extra_input, BlockEntity), 'extra_input must be None or a BlockEntity'

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            self.get_specification(object_input.namespace, object_input.base_name),
            self.get_mapping_to_universal(object_input.namespace, object_input.base_name),
            self._universal_format,
            'to universal',
            get_block_callback,
            extra_input
        )

        if cacheable:
            self._cache['to_universal'][object_input] = output, extra_output, extra_needed

        return output, extra_output, extra_needed

    def from_universal(
            self,
            object_input: 'Block',
            get_block_callback: Callable[[Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]] = None,
            extra_input: 'BlockEntity' = None
    ) -> Union[
        Tuple[Block, None, bool],
        Tuple[Block, BlockEntity, bool],
        Tuple[Entity, None, bool]
    ]:
        """
        A method to translate a given Block or Entity object from the Universal format to the format of this class instance.
        :param object_input: The object to translate
        :param get_block_callback: see get_block_at function at the top of _translate for a template
        :param extra_input: secondary to the object_input a block entity can be given. This should only be used in the select block tool or plugins. Not compatible with location
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Block), 'Input object must be a block'
        if extra_input is None:
            if object_input in self._cache['from_universal']:
                return self._cache['from_universal'][object_input]
        else:
            assert isinstance(extra_input, BlockEntity), 'extra_input must be None or a BlockEntity'

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            self._universal_format.block.get_specification(object_input.namespace, object_input.base_name),
            self.get_mapping_from_universal(object_input.namespace, object_input.base_name),
            self._parent_version,
            'from_universal',
            get_block_callback,
            extra_input
        )

        if cacheable:
            self._cache['from_universal'][object_input] = output, extra_output, extra_needed

        return output, extra_output, extra_needed


class EntityTranslator(BaseTranslator):
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict):
        super(EntityTranslator, self).__init__(parent_version, universal_format, database, 'entity')


class ItemTranslator(BaseTranslator):
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict):
        super(ItemTranslator, self).__init__(parent_version, universal_format, database, 'item')
