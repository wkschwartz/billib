"""Ordered symbol table data types.

You may use `OrderedMapping` or `OrderdSet` directly for keys or elements
(respectively) that are totally ordered but not necessarily hashable. These
data types support the mapping and set interfaces respectively. They do not
(currently) support deletion, but they do support insertion.

You may create your own ordered symbol table client interface by subclassing the
`BinarySearchTree` class.

The tests for this code have been run successfully on Python 3.3 and 3.2.
"""


from collections import Mapping as _MappingABC, Set as _SetABC


class _NullNode:

	"Drop-in dummy `_Node`"

	__slots__ = ()

	def __str__(self): return self.__class__.__name__ + "()"
	def __len__(self): return 0
	def __iter__(self, *, lo=None, hi=None): return iter([])
	def __reversed__(self, *, lo=None, hi=None): return iter([])
	def __contains__(self, key): return False
	def min(self): raise ValueError('No min of an empty container.')
	def max(self): raise ValueError('No max of an empty container.')
	def floor(self, key): raise KeyError(key)
	def ceiling(self, key): raise KeyError(key)
	def rank(self, key): return 0
	def index(self, key, start=None, stop=None): raise KeyError(key)
	def select(self, k): raise IndexError('Select index %r out of bounds' % k)
	def height(self): return 0
	def search(self, key): raise KeyError(key)
	def width(self, lo, hi): return 0

	def insert(self, key, value):
		n = _Node(key, value)
		n._color = _Node._BLACK
		return n


