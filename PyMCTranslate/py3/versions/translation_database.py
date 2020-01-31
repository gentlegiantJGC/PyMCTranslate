from typing import List, Tuple, Union, Callable, TYPE_CHECKING
import copy

from PyMCTranslate import Block, BlockEntity, Entity, minified, json_atlas, log
from ..versions.translate import translate

if TYPE_CHECKING:
    from ..versions import Version


class BaseTranslator:
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict, mode: str):
        self._parent_version = parent_version
        self._universal_format = universal_format
        self._database = database
        self._mode = mode

    def _format_key(self, force_blockstate):
        return 'numerical' if not force_blockstate and self._parent_version.has_abstract_format else 'blockstate'

    def _translate(
            self,
            object_input: Union[Block, Entity],
            input_spec: dict,
            mappings: List[dict],
            output_version: 'Version',
            force_blockstate: bool,
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
                force_blockstate,
                get_block_callback,
                extra_input,
                pre_populate_defaults
            )
            return output, extra_output, extra_needed, cacheable
        except Exception as e:
            log.error(f'Error converting {self._mode} {object_input} {translation_direction} in {self._parent_version}.')
            # traceback.print_stack()
            log.error(f'Error and traceback from the above "{e}"', exc_info=True)
            return object_input, extra_input, True, False

    def namespaces(self, force_blockstate: bool = False) -> List[str]:
        """
        A list of all the namespaces.
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
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
        A list of all the base names present in a given namespace.
        :param namespace: A namespace string as found using the namespaces method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: A list of base names
        """
        return list(
            self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'specification', {}
            )[namespace].keys()
        )

    @staticmethod
    def _get_data(data):
        if minified:
            return copy.deepcopy(json_atlas[data])
        else:
            return copy.deepcopy(data)

    def get_specification(self, namespace: str, base_name: str, force_blockstate: bool = False) -> dict:
        """
        Get the specification file for the requested object.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: A dictionary containing the specification for the object
        """
        try:
            data = self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'specification', {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(f'Specification for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}')

    def get_mapping_to_universal(self, namespace: str, base_name: str, force_blockstate: bool = False) -> List[dict]:
        """
        Get the mapping file for the requested object from this version format to the universal format.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: A list of mapping functions to apply to the object
        """
        try:
            data = self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'to_universal', {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(f'Mapping to universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}')

    def get_mapping_from_universal(self, namespace: str, base_name: str, force_blockstate: bool = False) -> List[dict]:
        """
        Get the mapping file for the requested object from the universal format to this version format.
        :param namespace: A namespace string as found using the namespaces method
        :param base_name: A base name string as found using the base_name method
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: A list of mapping functions to apply to the object
        """
        try:
            data = self._database.get(
                self._format_key(force_blockstate), {}
            ).get(
                'from_universal', {}
            )[namespace][base_name]
            return self._get_data(data)
        except KeyError:
            raise KeyError(f'Mapping from universal for {self._mode} {self._format_key(force_blockstate)} {namespace}:{base_name} does not exist in {self._parent_version}')

    def to_universal(self, *args, **kwargs):
        raise NotImplementedError

    def from_universal(self, *args, **kwargs):
        raise NotImplementedError


class BlockTranslator(BaseTranslator):
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict):
        super(BlockTranslator, self).__init__(parent_version, universal_format, database, 'block')
        self._cache = {  # only blocks without a block entity can be cached
            'to_universal': {

            },
            'from_universal': {

            }
        }

    def to_universal(
            self,
            object_input: 'Block',
            get_block_callback: Callable[[Tuple[int, int, int]], Tuple[Block, Union[None, BlockEntity]]] = None,
            force_blockstate: bool = False,
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
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
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

        try:
            input_spec = self.get_specification(object_input.namespace, object_input.base_name, force_blockstate)
            mapping = self.get_mapping_to_universal(object_input.namespace, object_input.base_name, force_blockstate)
        except KeyError:
            log.warning(f'Could not find translation information for {self._mode} {object_input} to universal in {self._parent_version}. If this is not a vanilla block ignore this message')
            return object_input, extra_input, False

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._universal_format,
            True,
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
            force_blockstate: bool = False,
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
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
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

        try:
            input_spec = self._universal_format.block.get_specification(object_input.namespace, object_input.base_name)
            mapping = self.get_mapping_from_universal(object_input.namespace, object_input.base_name, force_blockstate)
        except KeyError:
            if object_input.namespace == 'minecraft' and list(object_input.properties.keys()) == ['block_data']:
                log.debug(f'Probably just a quirk block {object_input} from universal in {self._parent_version}.')
            else:
                log.warning(f'Could not find translation information for {self._mode} {object_input} from universal in {self._parent_version}. If this is not a vanilla block ignore this message')
            return object_input, extra_input, False

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
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

    def to_universal(
            self,
            object_input: 'Entity',
            force_blockstate: bool = False
    ) -> Union[
        Tuple[Block, None],
        Tuple[Block, BlockEntity],
        Tuple[Entity, None]
    ]:
        """
        A method to translate a given Entity object to the Universal format.
        :param object_input: The object to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
        """
        assert isinstance(object_input, Entity), 'Input object must be an entity'

        try:
            input_spec = self.get_specification(object_input.namespace, object_input.base_name, force_blockstate)
            mapping = self.get_mapping_to_universal(object_input.namespace, object_input.base_name, force_blockstate)
        except KeyError:
            log.warning(f'Could not find translation information for {self._mode} {object_input} to universal in {self._parent_version}. If this is not a vanilla entity ignore this message')
            return object_input, None

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._universal_format,
            True,
            'to universal'
        )

        return output, extra_output

    def from_universal(
            self,
            object_input: 'Entity',
            force_blockstate: bool = False
    ) -> Union[
        Tuple[Block, None],
        Tuple[Block, BlockEntity],
        Tuple[Entity, None]
    ]:
        """
        A method to translate a given Entity object from the Universal format to the format of this class instance.
        :param object_input: The object to translate
        :param force_blockstate: True to get the blockstate format. False to get the native format (these are sometimes the same thing)
        :return: output, extra_output, extra_needed
            output - a Block or Entity instance
            extra_output - None or BlockEntity if there is a BlockEntity to return (only if output is Block)
            extra_needed - bool specifying if the location is needed to fully define the output
        """
        assert isinstance(object_input, Entity), 'Input object must be a block'

        try:
            input_spec = self._universal_format.entity.get_specification(object_input.namespace, object_input.base_name)
            mapping = self.get_mapping_from_universal(object_input.namespace, object_input.base_name, force_blockstate)
        except KeyError:
            log.warning(f'Could not find translation information for {self._mode} {object_input} from universal in {self._parent_version}. If this is not a vanilla entity ignore this message')
            return object_input, None

        output, extra_output, extra_needed, cacheable = self._translate(
            object_input,
            input_spec,
            mapping,
            self._parent_version,
            force_blockstate,
            'from_universal'
        )

        return output, extra_output


class ItemTranslator(BaseTranslator):
    def __init__(self, parent_version: 'Version', universal_format: 'Version', database: dict):
        super(ItemTranslator, self).__init__(parent_version, universal_format, database, 'item')
