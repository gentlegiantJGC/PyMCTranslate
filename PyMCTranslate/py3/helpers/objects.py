from typing import Tuple
from PyMCTranslate.py3.helpers.nbt import NBT


class Entity:
	def __init__(self, namespace: str, base_name: str, location: Tuple[float, float, float], nbt: NBT):
		self._namespace = namespace
		self._base_name = base_name
		assert all(isinstance(coord, float) for coord in location), 'Location must be a tuple of floats'
		self._x, self._y, self._z = location
		self._nbt = nbt

	@property
	def namespace(self):
		return self._namespace

	@namespace.setter
	def namespace(self, namespace):
		assert isinstance(namespace, str), 'Expected namespace to be a string'
		self._namespace = namespace

	@property
	def base_name(self):
		return self._base_name

	@base_name.setter
	def base_name(self, base_name):
		assert isinstance(base_name, str), 'Expected base_name to be a string'
		self._base_name = base_name

	@property
	def nbt(self):
		return self._nbt

	@nbt.setter
	def nbt(self, nbt):
		self._nbt = nbt

	@property
	def x(self) -> float:
		return self._x

	@x.setter
	def x(self, x: float):
		assert isinstance(x, float), 'The coordinate value must be a float value'

	@property
	def y(self) -> float:
		return self._y

	@y.setter
	def y(self, y: float):
		assert isinstance(y, float), 'The coordinate value must be a float value'

	@property
	def z(self) -> float:
		return self._z

	@z.setter
	def z(self, z: float):
		assert isinstance(z, float), 'The coordinate value must be a float value'


class BlockEntity:
	def __init__(self, namespace: str, base_name: str, location: Tuple[int, int, int], nbt: NBT):
		self._namespace = namespace
		self._base_name = base_name
		assert all(isinstance(coord, int) for coord in location), 'Location must be a tuple of ints'
		self._x, self._y, self._z = location
		self._nbt = nbt

	@property
	def namespace(self):
		return self._namespace

	@namespace.setter
	def namespace(self, namespace):
		assert isinstance(namespace, str), 'Expected namespace to be a string'
		self._namespace = namespace

	@property
	def base_name(self):
		return self._base_name

	@base_name.setter
	def base_name(self, base_name):
		assert isinstance(base_name, str), 'Expected base_name to be a string'
		self._base_name = base_name

	@property
	def nbt(self):
		return self._nbt

	@nbt.setter
	def nbt(self, nbt):
		self._nbt = nbt

	@property
	def x(self) -> int:
		return self._x

	@x.setter
	def x(self, x: int):
		assert isinstance(x, int), 'The coordinate value must be an integer value'

	@property
	def y(self) -> int:
		return self._y

	@y.setter
	def y(self, y: int):
		assert isinstance(y, int), 'The coordinate value must be an integer value'

	@property
	def z(self) -> int:
		return self._z

	@z.setter
	def z(self, z: int):
		assert isinstance(z, int), 'The coordinate value must be an integer value'
