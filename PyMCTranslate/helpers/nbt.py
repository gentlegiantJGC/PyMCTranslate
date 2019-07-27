# a very very minimalistic NBT data storage. Write/use a proper NBT library


class TAG_Value:
	def __init__(self, val):
		self._val = val

	@property
	def val(self):
		return self._val


class TAG_Byte(TAG_Value):
	datatype = 'byte'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Short(TAG_Value):
	datatype = 'short'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Int(TAG_Value):
	datatype = 'int'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Long(TAG_Value):
	datatype = 'long'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Float(TAG_Value):
	datatype = 'float'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Double(TAG_Value):
	datatype = 'double'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_String(TAG_Value):
	datatype = 'string'

	def __init__(self, val):
		TAG_Value.__init__(self, val)


class TAG_Compound(TAG_Value):
	datatype = 'compound'

	def __init__(self, val=None):
		if val is None:
			val = {}
		TAG_Value.__init__(self, val)

	def __contains__(self, item):
		return item in self.val

	def __getitem__(self, item):
		return self.val[item]

	def __len__(self):
		return len(self.val)

	def items(self):
		return self.val.items()


class TAG_List(TAG_Value):
	datatype = 'list'

	def __init__(self, val=None):
		if val is None:
			val = []
		TAG_Value.__init__(self, val)

	def __len__(self):
		return len(self.val)


class TAG_Byte_Array(TAG_Value):
	datatype = 'byte_array'

	def __init__(self, val=None):
		if val is None:
			val = []
		TAG_Value.__init__(self, val)


class TAG_Int_Array(TAG_Value):
	datatype = 'int_array'

	def __init__(self, val=None):
		if val is None:
			val = []
		TAG_Value.__init__(self, val)


class TAG_Long_Array(TAG_Value):
	datatype = 'long_array'

	def __init__(self, val=None):
		if val is None:
			val = []
		TAG_Value.__init__(self, val)


class NBT(TAG_Compound):
	def __init__(self, val=None):
		if val is None:
			val = {}
		TAG_Compound.__init__(self, val)


def from_spec(spec):
	return {
		key: _from_spec(val) for key, val in spec.items()
	}


nbt_map = {
	'byte': TAG_Byte,
	'short': TAG_Short,
	'int': TAG_Int,
	'long': TAG_Long,
	'float': TAG_Float,
	'double': TAG_Double,
	'string': TAG_String
}

nbt_array = {
	'byte_array': TAG_Byte_Array,
	'int_array': TAG_Int_Array,
	'long_array': TAG_Long_Array
}


def _from_spec(spec):
	assert 'type' in spec
	if spec['type'] == 'compound':
		return NBT(
			{
				key: _from_spec(val) for key, val in spec['val'].items()
			}
		)
	elif spec['type'] == 'list':
		return TAG_List(
			[
				_from_spec(val) for val in spec['val'].items()
			]
		)
	elif spec['type'] in nbt_array:
		return nbt_array[spec['type']](spec['val'])
	elif spec['type'] in nbt_map:
		return nbt_map[spec['type']](spec['val'])
	else:
		raise AssertionError
