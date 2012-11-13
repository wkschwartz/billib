from collections.abc import Sized, Iterable, Container

class _Node(Sized, Iterable, Container):

	"""BST helper node data type."""

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


class LeftLeaningRedBlackTree(Sized, Iterable, Container):

	"""A symbol table implemented using a left-leaning red-black BST. This is
	the 2-3 version.

	This code is adapted to Python from the Java code given in "Left-leaning
	Red-Black Trees", Robert Sedgewick,
	http://www.cs.princeton.edu/~rs/talks/LLRB/LLRB.pdf. See also the code at
	http://algs4.cs.princeton.edu/33balanced/RedBlackBST.java.html.
	"""


	def __init__(self):
		"""Instantiate new empty BST."""
		self._root = None

	def __len__(self):
		return 0 if self._root is None else len(self._root)

	def __contains__(self, key):
		if self._root is None:
			return False
		return key in self._root

	def __iter__(self):
		if self._root is None:
			return
		for item in self._root:
			yield item

	def search(self, key):
		"""Return value associated with `key`; `None` if `key` not contained."""
		if self._root is None:
			raise KeyError(key)
		return self._root.search(key)

	def insert(self, key, value):
		"""Insert the key-value pair; overwrite value if key already present."""
		if self._root is None:
			self._root = _Node(key, value)
		else:
			self._root = self._root.insert(key, value)
		self._root._color = _Node._BLACK
