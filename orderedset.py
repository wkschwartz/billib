class LeftLeaningRedBlackTree:

	"""A symbol table implemented using a left-leaning red-black BST. This is
	the 2-3 version.

	This code is adapted to Python from the Java code given in "Left-leaning
	Red-Black Trees", Robert Sedgewick,
	http://www.cs.princeton.edu/~rs/talks/LLRB/LLRB.pdf. See also the code at
	http://algs4.cs.princeton.edu/33balanced/RedBlackBST.java.html.
	"""

	_RED = True
	_BLACK = False

	class _Node:

		"""BST helper node data type."""

		def __init__(self, key, value):
			self._key = key
			self._value = value
			self._color = LeftLeaningRedBlackTree._RED
			self._left = self._right = None

	def __init__(self):
		"""Instantiate new empty BST."""
		self._root = None

	def search(self, key):
		"""Return value associated with `key`; `None` if `key` not contained."""
		x = self._root
		while x is not None:
			if key == x._key:
				return x._value
			elif key < x._key:
				x = x._left
			elif key > x._key:
				x = x._right
		return None

	def insert(self, key, value):
		"""Insert the key-value pair; overwrite value if key already present."""
		self._root = self._insert(self._root, key, value)
		self._root._color = self._BLACK

	@classmethod
	def _insert(cls, h, key, value):
		"""Recursively insert the key-value pair in the subtree rooted at `h`."""
		if h is None:
			return cls._Node(key, value)
		if key == h._key:
			h._value = value
		elif key < h._key:
			h._left = cls._insert(h._left, key, value)
		else:
			h._right = cls._insert(h._right, key, value)
		isred = cls._isred
		if isred(h._right) and not isred(h._left):
			h = cls._rotate_left(h)
		if isred(h._left) and isred(h._left._left):
			h = cls._rotate_right(h)
		if isred(h._left) and isred(h._right):
			cls._flip_colors(h)
		return h

	@classmethod
	def _rotate_left(cls, h):
		"""Make a right-leaning link `h` lean to the left."""
		x = h._right
		h._right = x._left
		x._left = h
		x._color = h._color
		h._color = cls._RED
		return x

	@classmethod
	def _rotate_right(cls, h):
		"""Make a left-leaning link `h` lean to the right."""
		x = h._left
		h._left = x._right
		x._right = h
		x._color = h._color
		h._color = cls._RED
		return x

	@classmethod
	def _flip_colors(cls, h):
		"""Flip the colors of a node `h` and its two children."""
		h._color = not h._color
		h._left._color = not h._left._color
		h._right._color = not h._right._color

	@classmethod
	def _isred(cls, h):
		"""Return whether node `h` is red; False if `h` is `None`."""
		if h is None:
			return False
		return h._color == cls._RED