class _Node:

	"""A left-leaning red-black BST. This is the 2-3 version.

	You usually will not need this class directly. Instead, subclass the
	`BinarySearchTree` class below. However, subclassing the present class may
	be useful for adding functionality with recursive algorithms. In that case,
	also subclass `_NullNode` to replace its `insert` method and sublcass
	`BinarySearchTree` to repalce its `__init__` method.

	Arbitrary attribute assignment is not allowed because every insertion would
	cause the client to lose direct access to the node he assigned the attribute
	to.

	This code is adapted to Python from the Java code given in "Left-leaning
	Red-Black Trees", Robert Sedgewick,
	http://www.cs.princeton.edu/~rs/talks/LLRB/LLRB.pdf. See also the code at
	http://algs4.cs.princeton.edu/33balanced/RedBlackBST.java.html, some of
	whose comments were cribbed.
	"""

	__slots__ = '_key', '_value', '_color', '_left', '_right', '_N'

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
		self._N = 1
		self._left = self._right = None

	def __str__(self):
		"Return a Lisp-style list of the keys as a string."
		return type(self).__name__ + self._str()

	def _str(self):
		"Helper for __str__."
		l = '' if self._left is None else ' ' + self._left._str()
		r = '' if self._right is None else ' ' + self._right._str()
		return '(' + str(self._key) + l + r + ')'

	def __len__(self):
		return self._N

	def __iter__(self, *, lo=None, hi=None):
		"""Iterate through the keys in order.

		Optionally use keyword arguments `lo` and `hi` to limit iteration to
		keys k such that lo <= k < hi. (The assymetry between the conditionals
		is meant to parallel the semantics of builtins slice() and range().)
		"""
		if (lo is None or lo < self._key) and self._left is not None:
			for item in self._left.__iter__(lo=lo, hi=hi):
				yield item
		if (lo is None and hi is None or lo is None and self._key < hi or
				hi is None and lo <= self._key or lo <= self._key < hi):
			yield self._key
		if (hi is None or hi > self._key) and self._right is not None:
			for item in self._right.__iter__(lo=lo, hi=hi):
				yield item

	def __reversed__(self, *, lo=None, hi=None):
		"""Iterate through the keys in reverse order.

		Optionally use keyword arguments `lo` and `hi` to limit iteration to
		keys k such that lo <= k < hi. (The assymetry between the conditionals
		is meant to parallel the semantics of builtins slice() and range().)
		"""
		if (hi is None or hi > self._key) and self._right is not None:
			for item in self._right.__reversed__(lo=lo, hi=hi):
				yield item
		if (lo is None and hi is None or lo is None and self._key < hi or
				hi is None and lo <= self._key or lo <= self._key < hi):
			yield self._key
		if (lo is None or lo < self._key) and self._left is not None:
			for item in self._left.__reversed__(lo=lo, hi=hi):
				yield item

	def __contains__(self, key):
		try:
			self.search(key)
		except KeyError:
			return False
		return True

	def height(self):
		l = 0 if self._left is None else self._left.height()
		r = 0 if self._right is None else self._right.height()
		return 1 + max(l, r)

	def search(self, key):
		"Return value associated with `key`; Raise `KeyError` if key not found."
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
		"Recursively insert the key-value pair in the subtree rooted at `self`."
		self = self._insert(key, value)
		self._color = self._BLACK
		return self

	def _insert(self, key, value):
		if key == self._key:
			self._value = value
		elif key < self._key:
			if self._left is None:
				self._left = self.__class__(key, value)
			else:
				self._left = self._left._insert(key, value)
		elif key > self._key:
			if self._right is None:
				self._right = self.__class__(key, value)
			else:
				self._right = self._right._insert(key, value)
		else:
			raise TypeError("{.__name__!r} can't contain unorderable keys of "
							"type {.__name__!r}".format(type(self), type(key)))
		return self._fixup()

	def delete(self, key):
		"Delete the corresponding with key."
		self.search(key) # Raise a KeyError if key not in self.
		self = self._delete(key)
		self._color = self._BLACK
		return self

	def _delete(self, key):
		isred = self._isred
		if key < self._key:
			if (not isred(self._left) and self._left is not None and
					not isred(self._left._left)):
				self = self._move_red_left()
			self._left = self._left._delete(key)
		else:
			if isred(self._left):
				self = self._rotate_right()
			if key == self._key and self._right is None:
				self = self._move_red_right()
			if (not isred(self._right) and self._right is not None and
					not isred(self._right._left):
				self = self._move_red_right()
			if key == self._key:
				rightmin = self._right.min()
				self._value = self._right.search(rightmin)
				self._key = rightmin
				self._right = self._right._delmin()
			else:
				self._right = self._right._delete(key)
		return self._fixup()

	def delmin(self):
		"Delete the key-value pair associated with the minimum key."
		self = self._delmin()
		self._color = self._BLACK
		return self

	def _delmin(self):
		if self._left is None: return None
		isred = self._isred
		if (not isred(self._left) and self._left is not None and
			    not isred(self._left._left)):
			self = self._move_red_left()
		self._left = self._left._delmin()
		return self._fixup()

	#### Ordered symbol table methods ####

	def min(self):
		"Return the least key."
		if self._left is None:
			return self._key
		return self._left.min()

	def max(self):
		"Return the greatest key."
		if self._right is None:
			return self._key
		return self._right.max()

	def floor(self, key):
		"Return the largest key <= the given key. Raise a KeyError if none present."
		if key == self._key:
			return self._key
		elif key < self._key:
			if self._left is None:
				raise KeyError(key)
			return self._left.floor(key)
		elif key > self._key:
			if self._right is None:
				return self._key
			try:
				t = self._right.floor(key)
			except KeyError:
				return self._key
			return t
		else:
			raise TypeError('Key %r not in a total order' % key)

	def ceiling(self, key):
		"Return the least key >= the given key. Raise a KeyError if none present."
		if key == self._key:
			return self._key
		elif key > self._key:
			if self._right is None:
				raise KeyError(key)
			return self._right.ceiling(key)
		elif key < self._key:
			if self._left is None:
				return self._key
			try:
				t = self._left.ceiling(key)
			except KeyError:
				return self._key
			return t
		else:
			raise TypeError('Key %r not in a total order' % key)

	def select(self, k):
		"Return the key with rank k. Raise IndexError if k out of bounds."
		if k < 0 or k >= len(self):
			raise IndexError('Requested rank %r out of bounds' % k)
		return self._select(k)._key

	def _select(self, k):
		# Assume: 0 <= k < len(self)
		t = 0 if self._left is None else len(self._left)
		if t > k:
			return self._left._select(k)
		elif t < k:
			return self._right._select(k - t - 1)
		else:
			return self

	def rank(self, key):
		"Return number of keys in the tree that are less than the given key."
		if key < self._key:
			return 0 if self._left is None else self._left.rank(key)
		l = 0 if self._left is None else len(self._left)
		if key > self._key:
			r = 0 if self._right is None else self._right.rank(key)
			return 1 + l + r
		elif key == self._key:
			return l
		else: raise TypeError("Key %r not in total order with tree's keys, such"
							  " as %r." % (key, self._key))

	def index(self, key, start=None, stop=None):
		"""Index i of key in self, optionally such that start <= i < stop.

		This is essentially the rank method with the same semantics as
		`list.index`. if `key` is not present, a `KeyError` is raised.
		"""
		if key not in self:
			raise KeyError(key)
		r = self.rank(key)
		if start is not None and start > r or stop is not None and r >= stop:
			raise KeyError(key)
		return r

	def width(self, lo, hi):
		"The number of keys k such that lo <= k < hi."
		if lo > hi:
			lo, hi = hi, lo
		return self.rank(hi) - self.rank(lo)

	#### Red-black helper methods ####

	def _move_red_left(self):
		"""Move a child's red link to the left of self.

		If self is red and self._left self._left._left are black, make
		self._left or one of its children red.
		"""
		self._flip_colors()
		if self._right is not None and self._isred(self._right._left):
			self._right = self._right._rotate_right()
			self = self._rotate_left()
			self._flip_colors()
		return self

	def _move_red_right(self):
		"""Move a child's red link to the right of self.

		If self is red and both self._right and self._right._left are
		black, make h._right or one of its children red.
		"""
		self._flip_colors()
		if self._left is not None and self._isred(self._left._left):
			self = self._rotate_right()
			self._flip_colors()
		return self

	def _fixup(self):
		"Shared code for enforcing the LLRB Tree invariants on the way up the tree."
		isred = self._isred
		if isred(self._right) and not isred(self._left):
			self = self._rotate_left()
		if isred(self._left) and isred(self._left._left):
			self = self._rotate_right()
		if isred(self._left) and isred(self._right):
			self._flip_colors()
		self._N = self._recursive_len()
		return self

	def _rotate_left(self):
		"""Make a right-leaning link `self` lean to the left."""
		# Assume: self._right._color == self._RED
		x = self._right
		self._right = x._left
		x._left = self
		x._color = self._color
		self._color = self._RED
		x._N = self._N
		self._N = self._recursive_len()
		return x

	def _rotate_right(self):
		"""Make a left-leaning link `self` lean to the right."""
		# Assume: self._left._color == self._RED
		x = self._left
		self._left = x._right
		x._right = self
		x._color = self._color
		self._color = self._RED
		x._N = self._N
		self._N = self._recursive_len()
		return x

	def _flip_colors(self):
		"""Flip the colors of a node `self` and its two children."""
		# Assume: self._color != self._left._color == self._right._color
		self._color = not self._color
		self._left._color = not self._left._color
		self._right._color = not self._right._color

	def _recursive_len(self):
		"Recursively calculate what the length attribute `N` should be."
		l = 0 if self._left is None else self._left._N
		r = 0 if self._right is None else self._right._N
		return l + 1 + r

	@classmethod
	def _isred(cls, h):
		"""Return whether node `h` is red; False if `h` is `None`."""
		if h is None:
			return False
		return h._color == cls._RED


class BinarySearchTree:

	"Abstract binary search tree. Subclass this class to add a client interface."

	def __init__(self):
		"""Instantiate new empty BST."""
		self._root = _NullNode()

	def clear(self):
		"Remove every element from the tree in constant time."
		self.__init__()

	def __len__(self): return len(self._root)
	def __contains__(self, key): return key in self._root

	def __iter__(self, *, lo=None, hi=None):
		"""Iterate through the keys in order.

		Optionally use keyword arguments `lo` and `hi` to limit iteration to
		keys k such that lo <= k < hi. (The assymetry between the conditionals
		is meant to parallel the semantics of builtins slice() and range().)
		"""
		return self._root.__iter__(lo=lo, hi=hi)

	def __reversed__(self, *, lo=None, hi=None):
		"""Iterate through the keys in reverse order.

		Optionally use keyword arguments `lo` and `hi` to limit iteration to
		keys k such that lo <= k < hi. (The assymetry between the conditionals
		is meant to parallel the semantics of builtins slice() and range().)
		"""
		return self._root.__reversed__(lo=lo, hi=hi)

	def insert(self, key, value):
		"Insert the key-value pair, replacing if key already present."
		self._root = self._root.insert(key, value)
	
	def __getattr__(self, name):
		"Provide transparent access to the methods of the root of the tree."
		if not name.startswith('_'):
			return getattr(self._root, name)
		else:
			raise AttributeError(name)

	def __dir__(self):
		"List the public attributes of the root of the tree too."
		root_attrs = [n for n in dir(self._root) if not n.startswith('_')]
		return list(set(super().__dir__() + root_attrs))

	def range(self, *args):
		"Return iterator over keys with arguments like builtin.range()."
		s = slice(*args)
		if s.step is None or s.step == 1:
			return self._root.__iter__(lo=s.start, hi=s.stop)
		elif s.step == -1:
			return self._root.__reversed__(lo=s.stop, hi=s.start)
		else:
			raise ValueError('{.__name__!s} objects only support range steps of '
							 '1 and -1, not {!r}'.format(type(self), s.step))


class OrderedMapping(BinarySearchTree, _MappingABC):

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

		`iterable` is an optional argument that is either a mapping or is an
		iterable containing two-item iterables: The first item is the key and
		the second the value. The `OrderedMapping` will contain these key-value
		pairs. If keys are repeated, later copies replace earlier ones. The keys
		must be totally ordered but they need not be hashable.
		"""
		if isinstance(iterable, _MappingABC):
			iterable = iterable.items()
		for item in iterable:
			try:
				k, v = item
			except TypeError:
				raise TypeError('{.__name__!r} must be initialized with mappings'
								' or iterables of pairs.'.format(type(self)))
			self[k] = v

	def __getitem__(self, key): return self.search(key)

	def __setitem__(self, key, value):
		self.insert(key, value)


class OrderedSet(BinarySearchTree, _SetABC):

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
		self.insert(item, item)

	def __ior__(self, other):
		"Update self with new and replacement values from other (in-place union)."
		for value in other:
			self.add(value)
		return self
