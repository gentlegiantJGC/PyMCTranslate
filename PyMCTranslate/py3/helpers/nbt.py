def from_spec(spec):
	return {
		key: _from_spec(val) for key, val in spec.items()
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
