from collections.abc import Sized, Iterable, Container, Mapping, Set

class _Node(Sized, Iterable, Container):

	"""A left-leaning red-black BST. This is the 2-3 version.

	This code is adapted to Python from the Java code given in "Left-leaning
	Red-Black Trees", Robert Sedgewick,
	http://www.cs.princeton.edu/~rs/talks/LLRB/LLRB.pdf. See also the code at
	http://algs4.cs.princeton.edu/33balanced/RedBlackBST.java.html."""

	_RED = True
	_BLACK = False

	def __init__(self, key, value):
		try:
			key < key
		except TypeError:
			raise TypeError("{.__name__!r} can't contain unorderable keys of "
							"type {.__name__!r}".format(type(self), type(key)))
		self._key = key
		self._value = value
		self._color = self._RED
		self._left = self._right = None

	def __len__(self):
		l = 0 if self._left is None else len(self._left)
		r = 0 if self._right is None else len(self._right)
		return l + 1 + r

	def __iter__(self):
		if self._left is not None:
			for item in self._left:
				yield item
		yield self._key
		if self._right is not None:
			for item in self._right:
				yield item

	def __contains__(self, key):
		try:
			self.search(key)
		except KeyError:
			return False
		return True

	def search(self, key):
		"""Return value associated with `key`; `None` if `key` not contained."""
		x = self
		while x is not None:
			if key == x._key:
				return x._value
			elif key < x._key:
				x = x._left
			elif key > x._key:
				x = x._right
			else:
				raise TypeError("{.__name__!r} can't contain unorderable keys of "
								"type {.__name__!r}".format(type(self), type(key)))
		raise KeyError(key)

	def insert(self, key, value):
		"""Recursively insert the key-value pair in the subtree rooted at `self`."""
		if key == self._key:
			self._value = value
		elif key < self._key:
			if self._left is None:
				self._left = self.__class__(key, value)
			else:
				self._left = self._left.insert(key, value)
		elif key > self._key:
			if self._right is None:
				self._right = self.__class__(key, value)
			else:
				self._right = self._right.insert(key, value)
		else:
			raise TypeError("{.__name__!r} can't contain unorderable keys of "
							"type {.__name__!r}".format(type(self), type(key)))
		isred = self._isred
		if isred(self._right) and not isred(self._left):
			self = self._rotate_left()
		if isred(self._left) and isred(self._left._left):
			self = self._rotate_right()
		if isred(self._left) and isred(self._right):
			self._flip_colors()
		return self

	#### Red-black helper methods ####

	def _rotate_left(self):
		"""Make a right-leaning link `self` lean to the left."""
		x = self._right
		self._right = x._left
		x._left = self
		x._color = self._color
		self._color = self._RED
		return x

	def _rotate_right(self):
		"""Make a left-leaning link `self` lean to the right."""
		x = self._left
		self._left = x._right
		x._right = self
		x._color = self._color
		self._color = self._RED
		return x

	def _flip_colors(self):
		"""Flip the colors of a node `self` and its two children."""
		self._color = not self._color
		self._left._color = not self._left._color
		self._right._color = not self._right._color

	@classmethod
	def _isred(cls, h):
		"""Return whether node `h` is red; False if `h` is `None`."""
		if h is None:
			return False
		return h._color == cls._RED


class _Null(Sized, Iterable, Container):

	"Drop-in dummy `_Node`"

	def __len__(self): return 0
	def __iter__(self): return iter([])
	def __contains__(self, key): return False
	def search(self, key): raise KeyError(key)
	def insert(self, key, value): return _Node(key, value)


class BinarySearchTree(Sized, Iterable, Container):

	"Abstract binary search tree. This class is only useful for sublcassing."

	def __init__(self):
		"""Instantiate new empty BST."""
		self._root = _Null()

	def __len__(self): return len(self._root)
	def __contains__(self, key): return key in self._root
	def __iter__(self): return iter(self._root)


class OrderedMapping(BinarySearchTree, Mapping):

	"Mapping of totally ordered keys, which need not be hashable."

	def __init__(self, iterable=()):
		"""Instantiate a new OrderedMapping optionally with key-value pairs.

		The optional argument `iterable` has the same semantics as it does for
		the `update` method.
		"""
		super().__init__()
		self.update(iterable)

	def update(self, iterable=()):
		"""Update self with new or replacement values from `iterable`.

		`iterable` is an optional argument  that is either a mapping or is an
		iterable containing two-item iterables: The first item is the key and
		the second the value. The `OrderedMapping` will contain these key-value
		pairs. If keys are repeated, later copies replace earlier ones. The keys
		must be totally ordered but they need not be hashable.
		"""
		if isinstance(iterable, Mapping):
			iterable = iterable.items()
		for item in iterable:
			try:
				k, v = item
			except TypeError:
				raise TypeError('{.__name__!r} must be initialized with mappings'
								' or iterables of pairs.'.format(type(self)))
			self[k] = v

	def __getitem__(self, key): return self._root.search(key)

	def __setitem__(self, key, value):
		self._root = self._root.insert(key, value)
		self._root._color = _Node._BLACK


class OrderedSet(BinarySearchTree, Set):

	"Set of totally ordered values, which need not be hashable."

	def __init__(self, iterable=()):
		"""Instantiate a new OrderedSet, optionally with values.

		`iterable` is an optional argument containing an iterable of values to
		fill up the new `OrderedSet`. If values are repeated (in terms of
		equality but not identity), later values replace earlier ones. The
		values must be totally ordered but they need not be hashable.
		"""
		super().__init__()
		self |= iterable

	def add(self, item):
		"Add an item to the set, replacing older items that are equal."
		self._root = self._root.insert(item, item)
		self._root._color = _Node._BLACK

	def __ior__(self, other):
		"Update self with new and replacement values from other (in-place union)."
		for value in other:
			self.add(value)
		return self

	def find(self, item):
		"If there is an equal item in self, return it. Else raise KeyError."
		return self._root.search(item)
